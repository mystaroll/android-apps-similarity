#!/usr/bin/env python
# encoding=utf8
import androguard.misc
import cPickle
import os
import hashlib
from sklearn.feature_extraction import DictVectorizer
import urllib2

VERSION = "0.0.1"

apks_dir = "data/apks"
if not os.path.exists("cache"):
    os.makedirs("cache")
if not os.path.exists(apks_dir):
    os.makedirs(apks_dir)
apks_list = os.listdir(apks_dir)

def download_if_not_exists(hash):
    global apks_dir, apks_list
    if (hash + ".apk" in apks_list):
        with open(apks_dir+"/"+hash + ".apk", "rb") as existing_apk:
            hash_in_file = hashlib.sha256(existing_apk.read()).hexdigest().upper()
        if hash_in_file != hash:
            print "\n File exists but no equal hashes: %s, %s" % (hash,hash_in_file)
        else:
            print "file apk exists, not downloading"
            return

    print "Apk not downloaded, downloading now...\n"
    with open(apks_dir + "/" + hash + ".apk", "wb") as fapk:
        fapk.write(urllib2.urlopen(
            "https://androzoo.uni.lu/api/download?apikey=a52054307648be3c6b753eb55c093f4c2fa4b03e452f8ed245db653fee146cdd&sha256=%s" % hash).read())
        print "Download completed\n"


def represent_methods(dx, restrict_classes=None, only_internal=True):
    return map(
        lambda internal_method: "%s->%s%s" % (internal_method.get_method().class_name, internal_method.get_method(
        ).get_name(), internal_method.get_method(
        ).get_descriptor()),
        filter(lambda mth: restrict_classes == None or mth.get_method().class_name in restrict_classes,
               filter(lambda method: (not method.is_external()) or (not only_internal), dx.get_methods())))


def compute_raw_feature_vector(a1):
    vector_feature_dict = {
        'And. vcode': str(a1.get_androidversion_code()),
        'And. vname': str(a1.get_androidversion_name()),
        'minsdk': str(a1.get_min_sdk_version()),
        'maxsdk': str(a1.get_max_sdk_version()),
        'targetsdk': str(a1.get_target_sdk_version()),
        'efftarget': str(a1.get_effective_target_sdk_version()),
        'package': str(a1.get_package()),
        # 'permissions': str(a1.get_permissions()),
        # str(a1.get_app_name())
        # a1.get_activities(),
        # a1.get_files(),
        # a1.get_services(),
        # a1.get_receivers(),
        # dx1.classes,
        # represent_methods(dx1, None, True),
        # represent_methods(dx1, None, False),
        # dx1.strings,
        # map(lambda f: str(f.get_field()), dx1.get_fields())
    }
    for permission in permissions:
        if not vector_feature_dict.has_key(permission):
            vector_feature_dict[permission] = 0
    for permission in a1.get_permissions():
        if not vector_feature_dict.has_key(permission):
            vector_feature_dict[permission] = 1
    return vector_feature_dict
# build feature vector

print "Getting feature vectors"
vectors = []
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

with open('data/groundtruth.txt') as f:
    for line in f.readlines()[:2]:
        [original_apk_hash, repackaged_apk_hash,
         grnd_is_similar] = line.strip().split(',')


        cache_filename = "vect-" + hashlib.sha256(bytes(original_apk_hash + VERSION)).hexdigest().upper()
        # if os.path.exists("./cache/" + cache_filename):
        #     # print "CACHED getting results...."
        #     with open("./cache/" + cache_filename, "rb") as file:
        #         feature_vector = cPickle.load(file)
        # else:
        download_if_not_exists(original_apk_hash)
        a1, d1, dx1 = androguard.misc.AnalyzeAPK(
            "./data/apks/%s.apk" % original_apk_hash)
        feature_vector = compute_raw_feature_vector(a1)
        print "CACHING...."
        with open("./cache/" + cache_filename, "wb") as file:
            cPickle.dump(feature_vector, file)
        vectors += [feature_vector]

# print(vector)#"\n".join(vector))
vec = DictVectorizer()
feature_vectors = vec.fit_transform(vectors).toarray()
# print vectors

searched_hash = "01195C7318FB8EFFA28DB5E32C46599C30C18B8743781C30470ADE92D83CAEA5"
# with open("./data/apks/01195C7318FB8EFFA28DB5E32C46599C30C18B8743781C30470ADE92D83CAEA5.apk") as searched_apk:
print "Searching given hash %s" % searched_hash

download_if_not_exists(searched_hash)
a1, d1, dx1 = androguard.misc.AnalyzeAPK(
    "./data/apks/%s.apk" % searched_hash)

searched_feature_vector = vec.transform(compute_raw_feature_vector(a1)).toarray()
