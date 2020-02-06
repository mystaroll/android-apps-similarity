#!/usr/bin/env python
# encoding=utf8

import androguard.misc
import androguard.core
import cPickle as pickle
from tabulate import tabulate
from datetime import datetime
import sys

reload(sys)
sys.setdefaultencoding('utf8')
THRESHOLD = 57
DIFF_CHAR_LIMIT = 1000
execution_time = datetime.now().strftime("%Y-%m-%d-%H:%M")


# print 'Checking existing session'
# SESSION_FILENAME = 'session.ag'
# s = androguard.session.Load(SESSION_FILENAME) if os.path.exists(
#     SESSION_FILENAME) else androguard.session.Session()

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("./report/report-FULL-%s.txt" % execution_time, 'w')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass


class Object:
    def __init__(self, **attributes):
        self.__dict__.update(attributes)


summary_report = open('./report/report-SUMMARY-%s.txt' % execution_time, 'w')
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
    s1 = set(list1)
    s2 = set(list2)
    if s1 == s2:
        return 100
    union_len = len(s1.union(s2))
    inter_len = len(s1.intersection(s2))
    # print "%f %f" % (len(s1.intersection(s2)), len(s1.union(s2)))
    return round((float(inter_len) / union_len) * 100, 2) if union_len > 0 else 0.0


def represent_methods(dx, restrict_classes=None, only_internal=True):
    return map(
        lambda internal_method: "%s->%s%s" % (internal_method.get_method().class_name, internal_method.get_method(
        ).get_name(), internal_method.get_method(
        ).get_descriptor()),
        filter(lambda mth: restrict_classes == None or mth.get_method().class_name in restrict_classes,
               filter(lambda method: (not method.is_external()) or (not only_internal), dx.get_methods())))


# def jaccard_similarity_strings(str1, str2):
#     str1 = set(str1.split())
#     str2 = set(str2.split())
#     return float(len(str1 & str2)) / len(str1 | str2)


def compare_lists(l1, l2):
    difference1 = set(l1).difference(l2)
    difference2 = set(l2).difference(l1)

    def result(print_difference): return chalk.bold('%s') % (chalk.red('\nDELETED %s\n---\nADDED %s' % (
        str(difference1), str(difference2)) if print_difference else 'CHANGED (JI %s%%)' % jaccard_similarity_lists(l1,
                                                                                                                    l2)) if len(
        difference1) != 0 or len(
        difference2) != 0 else chalk.green(
        "EQUAL (JI %s%%)" % jaccard_similarity_lists(l1, l2)))  # type: Callable[[bool], str]

    return to_detailed_dict(result(True), result(False), jaccard_similarity_lists(l1,
                                                                                  l2))  # {"detailed": result(True), "not_detailed": result(False)}


def compare_strings(s1, s2):
    # type: (str, str) -> dict
    def result(print_difference): return chalk.bold('%s') % (
        chalk.red('DIFFERENT: %s!=%s' % (s1, s2) if print_difference else 'CHANGED') if s1 != s2 else chalk.green(
            "EQUAL"))

    return to_detailed_dict(result(True), result(False), 0 if s1 != s2 else 100)


def compare_methods_common_classes(dx1, dx2, only_internal=True):
    # type: (any, any) -> dict
    union_classes = set(dx1.classes).intersection(set(dx2.classes))
    meths_dx1 = represent_methods(dx1, union_classes, only_internal)
    meths_dx2 = represent_methods(dx2, union_classes, only_internal)

    return compare_lists(meths_dx1, meths_dx2)


def compare_methods(dx1, dx2, only_internals=True):
    # type: (androguard.misc.Analysis, androguard.misc.Analysis) -> dict
    meths_dx1 = represent_methods(dx1, None, only_internals)
    meths_dx2 = represent_methods(dx2, None, only_internals)

    return compare_lists(meths_dx1, meths_dx2)

def compare_fields(dx1, dx2):
    # type: (any, any) -> dict
    fields_dx1 = map(lambda f: str(f.get_field()), dx1.get_fields())
    fields_dx2 = map(lambda f: str(f.get_field()), dx2.get_fields())
    return compare_lists(fields_dx1, fields_dx2)

analysis_rows, ground_truth_rows = [], []
analysis_header = ['Ref.',
                   'And. vcode',
                   'And. vname',
                   'minsdk',
                   'maxsdk',
                   'targetsdk',
                   'efftarget',
                   'permissions',
                   'package',
                   'appname',
                   'activities',
                   'Resources',
                   'Services',
                   'Receivers',
                   'Classes',
                   'Methods All',
                   'Methods Common cls',
                   'Methods All(ext)',
                   'Meths Com. cls(ext)',
                   'Strings',
                   'Fields',
                   'GRND TRUTH']
ground_truth_header = ['Ref.',
                      'Ground Truth',
                      'Score',
                      'Tool Result',
                      'Tool Conclusion']

with open('data/common_with_groundtruth.txt') as f:
    for line in f.readlines():
        [original_apk_hash, repackaged_apk_hash,
         grnd_is_similar] = line.strip().split(',')
        print chalk.bold(
            "\n\n################################################################### Analyzing pair of dataset: [%s...],[%s...] ###################################################################") % (
                  chalk.blue(chalk.bold(original_apk_hash[:10])), chalk.bold(repackaged_apk_hash[:10]))

        # TODO check if apk exist, if not download
        a1, d1, dx1 = androguard.misc.AnalyzeAPK(
            "./data/apks/%s.apk" % original_apk_hash)

        a2, d2, dx2 = androguard.misc.AnalyzeAPK(
            "./data/apks/%s.apk" % repackaged_apk_hash)



        # COMPARISONS
        comparisons = [
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
            compare_strings(
                a1.get_package(), a2.get_package()),
            compare_strings(
                a1.get_app_name(), a2.get_app_name()),
            compare_lists(
                a1.get_activities(), a2.get_activities()),
            compare_lists(
                a1.get_files(), a2.get_files()),
            compare_lists(
                a1.get_services(), a2.get_services()),
            compare_lists(
                a1.get_receivers(), a2.get_receivers()),
            compare_lists(
                dx1.classes, dx2.classes),
            compare_methods(dx1, dx2),
            compare_methods_common_classes(dx1, dx2),
            compare_methods(dx1, dx2, False),
            compare_methods_common_classes(dx1, dx2, False),
            compare_lists(dx1.strings, dx2.strings),
            compare_fields(dx1,dx2)
        ]

        print '=============================================='
        print 'Android version code: %s' % comparisons[0]['detailed']
        print 'Android version name: %s' % comparisons[1]['detailed']
        print 'Min SDK version: %s' % comparisons[2]['detailed']
        print 'Max SDK version: %s' % comparisons[3]['detailed']
        print 'Target SDK version: %s' % comparisons[4]['detailed']
        print 'Effective Target SDK version: %s' % comparisons[5]['detailed']
        print '=============================================='
        print "Permissions: %s" % comparisons[6]['detailed']
        print '=============================================='
        print 'Package name: %s' % comparisons[7]['detailed']
        print '=============================================='
        print 'APP name: %s' % comparisons[8]['detailed']
        print '=============================================='
        print 'Activities: %s' % comparisons[9]['detailed']
        print '=============================================='
        print 'Resources: %s' % comparisons[10]['detailed']
        print '=============================================='
        print 'Services: %s' % comparisons[11]['detailed']
        print '=============================================='
        print 'Receivers: %s' % comparisons[12]['detailed']
        print '=============================================='
        print 'Classes: %s' % comparisons[13]['detailed']
        print '=============================================='
        print 'Methods: %s' % comparisons[14]['detailed']
        print '=============================================='
        print 'Methods Common classes: %s' % comparisons[15]['detailed']
        print '=============================================='
        print '(ext. incl.) Methods: %s' % comparisons[16]['detailed']
        print '=============================================='
        print '(ext. incl.) Methods Common classes: %s' % comparisons[17]['detailed']
        print '=============================================='
        print 'Strings: %s' % comparisons[18]['detailed']
        print '=============================================='
        print 'Fields: %s' % comparisons[19]['detailed']
        print '========================= CURRENT ANALYSIS ========================='

        analysis_rows = analysis_rows + [[chalk.blue(chalk.bold("%s" % original_apk_hash[:10]))] +
                                         map(lambda comparison: comparison['not_detailed'], comparisons) +
                                         [grnd_is_similar]]

        print tabulate(analysis_rows, headers=analysis_header, tablefmt="grid")

        avg_score = sum(
            map(lambda x: x['score'], comparisons)) / len(comparisons)
        tool_result = "SIMILAR" if avg_score >= THRESHOLD else "NOT_SIMILAR"
        ground_truth_rows = ground_truth_rows + [[chalk.blue(chalk.bold("%s" % original_apk_hash[:10])),
                                                  grnd_is_similar,
                                                  avg_score,
                                                  chalk.bold(chalk.red(
                                                      tool_result) if tool_result != grnd_is_similar else chalk.green(
                                                      tool_result)),
                                                  chalk.bold(chalk.red(
                                                      "WRONG") if tool_result != grnd_is_similar else chalk.green(
                                                      "RIGHT"))]]
        accuracy = "%d" % (round((float(len(filter(lambda v: v == chalk.bold(chalk.green("RIGHT")), map(
            lambda row: row[4], ground_truth_rows)))) / len(ground_truth_rows)) * 100, 2)) if len(
            ground_truth_rows) > 0 else "NA"
        print tabulate(ground_truth_rows, headers=ground_truth_header, tablefmt="grid")

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

        print "======= CURRENT THRESHOLD %s%% ======= CURRENT ACCURACY: %s ======= RECOMMENDED THRESHOLD %s%%    " % (
            chalk.blue(THRESHOLD), chalk.bold(chalk.blue(accuracy + "%")), chalk.bold(recommended_threshold))
        summary_report.write(
            "\n======= CURRENT THRESHOLD %s%% ======= CURRENT ACCURACY: %s ======= RECOMMENDED THRESHOLD %s%%    " % (
                chalk.blue(THRESHOLD), chalk.bold(chalk.blue(accuracy + "%")), chalk.bold(recommended_threshold)))
        # setting threshold to recommended
        if recommended_threshold != "ND":
            THRESHOLD = recommended_threshold

summary_report.write("\nFINAL ANALYSIS TABLE: \n")
summary_report.write(tabulate(analysis_rows, headers=analysis_header, tablefmt="grid"))
summary_report.write(tabulate(ground_truth_rows, headers=ground_truth_header, tablefmt="grid"))
summary_report.close()

# print "CACHING...."
# if not os.path.exists("./cache/analysis.bin"):
# with open("./cache/analysis.bin", "w") as file:
#     pickle.dump(cache, file)
