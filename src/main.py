#!/usr/bin/env python
# encoding=utf8

import androguard.misc
import androguard.core
from tabulate import tabulate
from datetime import datetime
import sys
import os
import urllib2
import hashlib
import cPickle
import csv
import time
import argparse
import multiprocessing
sys.path.append("LiteRadar")  
from literadar import LibRadarLite

reload(sys)
sys.setdefaultencoding('utf8')

VERSION_ANDROGUARD = "0.0.5"  # useful for caching androguard
VERSION_LIBRADAR = "0.0.5"  # useful for caching libradar


parser = argparse.ArgumentParser(
    description='This script runs the comparisons on a given dataset')

parser.add_argument("--empty", default=5,
                    help="Rate between 0 and 100 that represents J.I. to assign to equal empty strings and sets", type=int)
parser.add_argument("--pair",
                    help="Run comparisons only for the provided index of the pair in the dataset", type=int)
parser.add_argument("--processes", default=8,
                    help="Number of processes to use for multiprocessing, defaults to 8", type=int)
parser.add_argument("--nocache", default=False,
                    help="If given to any true value, comparisons will be recomputed ignoring the cache (if any)", type=bool)
parser.add_argument("--output", default=datetime.now().strftime("%Y-%m-%d-%H:%M"),
                    help="Suffix of the reports, defaults to the current datetime", type=str)
parser.add_argument("--dataset", default='data/groundtruth.txt',
                    help="Path to the dataset to analyze", type=str)

args = parser.parse_args()

N_PROCESSES = args.processes
THRESHOLD = 80
JI_OF_EMPTY_SETS = args.empty
DIFF_LIMIT = 5000
execution_time = args.output

apks_dir = "data/apks"
if not os.path.exists("cache"):
    os.makedirs("cache")
if not os.path.exists(apks_dir):
    os.makedirs(apks_dir)
apks_list = os.listdir(apks_dir)


class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("./report/report-FULL-E%s-%s.txt" %
                        (JI_OF_EMPTY_SETS, execution_time), 'w')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass


class Object:
    def __init__(self, **attributes):
        self.__dict__.update(attributes)


summary_report = open('./report/report-SUMMARY-E%s-%s.txt' %
                      (JI_OF_EMPTY_SETS, execution_time), 'w')
sys.stdout = Logger()
# chalk wrapper to print html tags
chalk_html = Object(
    blue=lambda x: "<span style='color: blue'>%s</span>" % x,
    green=lambda x: "<span style='color: green'>%s</span>" % x,
    red=lambda x: "<span style='color: red'>%s</span>" % x,
    bold=lambda x: "<b>%s</b>" % x)


def identity(x): return x


chalk_file = Object(
    blue=identity,
    green=identity,
    red=identity,
    bold=identity)
chalk = chalk_file


def to_detailed_dict(detailed, not_detailed=None, score=0):
    # type: (str, str, float) -> dict
    return {"detailed": detailed, "not_detailed": not_detailed if not_detailed != None else detailed, "score": score}


def jaccard_similarity_lists(list1, list2):
    if len(list1) == 0 and len(list2) == 0:
        return JI_OF_EMPTY_SETS
    s1 = set(list1)
    s2 = set(list2)
    if s1 == s2:
        return 100
    union_len = len(s1.union(s2))
    inter_len = len(s1.intersection(s2))
    # print "%f %f" % (len(s1.intersection(s2)), len(s1.union(s2)))
    return round((float(inter_len) / union_len) * 100, 2) if union_len > 0 else 0.0


def jaccard_similarity_strings(s1, s2):
    if s1 == s2 == None or len(str(s1)) == 0 and len(str(s2)) == 0:
        return JI_OF_EMPTY_SETS
    return 0 if s1 != s2 else 100


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def chuncked_table(header, rows):
    LIMIT_COLUMNS = 100
    LIMIT_TOTAL_ROWS = 500
    rows = rows[:LIMIT_TOTAL_ROWS]
    # generating columns
    header = [header for i in range(
        (len(rows) / LIMIT_COLUMNS) + (1 if len(rows) % LIMIT_COLUMNS != 0 else 0))]
    header = header[:1]
    # print "headers " + str(header) + " rows" + str(list(chunks(rows,  len(header))))
    # tabulate(rows, header)
    return tabulate(chunks([unicode(x) for x in rows], len(header)), header) if len(rows) > 0 else "[]"


def compare_lists(l1, l2):
    difference1 = set(l1).difference(l2)
    difference2 = set(l2).difference(l1)

    cardinalities = u"|l1|=%s,|l2|=%s, diff: -%s +%s, |l1 \u2229 l2|=%s" % (len(
        l1), len(l2), len(difference1), len(difference2), len(set(l1).intersection(set(l2))))

    def result(print_difference):
        if len(difference1) == 0 and len(difference2) == 0:
            return ("EQUAL (%s%%) " % jaccard_similarity_lists(l1, l2)) + (cardinalities if print_difference else "")

        if print_difference:
            return ('CHANGED (%s%%) ' % jaccard_similarity_lists(l1, l2)) + cardinalities + u'\nDELETED %s\n---\nADDED %s' % (str(difference1)[:DIFF_LIMIT],
                                                                                                                              str(difference2)[:DIFF_LIMIT])  # chuncked_table("ADDED", list(difference2)))
        else:
            return 'CHANGED (%s%%)' % jaccard_similarity_lists(l1, l2)

    return to_detailed_dict(result(True), result(False), jaccard_similarity_lists(l1,
                                                                                  l2))  # {"detailed": result(True), "not_detailed": result(False)}


def compare_strings(s1, s2):
    similarity = jaccard_similarity_strings(s1, s2)

    def result(print_difference):
        if s1 != s2:
            difference = ('DIFFERENT: %s!=%s' %
                          (str(s1), str(s2))) if print_difference else ""

            return 'CHANGED (%s%%) %s' % (similarity, difference)
        else:
            return "EQUAL(%s%%) %s" % (str(similarity), s1 if print_difference else "")

    return to_detailed_dict(result(True), result(False), similarity)


def represent_methods(dx, restrict_classes=None, exclude_package=None, only_internal=True):
    return map(
        lambda internal_method: "%s->%s%s" % (internal_method.get_method().class_name, internal_method.get_method(
        ).get_name(), internal_method.get_method(
        ).get_descriptor()),

        filter(lambda mth: (restrict_classes == None or mth.get_method().class_name in restrict_classes) and (
            exclude_package == None or all(not (str(lib) in str(mth)) for lib in exclude_package)),
            filter(lambda method: (method.is_external() and not only_internal) or (
                   not method.is_external() and only_internal), dx.get_methods())))


def compare_classes(dx1, dx2, excluded_libraries):
    cls1 = filter(lambda c: excluded_libraries == None or all(not (str(lib) in str(
        c)) for lib in excluded_libraries), [str(cls) for cls in dx1.classes])
    cls2 = filter(lambda c: excluded_libraries == None or all(not (str(lib) in str(
        c)) for lib in excluded_libraries), [str(cls) for cls in dx1.classes])
    return compare_lists(cls1, cls2)


def compare_methods_common_classes(dx1, dx2, excluded_libraries=None, only_internal=True):
    # type: (any, any) -> dict
    union_classes = set(dx1.classes).intersection(set(dx2.classes))
    meths_dx1 = represent_methods(
        dx1, union_classes, excluded_libraries, only_internal)
    meths_dx2 = represent_methods(
        dx2, union_classes, excluded_libraries, only_internal)

    return compare_lists(meths_dx1, meths_dx2)


def compare_methods(dx1, dx2, excluded_libraries=None, only_internals=True):
    # type: (androguard.misc.Analysis, androguard.misc.Analysis) -> dict
    meths_dx1 = represent_methods(
        dx1, None, excluded_libraries, only_internals)
    meths_dx2 = represent_methods(
        dx2, None, excluded_libraries, only_internals)

    return compare_lists(meths_dx1, meths_dx2)


def compare_fields(dx1, dx2, excluded_libraries):
    # type: (any, any) -> dict
    fields_dx1 = filter(lambda f: excluded_libraries == None or all(not (str(lib) in str(
        f)) for lib in excluded_libraries), [str(field) for field in dx1.get_fields()])
    fields_dx2 = filter(lambda f: excluded_libraries == None or all(not (str(lib) in str(
        f)) for lib in excluded_libraries), [str(field) for field in dx2.get_fields()])
    return compare_lists(fields_dx1, fields_dx2)


def compare_activities(a1, a2, excluded_libraries):
    act1 = filter(lambda f: excluded_libraries == None or all(not (str(lib).replace(
        '/', '.')[1:] in str(f)) for lib in excluded_libraries), a1.get_activities())
    act2 = filter(lambda f: excluded_libraries == None or all(not (str(lib).replace(
        '/', '.')[1:] in str(f)) for lib in excluded_libraries), a2.get_activities())
    return compare_lists(act1, act2)


def compare_services(a1, a2, excluded_libraries):
    act1 = filter(lambda f: excluded_libraries == None or all(not (str(lib).replace(
        '/', '.')[1:] in str(f)) for lib in excluded_libraries), a1.get_services())
    act2 = filter(lambda f: excluded_libraries == None or all(not (str(lib).replace(
        '/', '.')[1:] in str(f)) for lib in excluded_libraries), a2.get_services())
    return compare_lists(act1, act2)


def compare_receivers(a1, a2, excluded_libraries):
    act1 = filter(lambda f: excluded_libraries == None or all(not (str(lib).replace(
        '/', '.')[1:] in str(f)) for lib in excluded_libraries), a1.get_receivers())
    act2 = filter(lambda f: excluded_libraries == None or all(not (str(lib).replace(
        '/', '.')[1:] in str(f)) for lib in excluded_libraries), a2.get_receivers())
    return compare_lists(act1, act2)


def compare_resources(a1, a2, excluded_libraries):
    act1 = filter(
        lambda f: excluded_libraries == None or all(
            not (str(lib)[1:] in str(f)) for lib in excluded_libraries),
        a1.get_files())
    act2 = filter(
        lambda f: excluded_libraries == None or all(
            not (str(lib)[1:] in str(f)) for lib in excluded_libraries),
        a2.get_files())
    return compare_lists(act1, act2)


analysis_header = ['Ref.',
                   'package',
                   'AppName',
                   'And. vcode',
                   'And. vname',
                   'MinSDK',
                   'MaxSDK',
                   'TargetSDK',
                   'Eff.TargetSDK',
                   'Permissions',
                   'Activities',
                   'Resources',
                   'Services',
                   'Receivers',
                   'Classes',
                   'Methods Int. Classes',
                   'Methods Int. Common Classes',
                   'Methods Ext. Classes',
                   'Methods Ext. Common Classes',
                   'Strings',
                   'Fields',
                   'GRND TRUTH']
ground_truth_header = ['Ref.',
                       'Ground Truth',
                       'Score',
                       'Tool Result',
                       'Tool Conclusion']


def download_if_not_exists(hash):
    global apks_dir, apks_list
    if (hash + ".apk" in apks_list):
        with open(apks_dir + "/" + hash + ".apk", "rb") as existing_apk:
            hash_in_file = hashlib.sha256(
                existing_apk.read()).hexdigest().upper()
        if hash_in_file != hash:
            print "\n File exists but no equal hashes: %s, %s" % (
                hash, hash_in_file)
        else:
            return

    print "Apk not downloaded, downloading now...\n"
    with open(apks_dir + "/" + hash + ".apk", "wb") as fapk:
        fapk.write(urllib2.urlopen(
            "https://androzoo.uni.lu/api/download?apikey=a52054307648be3c6b753eb55c093f4c2fa4b03e452f8ed245db653fee146cdd&sha256=%s" % hash).read())
        print "Download completed\n"


def libradar_and_cache(apk_hash):
    filename = "libradar-"+hashlib.sha256(
        bytes(apk_hash + VERSION_LIBRADAR)).hexdigest().upper()
    if os.path.exists("./cache/" + filename):
        print "CACHED(libradar) getting results... %s" % apk_hash
        with open("./cache/" + filename, "rb") as file:
            res = cPickle.load(file)
    else:
        lrd = LibRadarLite("./data/apks/%s.apk" % apk_hash)
        res = [lib["Package"] for lib in lrd.compare()]

        print "CACHING (libradar)... %s" % apk_hash
        with open("./cache/" + filename, "wb") as file:
            cPickle.dump(res, file)
    return res


def compare_ground_truth(groundtruth_lines, current_process, analysis_rows, ground_truth_rows, skipped_lines, locks):
    global args

    for num, line in enumerate(groundtruth_lines):
        if args.pair != None and num != args.pair:
            continue

        if num % N_PROCESSES != current_process:
            continue

        # Check if another process is using the same files
        prints = str()
        print "Process n°%s" % current_process

        [original_apk_hash, repackaged_apk_hash,
         grnd_is_similar] = line.strip().split(',')
        prints += chalk.bold(
            "\n\n###(%s)###  ########################### Analyzing pair of dataset: [%s,%s] ####################################") % (
            num, chalk.blue(chalk.bold(original_apk_hash)), chalk.bold(repackaged_apk_hash))

        # print "locks %s" % str(locks)
        while original_apk_hash in locks or repackaged_apk_hash in locks:
            print "Process %s: Another process is running the same file, waiting..." % current_process
            time.sleep(3)
        locks.append(original_apk_hash)
        locks.append(repackaged_apk_hash)

        download_if_not_exists(original_apk_hash)
        download_if_not_exists(repackaged_apk_hash)

        cache_filename = "androguard-" + hashlib.sha256(
            bytes(original_apk_hash + repackaged_apk_hash + VERSION_ANDROGUARD + str(JI_OF_EMPTY_SETS))).hexdigest().upper()

        pair_processed = False
        for tries in range(3):
            try:
                # running libradar
                res_libradar_a1 = libradar_and_cache(original_apk_hash)
                res_libradar_a2 = libradar_and_cache(repackaged_apk_hash)

                external_libraries = set(
                    res_libradar_a1).union(res_libradar_a2)

                # running androguard
                if os.path.exists("./cache/" + cache_filename) and not args.nocache:
                    prints += "CACHED(androguard) getting results...."
                    with open("./cache/" + cache_filename, "rb") as file:
                        comparisons = cPickle.load(file)
                else:
                    prints += "Running comparisons"
                    a1, d1, dx1 = androguard.misc.AnalyzeAPK(
                        "./data/apks/%s.apk" % original_apk_hash)
                    a2, d2, dx2 = androguard.misc.AnalyzeAPK(
                        "./data/apks/%s.apk" % repackaged_apk_hash)

                    # COMPARISONS
                    comparisons = [
                        compare_strings(
                            a1.get_package(), a2.get_package()),
                        compare_strings(
                            a1.get_app_name(), a2.get_app_name()),
                        compare_strings(
                            a1.get_androidversion_code(), a2.get_androidversion_code()),
                        compare_strings(
                            a1.get_androidversion_name(), a2.get_androidversion_name()),
                        compare_strings(
                            a1.get_min_sdk_version(), a2.get_min_sdk_version()),
                        compare_strings(
                            a1.get_max_sdk_version(), a2.get_max_sdk_version()),
                        compare_strings(
                            a1.get_target_sdk_version(), a2.get_target_sdk_version()),
                        compare_strings(
                            a1.get_effective_target_sdk_version(), a2.get_effective_target_sdk_version()),
                        compare_lists(
                            a1.get_permissions(), a2.get_permissions()),
                        compare_activities(
                            a1, a2, external_libraries),
                        compare_lists(
                            a1.get_files(), a2.get_files()),
                        compare_services(
                            a1, a2, external_libraries),
                        compare_receivers(
                            a1, a2, external_libraries),
                        compare_classes(
                            dx1, dx2, external_libraries),
                        compare_methods(dx1, dx2, external_libraries),
                        compare_methods_common_classes(
                            dx1, dx2, external_libraries),
                        compare_methods(dx1, dx2, external_libraries, False),
                        compare_methods_common_classes(
                            dx1, dx2, external_libraries, False),
                        compare_lists(dx1.strings, dx2.strings),
                        compare_fields(dx1, dx2, external_libraries)
                    ]
                    prints += "CACHING(androguard)...."
                    with open("./cache/" + cache_filename, "wb") as file:
                        cPickle.dump(comparisons, file)

                pair_processed = True
                break
            except Exception as ex:
                prints += "Androguard/LibRadar failed to analyze this pair, excluding it.."
                print ex
                pair_processed = False
                time.sleep(3)

        if not pair_processed:
            skipped_lines.append(str((num, line)))
            continue

        if original_apk_hash in locks:
            locks.remove(original_apk_hash)
        if repackaged_apk_hash in locks:
            locks.remove(repackaged_apk_hash)

        prints += '\n=================LIBS Apk1 and apk2=============================\n'
        prints += "APK1: %s\nAPK2: %s" % (res_libradar_a1, res_libradar_a2)

        for i, comparison in enumerate(comparisons):
            prints += '\n==============================================\n'
            prints += '%s: \n-----------\n  %s' % (analysis_header[i +
                                                                   1], comparison['detailed'])

        prints += "\n\n=============== CURRENT ANALYSIS =============== \n\n"

        analysis_rows.append(
            [str(num)] +
            map(lambda comparison: comparison['not_detailed'], comparisons) +
            [grnd_is_similar])

        prints += tabulate(analysis_rows,
                           headers=analysis_header, tablefmt="grid") + "\n"

        avg_score = sum(
            map(lambda x: x['score'], comparisons)) / len(comparisons)

        tool_result = "SIMILAR" if avg_score >= THRESHOLD else "NOT_SIMILAR"
        ground_truth_rows.append([chalk.blue(chalk.bold("%s" % num)),
                                  grnd_is_similar,
                                  avg_score,
                                  chalk.bold(chalk.red(
                                      tool_result) if tool_result != grnd_is_similar else chalk.green(
                                      tool_result)),
                                  chalk.bold(chalk.red(
                                      "WRONG") if tool_result != grnd_is_similar else chalk.green(
                                      "RIGHT"))])

        prints += tabulate(ground_truth_rows,
                           headers=ground_truth_header, tablefmt="grid") + "\n"

        print prints
        # setting threshold to recommended
        # if recommended_threshold != "ND":
        #     THRESHOLD = recommended_threshold


def concurrent_process(lines, analysis_rows, ground_truth_rows, skipped_lines, locks):
    processes = list()
    for i in range(N_PROCESSES):
        x = multiprocessing.Process(target=compare_ground_truth, args=[
                                    lines, i, analysis_rows, ground_truth_rows, skipped_lines, locks])
        processes.append(x)
        x.start()

    for index, process in enumerate(processes):
        process.join()


if __name__ == '__main__':
    with open(args.dataset) as f:
        file_lines = f.readlines()

    manager = multiprocessing.Manager()
    analysis_rows, ground_truth_rows, skipped_lines = manager.list(
    ), manager.list(), manager.list()
    locks = manager.list()

    concurrent_process(file_lines, analysis_rows,
                       ground_truth_rows, skipped_lines, locks)

    # average between min of similar and max of non similar
    similar_rows = filter(
        lambda row: row[1] == "SIMILAR", ground_truth_rows)
    not_similar_rows = filter(
        lambda row: row[1] == "NOT_SIMILAR", ground_truth_rows)
    recommended_threshold = round(float(
        min(map(lambda row: row[2], similar_rows))
        +
        max(map(lambda row: row[2], not_similar_rows))
    ) / 2, 2) if len(similar_rows) > 0 and len(not_similar_rows) > 0 else "ND"

    TP = len(filter(lambda row: row[4] == "RIGHT", similar_rows))
    TN = len(filter(lambda row: row[4] == "RIGHT", not_similar_rows))
    FP = len(filter(lambda row: row[4] == "WRONG", not_similar_rows))
    FN = len(filter(lambda row: row[4] == "WRONG", similar_rows))

    max_non_similar = max(map(lambda row: (row[0], row[2]), not_similar_rows), key=lambda x: x[1]) if len(
        not_similar_rows) > 0 else "ND"
    min_similar = min(map(lambda row: (row[0], row[2]), similar_rows), key=lambda x: x[1]) if len(
        similar_rows) > 0 else "ND"

    summary_threshold = "\n======= CURRENT THRESHOLD %s%% ======= F1 SCORE: %s%% ======= RECOMMENDED THRESHOLD %s%%  == MAX_NON_SIM(id %s): %s%% MIN_SIM(id %s). %s%% \n" % (
        chalk.blue(THRESHOLD),
        round((float(2 * TP) / (2 * TP + FN + FP)) *
              100, 2) if 2 * TP + FN + FP > 0 else "ND",
        chalk.bold(recommended_threshold),
        max_non_similar[0],
        max_non_similar[1],
        min_similar[0],
        min_similar[1]
    )
    analysis_table = tabulate([
        ["TOOL_SIMILAR", "TP(%s)" % TP, "FP(%s)" % FP],
        ["TOOL_NOT_SIMILAR", "FN(%s)" % FN, "TN(%s)" % TN]
    ], ["", "GND_SIMILAR", "GND_NOT_SIMILAR"], tablefmt="grid")

    summary_report.write("\nFINAL ANALYSIS TABLE: \n")
    summary_report.write(
        tabulate(analysis_rows, headers=analysis_header, tablefmt="grid"))
    summary_report.write("\n" +
                         tabulate(ground_truth_rows, headers=ground_truth_header, tablefmt="grid"))
    summary_report.write("\n"+analysis_table + "\n"+summary_threshold)
    summary_report.write(
        "\n\nExcluded pairs because of androguard exceptions\n%s" % "\n".join((skipped_lines)))
    summary_report.close()
    with open(summary_report.name + '(a).csv', 'wb') as csv_file:
        wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        wr.writerow(analysis_header)
        wr.writerows(analysis_rows)
    with open(summary_report.name + '(b).csv', 'wb') as csv_file:
        wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        wr.writerow(ground_truth_header)
        wr.writerows(ground_truth_rows)
    print "Summary file saved in: %s" % summary_report.name
