# patch DTML, make unicode aware. this is reported at zope-dev list
# we may remove this if zope.documenttemplate is fixed.
from types import TupleType, StringTypes
from zope.documenttemplate.ustr import ustr

def patched_render_blocks(blocks, md):
    rendered = []
    for section in blocks:
        if type(section) is TupleType:
            l = len(section)
            if l == 1:
                # Simple var
                section = section[0]
                if isinstance(section, StringTypes):
                    section = md[section]
                else:
                    section = section(md)
                section = ustr(section)
            else:
                # if
                cache = {}
                md._push(cache)
                try:
                    i = 0
                    m = l-1
                    while i < m:
                        cond = section[i]
                        if isinstance(cond, StringTypes):
                            n = cond
                            try:
                                cond = md[cond]
                                cache[n] = cond
                            except KeyError, v:
                                v = v[0]
                                if n != v:
                                    raise KeyError(v), None, sys.exc_traceback
                                cond=None
                        else:
                            cond = cond(md)
                        if cond:
                            section = section[i+1]
                            if section:
                                section = patched_render_blocks(section,md)
                            else: section=''
                            m = 0
                            break
                        i += 2
                    if m:
                        if i == m:
                            section = patched_render_blocks(section[i],md)
                        else:
                            section = ''

                finally: md._pop()

        elif not isinstance(section, StringTypes):
            section = section(md)

        if section:
            rendered.append(section)

    l = len(rendered)
    if l == 0:
        return ''
    elif l == 1:
        return rendered[0]
    rendered = u''.join([(isinstance(r, unicode) and r or r.decode('utf8')) 
                        for r in rendered])
    return rendered

from zope.documenttemplate import pdocumenttemplate
pdocumenttemplate.render_blocks = patched_render_blocks
