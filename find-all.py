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

def addline(no,group,value,line):
    if value:
        value="<<%s>>" % value
    items.append("%s: %s %s %s" % (no, group,value,line))

for line in generator.readlines():
    nr+=1
    line = line.strip().replace('"',"'")

    if re.search (r'''def\s?.*\:''', line):
        if empty and items:
            items.pop()
        #method = re.sub(r'''^.*def\s?[^']+:.*$''',
        #                '\\0', line)
        addline(nr,'DEF','',line)
        empty=True

    if re.search (r'''getTaggedValue\s?\(''', line):
        tgv = re.sub(r'''^.*getTaggedValue\s?\(['"]([^']+)['"].*$''',
                        '\\1', line)
        addline(nr,'TGV',tgv,line)
        empty=False

    if line.find('getTaggedValues') >= 0:
        addline(nr,'TGVS','',line)
        empty=False

    if re.search (r'''hasStereoType\s?\(''', line):
        stt = re.sub(r'''^.*hasStereoType\s?\(['"]([^']+)['"].*$''',
                        '\\1', line)
        addline(nr,'STT',stt,line)
        empty=False


#items.sort()
prevItem = ''

for item in items:
    if item != prevItem:
        print item
    prevItem = item
