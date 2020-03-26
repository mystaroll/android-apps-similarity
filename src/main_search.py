#!/usr/bin/env python
# encoding=utf8
import androguard.misc
import _pickle as cPickle
import os
import hashlib
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics.pairwise import euclidean_distances
import urllib
import argparse
import sys
import ngram
from datetime import datetime
from tabulate import tabulate
import gc
# import ray
import multiprocessing as mp
# reload(sys)
# sys.setdefaultencoding('utf8')

VERSION = "0.0.2"

parser = argparse.ArgumentParser(
    description='Given a hash of an apk, this script searches for the most similar app in the dataset')

parser.add_argument("-s",
                    help="Search single hash", type=str)
parser.add_argument("--ngrams", default=4,
                    help="n grams to use for strings and sets", type=int)
parser.add_argument("--processes", default = 8,
                    help="Number of processes to use for multiprocessing, defaults to 8", type=int)
parser.add_argument("--nocache", default=False,
                    help="If to use the cache", type=bool)
parser.add_argument("--output", default=datetime.now().strftime("%Y%m%d%H%M"),
                    help="Suffix for summary report", type=str)
parser.add_argument("--threshold", default=100,
                    help="Euclidean distance threshold to use for considering two apps similar", type=int)
parser.add_argument("-n",
                    help="Evaluate only the first n lines of the dataset", type=int)
args = parser.parse_args()
N_GRAMS = args.ngrams
N_PROCESSES = args.processes

THRESHOLD = args.threshold
apks_dir = "data/apks"
if not os.path.exists("cache"):
    os.makedirs("cache")
if not os.path.exists(apks_dir):
    os.makedirs(apks_dir)
apks_list = os.listdir(apks_dir)


def download_if_not_exists(hash):
    global apks_dir, apks_list
    if (hash + ".apk" in apks_list):
        with open(apks_dir + "/" + hash + ".apk", "rb") as existing_apk:
            hash_in_file = hashlib.sha256(existing_apk.read()).hexdigest().upper()
        if hash_in_file == hash:  # print "\n File exists but no equal hashes: %s, %s" % (hash,hash_in_file)
            # print "file apk exists, not downloading"
            return

    print("Apk not downloaded, downloading now...\n")
    with open(apks_dir + "/" + hash + ".apk", "wb") as fapk:
        fapk.write(urllib.urlopen(
            "https://androzoo.uni.lu/api/download?apikey=a52054307648be3c6b753eb55c093f4c2fa4b03e452f8ed245db653fee146cdd&sha256=%s" % hash).read())
        print("Download completed\n")


def represent_methods(dx, restrict_classes=None, only_internal=True):
    return map(
        lambda internal_method: "%s->%s%s" % (internal_method.get_method().class_name, internal_method.get_method(
        ).get_name(), internal_method.get_method(
        ).get_descriptor()),
        filter(lambda mth: restrict_classes == None or mth.get_method().class_name in restrict_classes,
               filter(lambda method: (not method.is_external()) or (not only_internal), dx.get_methods())))


def string_to_feature_vector(key, string):
    ng = ngram.NGram(N=N_GRAMS, pad_len=0)
    grams = ng.split(string)
    res = dict()
    for word in grams:
        res[key + "-" + unicode(word, 'utf-8', 'ignore')] = 1
    return res


def list_to_feature_vector(key, lst):
    # grams = [lst[i:i + N_GRAMS] for i in xrange(len(lst) - N_GRAMS + 1)]
    res = dict()
    for el in lst:
        res.update(string_to_feature_vector(key, str(el)))
    return res


def compute_raw_feature_vector(a1, dx1):
    vector_feature_dict = {
        'And. vcode': str(a1.get_androidversion_code()),
        'And. vname': str(a1.get_androidversion_name()),
        'minsdk': str(a1.get_min_sdk_version()),
        'maxsdk': str(a1.get_max_sdk_version()),
        'targetsdk': str(a1.get_target_sdk_version()),
        'efftarget': str(a1.get_effective_target_sdk_version())

    }
    # package name
    vector_feature_dict.update(string_to_feature_vector("package", str(a1.get_package())))

    # app name
    vector_feature_dict.update(string_to_feature_vector("appname", str(a1.get_app_name())))

    # activities
    vector_feature_dict.update(list_to_feature_vector("activities", a1.get_activities()))

    # resources files
    vector_feature_dict.update(list_to_feature_vector("resfiles", a1.get_files()))

    # services
    vector_feature_dict.update(list_to_feature_vector("services", a1.get_services()))

    # receivers
    vector_feature_dict.update(list_to_feature_vector("receivers", a1.get_receivers()))

    # methods
    vector_feature_dict.update(list_to_feature_vector("services", represent_methods(dx1)))

    # fields
    vector_feature_dict.update(list_to_feature_vector("fields", map(lambda f: str(f.get_field()), dx1.get_fields())))

    # strings
    vector_feature_dict.update(list_to_feature_vector("strings", list(dx1.strings)))

    # Permissions
    for permission in permissions:
        if not vector_feature_dict.has_key(permission):
            vector_feature_dict[permission] = 0
    for permission in a1.get_permissions():
        if not vector_feature_dict.has_key(permission):
            vector_feature_dict[permission] = 1
    return vector_feature_dict

# @profile
def get_raw_feature_vector_from_hash(hash):
    cache_filename = "vect-" + hashlib.sha256(bytes(hash + VERSION, encoding='utf8')).hexdigest().upper()
    if os.path.exists("./cache/" + cache_filename) and not args.nocache:
        # print "FEATURE VECTOR CACHED getting results...."
        with open("./cache/" + cache_filename, "rb") as file:
            feature_vector = cPickle.load(file)
    else:
        try:
            download_if_not_exists(hash)
            a1, d1, dx1 = androguard.misc.AnalyzeAPK(
                "./data/apks/%s.apk" % hash)
            feature_vector = compute_raw_feature_vector(a1, dx1)
            print("CACHING....")
            with open("./cache/" + cache_filename, "wb") as file:
                cPickle.dump(feature_vector, file)

        except urllib.HTTPError as err:
            print("Cannot download the hash from Androzoo %s" % str(err))
            raise err
        except Exception as err:
            print("Failed to get feature vector of apk %s, skipping.. %s" % (hash, err))
            raise err
    return feature_vector


def compute_distances_from_hash(vectorizer,feature_vectors,hash):
    raw_feature_vec = get_raw_feature_vector_from_hash(hash)
    searched_feature_vector = vectorizer.transform(raw_feature_vec).toarray()
    return euclidean_distances(feature_vectors, searched_feature_vector)


# build feature vector
ground_truth_header = ['Ref.',
                       'Ground Truth',
                       'Distance',
                       'Tool Result',
                       'Tool Conclusion']
permissions = [
    "android.permission.ACCEPT_HANDOVER",
    "android.permission.ACCESS_BACKGROUND_LOCATION",
    "android.permission.ACCESS_CHECKIN_PROPERTIES",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.ACCESS_LOCATION_EXTRA_COMMANDS",
    "android.permission.ACCESS_MEDIA_LOCATION",
    "android.permission.ACCESS_NETWORK_STATE",
    "android.permission.ACCESS_NOTIFICATION_POLICY",
    "android.permission.ACCESS_WIFI_STATE",
    "android.permission.ACCOUNT_MANAGER",
    "android.permission.ACTIVITY_RECOGNITION",
    "android.permission.ADD_VOICEMAIL",
    "android.permission.ANSWER_PHONE_CALLS",
    "android.permission.BATTERY_STATS",
    "android.permission.BIND_ACCESSIBILITY_SERVICE",
    "android.permission.BIND_APPWIDGET",
    "android.permission.BIND_AUTOFILL_SERVICE",
    "android.permission.BIND_CALL_REDIRECTION_SERVICE",
    "android.permission.BIND_CARRIER_MESSAGING_CLIENT_SERVICE",
    "android.permission.BIND_CARRIER_MESSAGING_SERVICE",
    "android.permission.BIND_CARRIER_SERVICES",
    "android.permission.BIND_CHOOSER_TARGET_SERVICE",
    "android.permission.BIND_CONDITION_PROVIDER_SERVICE",
    "android.permission.BIND_DEVICE_ADMIN",
    "android.permission.BIND_DREAM_SERVICE",
    "android.permission.BIND_INCALL_SERVICE",
    "android.permission.BIND_INPUT_METHOD",
    "android.permission.BIND_MIDI_DEVICE_SERVICE",
    "android.permission.BIND_NFC_SERVICE",
    "android.permission.BIND_NOTIFICATION_LISTENER_SERVICE",
    "android.permission.BIND_PRINT_SERVICE",
    "android.permission.BIND_QUICK_ACCESS_WALLET_SERVICE",
    "android.permission.BIND_QUICK_SETTINGS_TILE",
    "android.permission.BIND_REMOTEVIEWS",
    "android.permission.BIND_SCREENING_SERVICE",
    "android.permission.BIND_TELECOM_CONNECTION_SERVICE",
    "android.permission.BIND_TEXT_SERVICE",
    "android.permission.BIND_TV_INPUT",
    "android.permission.BIND_VISUAL_VOICEMAIL_SERVICE",
    "android.permission.BIND_VOICE_INTERACTION",
    "android.permission.BIND_VPN_SERVICE",
    "android.permission.BIND_VR_LISTENER_SERVICE",
    "android.permission.BIND_WALLPAPER",
    "android.permission.BLUETOOTH",
    "android.permission.BLUETOOTH_ADMIN",
    "android.permission.BLUETOOTH_PRIVILEGED",
    "android.permission.BODY_SENSORS",
    "android.permission.BROADCAST_PACKAGE_REMOVED",
    "android.permission.BROADCAST_SMS",
    "android.permission.BROADCAST_STICKY",
    "android.permission.BROADCAST_WAP_PUSH",
    "android.permission.CALL_COMPANION_APP",
    "android.permission.CALL_PHONE",
    "android.permission.CALL_PRIVILEGED",
    "android.permission.CAMERA",
    "android.permission.CAPTURE_AUDIO_OUTPUT",
    "android.permission.CHANGE_COMPONENT_ENABLED_STATE",
    "android.permission.CHANGE_CONFIGURATION",
    "android.permission.CHANGE_NETWORK_STATE",
    "android.permission.CHANGE_WIFI_MULTICAST_STATE",
    "android.permission.CHANGE_WIFI_STATE",
    "android.permission.CLEAR_APP_CACHE",
    "android.permission.CONTROL_LOCATION_UPDATES",
    "android.permission.DELETE_CACHE_FILES",
    "android.permission.DELETE_PACKAGES",
    "android.permission.DIAGNOSTIC",
    "android.permission.DISABLE_KEYGUARD",
    "android.permission.DUMP",
    "android.permission.EXPAND_STATUS_BAR",
    "android.permission.FACTORY_TEST",
    "android.permission.FOREGROUND_SERVICE",
    "android.permission.GET_ACCOUNTS",
    "android.permission.GET_ACCOUNTS_PRIVILEGED",
    "android.permission.GET_PACKAGE_SIZE",
    "android.permission.GET_TASKS",
    "android.permission.GLOBAL_SEARCH",
    "android.permission.INSTALL_LOCATION_PROVIDER",
    "android.permission.INSTALL_PACKAGES",
    "android.permission.INSTALL_SHORTCUT",
    "android.permission.INSTANT_APP_FOREGROUND_SERVICE",
    "android.permission.INTERACT_ACROSS_PROFILES",
    "android.permission.INTERNET",
    "android.permission.KILL_BACKGROUND_PROCESSES",
    "android.permission.LOCATION_HARDWARE",
    "android.permission.MANAGE_DOCUMENTS",
    "android.permission.MANAGE_EXTERNAL_STORAGE",
    "android.permission.MANAGE_OWN_CALLS",
    "android.permission.MASTER_CLEAR",
    "android.permission.MEDIA_CONTENT_CONTROL",
    "android.permission.MODIFY_AUDIO_SETTINGS",
    "android.permission.MODIFY_PHONE_STATE",
    "android.permission.MOUNT_FORMAT_FILESYSTEMS",
    "android.permission.MOUNT_UNMOUNT_FILESYSTEMS",
    "android.permission.NFC",
    "android.permission.NFC_PREFERRED_PAYMENT_INFO",
    "android.permission.NFC_TRANSACTION_EVENT",
    "android.permission.PACKAGE_USAGE_STATS",
    "android.permission.PERSISTENT_ACTIVITY",
    "android.permission.PROCESS_OUTGOING_CALLS",
    "android.permission.QUERY_ALL_PACKAGES",
    "android.permission.READ_CALENDAR",
    "android.permission.READ_CALL_LOG",
    "android.permission.READ_CONTACTS",
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.READ_INPUT_STATE",
    "android.permission.READ_LOGS",
    "android.permission.READ_PHONE_NUMBERS",
    "android.permission.READ_PHONE_STATE",
    "android.permission.READ_PRECISE_PHONE_STATE",
    "android.permission.READ_SMS",
    "android.permission.READ_SYNC_SETTINGS",
    "android.permission.READ_SYNC_STATS",
    "android.permission.READ_VOICEMAIL",
    "android.permission.REBOOT",
    "android.permission.RECEIVE_BOOT_COMPLETED",
    "android.permission.RECEIVE_MMS",
    "android.permission.RECEIVE_SMS",
    "android.permission.RECEIVE_WAP_PUSH",
    "android.permission.RECORD_AUDIO",
    "android.permission.REORDER_TASKS",
    "android.permission.REQUEST_COMPANION_RUN_IN_BACKGROUND",
    "android.permission.REQUEST_COMPANION_USE_DATA_IN_BACKGROUND",
    "android.permission.REQUEST_DELETE_PACKAGES",
    "android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS",
    "android.permission.REQUEST_INSTALL_PACKAGES",
    "android.permission.REQUEST_PASSWORD_COMPLEXITY",
    "android.permission.RESTART_PACKAGES",
    "android.permission.SEND_RESPOND_VIA_MESSAGE",
    "android.permission.SEND_SMS",
    "android.permission.SET_ALARM",
    "android.permission.SET_ALWAYS_FINISH",
    "android.permission.SET_ANIMATION_SCALE",
    "android.permission.SET_DEBUG_APP",
    "android.permission.SET_PREFERRED_APPLICATIONS",
    "android.permission.SET_PROCESS_LIMIT",
    "android.permission.SET_TIME",
    "android.permission.SET_TIME_ZONE",
    "android.permission.SET_WALLPAPER",
    "android.permission.SET_WALLPAPER_HINTS",
    "android.permission.SIGNAL_PERSISTENT_PROCESSES",
    "android.permission.SMS_FINANCIAL_TRANSACTIONS",
    "android.permission.START_VIEW_PERMISSION_USAGE",
    "android.permission.STATUS_BAR",
    "android.permission.SYSTEM_ALERT_WINDOW",
    "android.permission.TRANSMIT_IR",
    "android.permission.UNINSTALL_SHORTCUT",
    "android.permission.UPDATE_DEVICE_STATS",
    "android.permission.USE_BIOMETRIC",
    "android.permission.USE_FINGERPRINT",
    "android.permission.USE_FULL_SCREEN_INTENT",
    "android.permission.USE_SIP",
    "android.permission.VIBRATE",
    "android.permission.WAKE_LOCK",
    "android.permission.WRITE_APN_SETTINGS",
    "android.permission.WRITE_CALENDAR",
    "android.permission.WRITE_CALL_LOG",
    "android.permission.WRITE_CONTACTS",
    "android.permission.WRITE_EXTERNAL_STORAGE",
    "android.permission.WRITE_GSERVICES",
    "android.permission.WRITE_SECURE_SETTINGS",
    "android.permission.WRITE_SETTINGS",
    "android.permission.WRITE_SYNC_SETTINGS",
    "android.permission.WRITE_VOICEMAIL"
]

# @ray.remote
def build_raw_feature_vector(opts):
        dataset_line, use_repackaged=opts
        raw_feature = None
        skipped_apk = ""
        num,line = dataset_line
        print("Process running line: %s" % ( num))
        [original_apk_hash,repackaged_apk_hash,_] = line.strip().split(',')
        hash_to_use = repackaged_apk_hash if use_repackaged else original_apk_hash
        try:
            raw_feature = get_raw_feature_vector_from_hash(hash_to_use)
        except:
            skipped_apk = hash_to_use
        
        return (num, raw_feature, skipped_apk)

# @profile
def evaluate(file_lines, vec, feature_vectors):
    ground_truth_rows = []
    skipped_apks = set()
    for num, line in file_lines:
        [_, repackaged_apk_hash,
         gnd] = line.strip().split(',')
        print("Searching (idx %s), repackaged app %s " % (num, repackaged_apk_hash))
        try:
            euclidean_distances_vector = compute_distances_from_hash(vec, feature_vectors, repackaged_apk_hash)
            min_distance_idx = euclidean_distances_vector.argmin()

            grnd_truth_result = "SIMILAR(%s)" % num if gnd == "SIMILAR" else "NOT_SIMILAR"
            tool_result = "SIMILAR(%s)" % file_lines[min_distance_idx][0] if euclidean_distances_vector[
                                                                min_distance_idx] <= THRESHOLD else "NOT_SIMILAR"
            
            row = [num,
                grnd_truth_result,
                euclidean_distances_vector[min_distance_idx],
                tool_result,
                "RIGHT" if grnd_truth_result == tool_result else "WRONG"]
            ground_truth_rows.append(
              row  )
            print(row)
        except:
            skipped_apks.add(repackaged_apk_hash)
            continue
    return ground_truth_rows, skipped_apks

def concurrent_process(target, opts_lst):
    """ chunk_size = 10 #trying to fix the memory leak
    res = []
    for chunkidx in range(0, len(opts_lst),chunk_size):
        p = Pool(N_PROCESSES,maxtasksperchild=10)
        res.extend(p.map(target, opts_lst[chunkidx:chunkidx+chunk_size]))
        p.close() """
    p = mp.Pool(N_PROCESSES, maxtasksperchild=100)#, initializer=init_proces
    res= p.map(target, opts_lst)
    p.close()
    
    return res

def main():
    # ray.init()
    vec = DictVectorizer()
    with open('data/groundtruth_search.txt') as f:
        file_lines = list(enumerate(f.readlines()))
        file_lines = file_lines[:args.n if args.n != None else len(file_lines)]
    raw_features = []
    skipped_apks = set()

    print("Getting feature vectors..")

    concurrent_process(build_raw_feature_vector, [(fn,True) for fn in file_lines]) 
    results = concurrent_process(build_raw_feature_vector, [(fn,False) for fn in file_lines])

    #use single processing because of memory leaks
    #map(build_raw_feature_vector, [(fn,True) for fn in file_lines])
    # ray.get([build_raw_feature_vector.remote((fn,True)) for fn in file_lines])
    # results = ray.get([build_raw_feature_vector.remote((fn,False)) for fn in file_lines])
    #map(build_raw_feature_vector, [(fn,True) for fn in file_lines])
    # after this the raw feature vectors are cached thus the evaluation call later has only IO overhead (and distance computing)
    
    for result in results:
        (num,raw_feature,skipped_apk) = result
        if raw_feature != None:
            raw_features.insert(num,raw_feature) #
        else:
            skipped_apks.add(skipped_apk)

    
    feature_vectors = vec.fit_transform(raw_features).toarray()
    del raw_features
    del results
    results =  raw_features = None
    gc.collect()
    
    if args.s != None:
        searched_hash = args.s
        print("Searching given hash %s" % searched_hash)
        euclidean_distances_vector = compute_distances_from_hash(vec, feature_vectors, searched_hash)
        min_distance_idx = euclidean_distances_vector.argmin()
        if euclidean_distances_vector[min_distance_idx] <= THRESHOLD:
            print("The given app is similar to (with distance %s) %s (index %s in the dataset) " % (
                euclidean_distances_vector[min_distance_idx],
                str(list(file_lines)[min_distance_idx][1].strip().split(',')[0]),
                min_distance_idx))
        else:
            print("The searched app has no similar app in the dataset")
    else:
        print("Evaluating dataset..")
        ground_truth_rows,skipped_searched_apks = evaluate(file_lines, vec, feature_vectors)
        with open('./report/report-search-SUMMARY-%s.txt' % (args.output), 'w') as summary_report:
            prints= ""
            prints += tabulate(ground_truth_rows, headers=ground_truth_header, tablefmt="grid")
            prints += "\nTotal wrong tool results: %s" % len(list(filter(lambda row: row[4] == "WRONG", ground_truth_rows)))

            similar_rows = list(filter(lambda row: "SIMILAR" in row[1][:7], ground_truth_rows))
            not_similar_rows = list(filter(lambda row: "NOT_SIMILAR" in row[1], ground_truth_rows))

            TP = len(list(filter(lambda row: "SIMILAR" in (row[3])[:7], similar_rows)))
            TN = len(list(filter(lambda row: "NOT_SIMILAR" in row[3], not_similar_rows)))
            FP = len(list(filter(lambda row: "SIMILAR" in (row[3])[:7], not_similar_rows)))
            FN = len(list(filter(lambda row: "NOT_SIMILAR" in row[3], similar_rows)))

            prints +="\n" + tabulate([
                ["TOOL_SIMILAR", "TP(%s)" % TP, "FP(%s)" % FP],
                ["TOOL_NOT_SIMILAR", "FN(%s)" % FN, "TN(%s)" % TN]
            ], ["", "GND_SIMILAR", "GND_NOT_SIMILAR"], tablefmt="grid")

            prints += "\n F1 SCORE: %s\n" %  (round((float(2 * TP) / (2 * TP + FN + FP)) *
                100, 2) if 2 * TP + FN + FP > 0 else "ND")
            prints +="\nMAX_DISTANCE_SIMILAR: %s" % (max(map(lambda row: row[2], similar_rows)) if len(similar_rows) >0 else "ND")
            prints +="\nMIN_DISTANCE_NON_SIMILAR: %s" % (min(map(lambda row: row[2], not_similar_rows)) if len(not_similar_rows) >0 else "ND")

            prints += "\nSkipped apks in building feature vectors: " + "\n".join(skipped_apks)
            prints += "\nSkipped apks in evaluating the dataset: " + "\n".join(skipped_searched_apks)
            summary_report.write(prints)
            print(prints)

if __name__ == '__main__':
    main()
