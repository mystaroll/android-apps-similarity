#!/usr/bin/env python
import androguard.misc
import os
import chalk
import sys
from tabulate import tabulate

print 'Checking existing session'
SESSION_FILENAME = 'session.ag'
s = androguard.session.Load(SESSION_FILENAME) if os.path.exists(
    SESSION_FILENAME) else androguard.session.Session()


def compare_lists(l1, l2, print_difference=True):
    difference1 = set(l1).difference(l2)
    difference2 = set(l2).difference(l1)
    return chalk.bold('%s') % (chalk.red('\nDELETED %s\n---\nADDED %s' % (str(difference1), str(difference2)) if print_difference else 'CHANGED') if len(
        difference1) != 0 or len(
        difference2) != 0 else chalk.green("EQUAL"))


def compare_strings(s1, s2, print_difference=True):
    return chalk.bold('%s') % (chalk.red('DIFFERENT: %s!=%s' % (s1, s2) if print_difference else 'CHANGED') if s1 != s2 else chalk.green("EQUAL"))


analysis_rows = []

with open('data/common.txt') as f:
    for line in f.readlines():
        [original_apk_hash, repackaged_apk_hash] = line.strip().split(',')
        print chalk.bold("Analyzing pair of dataset: [%s...],[%s...]") % (
            original_apk_hash[:10], repackaged_apk_hash[:10])

        # TODO check if apk exist, if not download
        a1, d1, dx1 = androguard.misc.AnalyzeAPK(
            "./data/pairs/original/%s.apk" % original_apk_hash)

        a2, d2, dx2 = androguard.misc.AnalyzeAPK(
            "./data/pairs/repackaged/%s.apk" % repackaged_apk_hash)
        # COMPARISONS

        print '\n==============================================\n'
        print 'Android version code: %s' % compare_strings(
            a1.get_androidversion_code(), a2.get_androidversion_code())

        print '\nAndroid version name: %s' % compare_strings(
            a1.get_androidversion_name(), a2.get_androidversion_name())

        print '\nMin SDK version: %s' % compare_strings(
            a1.get_min_sdk_version(), a2.get_min_sdk_version())

        print '\nMax SDK version: %s' % compare_strings(
            a1.get_max_sdk_version(), a2.get_max_sdk_version())

        print '\nTarget SDK version: %s' % compare_strings(
            a1.get_target_sdk_version(), a2.get_target_sdk_version())

        print '\nEffective Target SDK version: %s' % compare_strings(
            a1.get_effective_target_sdk_version(), a2.get_effective_target_sdk_version())
        print '\n==============================================\n'
        print "Permissions: %s" % compare_lists(
            a1.get_permissions(), a2.get_permissions())

        print '\n==============================================\n'
        print 'Package name: %s' % compare_strings(
            a1.get_package(), a2.get_package())

        print '\n==============================================\n'
        print 'APP name: %s' % compare_strings(
            a1.get_app_name(), a2.get_app_name())

        print '\n==============================================\n'
        print 'Activities: %s' % compare_lists(
            a1.get_activities(), a2.get_activities())

        print '\n==============================================\n'
        print 'Files: %s' % compare_lists(
            a1.get_files(), a2.get_files())

        print '\n==============================================\n'
        print 'Services: %s' % compare_lists(
            a1.get_services(), a2.get_services())

        print '\n==============================================\n'
        print 'Receivers: %s' % compare_lists(
            a1.get_receivers(), a2.get_receivers())

        print '\n========================= CURRENT ANALYSIS =========================\n'

        analysis_rows = analysis_rows + [[
            compare_strings(
                a1.get_androidversion_code(), a2.get_androidversion_code(), False),
            compare_strings(
                a1.get_androidversion_name(), a2.get_androidversion_name(), False),
            compare_strings(
                a1.get_min_sdk_version(), a2.get_min_sdk_version(), False),
            compare_strings(
                a1.get_max_sdk_version(), a2.get_max_sdk_version(), False),
            compare_strings(
                a1.get_target_sdk_version(), a2.get_target_sdk_version(), False),
            compare_strings(
                a1.get_effective_target_sdk_version(), a2.get_effective_target_sdk_version(), False),
            compare_lists(
                a1.get_permissions(), a2.get_permissions(), False),
            compare_strings(
                a1.get_package(), a2.get_package(), False),
            compare_strings(
                a1.get_app_name(), a2.get_app_name(), False),
            compare_lists(
                a1.get_activities(), a2.get_activities(), False),
            compare_lists(
                a1.get_files(), a2.get_files(), False),
            compare_lists(
                a1.get_services(), a2.get_services(), False),
            compare_lists(
                a1.get_receivers(), a2.get_receivers(), False)
        ]]
        print tabulate(analysis_rows, headers=['And. vcode',
                                               'And. vname',
                                               'minsdk',
                                               'maxsdk',
                                               'targetsdk',
                                               'efftarget',
                                               'permissions',
                                               'package',
                                               'appname',
                                               'activities',
                                               'Files',
                                               'Services',
                                               'Receivers'])


# s.save(SESSION_FILENAME)
# androguard.session.Save(s, SESSION_FILENAME)

# sys.exit(0)
