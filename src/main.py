#!/usr/bin/env python
import androguard.misc
import os
import chalk

with open('data/pairs.txt') as f:
    [original_apk_hash, repackaged_apk_hash] = f.readline().strip().split(',')
    print chalk.bold("Using first pair of dataset: [%s...],[%s...]") % (
        original_apk_hash[:10], repackaged_apk_hash[:10])


print chalk.bold('Analyzing original apk:')
# TODO check if apk exist, if not download
a1, d1, dx1 = androguard.misc.AnalyzeAPK(
    "./data/pairs/original/%s.apk" % original_apk_hash)

a2, d2, dx2 = androguard.misc.AnalyzeAPK(
    "./data/pairs/repackaged/%s.apk" % repackaged_apk_hash)

print '\nPermissions ORIGINAL:'
print a1.get_permissions()

print '\nPermissions REPACKAGED:'
print a2.get_permissions()

perm_difference = set(a1.get_permissions()).difference(a2.get_permissions())

print chalk.bold('\nPermissions DIFFERENCE: %s') % (chalk.red(perm_difference) if len(
    perm_difference) != 0 else chalk.green("EQUAL"))
