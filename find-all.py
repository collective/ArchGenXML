#!/usr/bin/python

#
# Find all tagged values read in ArchetypesGenerator.py and print a sorted list
#

import re
import sys

generator = open('ArchetypesGenerator.py', 'r')

items = []
nr = 0

empty = False

for line in generator.readlines():
    nr+=1
    line = line.strip()

    #import pdb
    #if line.find('def') >0 and line.find('default') == -1:
    #    pdb.set_trace()

    if re.search (r'''def\s?.*\:''', line):
        if empty and items:
            items.pop()
        #method = re.sub(r'''^.*def\s?[^']+:.*$''',
        #                '\\0', line)
        items.append("%d: DEF  %s" % (nr, line))
        empty=True

    if re.search (r'''getTaggedValue\s?\(''', line):
        line = re.sub(r'''^.*getTaggedValue\s?\(['"]([^']+)['"].*$''',
                        '\\1', line)
        items.append ('%d: TGV  %s' % (nr,line))
        empty=False

    if line.find('getTaggedValues') >= 0:
        items.append ('%d: TGVS %s' % (nr, line))
        empty=False

    if re.search (r'''hasStereoType\s?\(''', line):
        line = re.sub(r'''^.*hasStereoType\s?\(['"]([^']+)['"].*$''',
                        '\\1', line)
        items.append ('%d: STT  %s' % (nr,line))
        empty=False


#items.sort()
prevItem = ''

for item in items:
    if item != prevItem:
        print item
    prevItem = item
