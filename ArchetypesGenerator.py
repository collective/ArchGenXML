#-----------------------------------------------------------------------------
# Name:        ArchetypesGenerator.py
# Purpose:     main class generating archetypes code out of an UML-model
#
# Author:      Philipp Auersperg
#
# Created:     2003/16/04
# RCS-ID:      $Id: ArchetypesGenerator.py,v 1.3 2004/05/01 21:27:26 yenzenz Exp $
# Copyright:   (c) 2003 BlueDynamics
# Licence:     GPL
#-----------------------------------------------------------------------------

import getopt, os.path, time, sys

from zipfile import ZipFile
from StringIO import StringIO
from shutil import copy

# AGX-specific imports
import XSDParser, XMIParser, PyParser
from utils import makeFile, makeDir,mapName, wrap, indent, getExpression, \
    isTGVTrue, isTGVFalse

has_i18ndude = 1    
try:
    from i18ndude import catalog as msgcatalog
except ImportError:
    has_i18ndude = 0

has_enhanced_strip_support=1
try:
    "abca".strip('a')
except:
    has_enhanced_strip_support=0

#
# Global variables etc.
#
DelayedElements = []
AlreadyGenerated = []
Force = 0       

class ArchetypesGenerator:

    force=1
    unknownTypesAsString=0
    generateActions=1
    generateDefaultActions=0
    prefix=''
    prefix=''
    packages=[] #packages to scan for classes
    noclass=0   # if set no module is reverse engineered,
                #just an empty project + skin is created
    ape_support=0 #generate ape config and serializers/gateways for APE
    method_preservation=1 #should the method bodies be preserved? defaults now to 0 will change to 1
    i18n_support=0
    build_msgcatalog=1
    striphtml=0
    
    reservedAtts=['id',]
    portal_tools=['portal_tool']
    stub_stereotypes=['odStub','stub']
    left_slots=[]
    right_slots=[]
    creation_permission=None
    detailled_creation_permissions=0
    
    parsed_class_sources={} #dict containing the parsed sources by class names (for preserving method codes)
    parsed_sources=[] #list of containing the parsed sources (for preserving method codes)
    
    nonstring_tgvs=['widget','vocabulary','required','precision'] #taggedValues that are not strings, e.g. widget or vocabulary
    
    msgcatstack = []
    
    def __init__(self,xschemaFileName,projectName=None, **kwargs):
        self.outfileName=kwargs['outfilename']

        if self.outfileName[-1] in ('/','\\'):
            self.outfileName=self.outfileName[:-1]

        path=os.path.split(self.outfileName)
        self.targetRoot=path[0]
        print 'targetRoot:',self.targetRoot
        #os.chdir(self.targetRoot or '.')
        
        if not projectName:
            if path[1]:
                self.projectName=path[1]
            else:
                #in case of trailing slash
                self.projectName=os.path.split(path[0])[1]
                
        print 'projectName:',self.projectName

        self.xschemaFileName=xschemaFileName
        self.__dict__.update(kwargs)

    ACT_TEMPL='''
           {'action':      %(action)s,
            'category':    %(action_category)s,
            'id':          '%(action_id)s',
            'name':        '%(action_label)s',
            'permissions': (%(permission)s,),
            'condition'  : '%(condition)s'},
          '''
    def makeFile(self,fn,force=1):
        ffn=os.path.join(self.targetRoot,fn)
        return makeFile(ffn,force=force)
    
    def makeDir(self,fn,force=1):
        ffn=os.path.join(self.targetRoot,fn)
        return makeDir(ffn,force=force)

    def getSkinPath(self,element):
        return os.path.join(element.getRootPackage().getFilePath(),'skins',element.getRootPackage().getName())
    
    def addMsgid(self,msgid,msgstr,element,fieldname):        
        """add a msgid to the catalog if it not exists. if it exists and not 
           listed in occurrences, then add its occurence."""
        if has_i18ndude and self.build_msgcatalog and len(self.msgcatstack):                  
            msgcat=self.msgcatstack[len(self.msgcatstack)-1]
            package=element.getPackage()
            module_id=os.path.join(element.getPackage().getFilePath(includeRoot=0),element.getName()+'.py')
            if not msgcat.has_key(msgid):
                # add new msgid
                msgcat[msgid] = (msgstr, [(module_id, [msgstr])], [])
            else:
                # check if occurrence is listed
                entry=msgcat[msgid]
                for entry_id, entry_ex in entry[1]:
                    if entry_id == module_id:
                        return
                # isnt listed, so add it
                entry[1].append((module_id, [msgstr])) 
                    
    def generateMethodActions(self,element):
        outfile=StringIO()
        print >> outfile
        for m in element.getMethodDefs():
            if m.hasStereoType( ['action','view','form']):
                action_name=m.getTaggedValue(m.getStereoType(), m.getName()).strip()
                print 'generating ' + m.getStereoType()+':',action_name
                dict={}
                
                if not action_name.startswith('string:') and not action_name.startswith('python:'):
                    action_target='string:$object_url/'+action_name
                else:
                    action_target=action_name
                    
                dict['action']=getExpression(action_target)
                dict['action_category']=getExpression(m.getTaggedValue('category','object'))
                dict['action_id']=m.getTaggedValue('id',m.getName())
                dict['action_label']=m.getTaggedValue('action_label') or m.getTaggedValue('label',m.getName()) # action_label is deprecated and for backward compability only!
                dict['permission']=getExpression(m.getTaggedValue('permission','View'))
                dict['action_id']=m.getTaggedValue('id',m.getName())

                condition=m.getTaggedValue('condition') or '1'
                dict['condition']='python:'+condition
                    
                if not isTGVFalse(m.getTaggedValue('create_action')):
                    print >>outfile, self.ACT_TEMPL % dict

            if m.hasStereoType('view'):
                f=self.makeFile(os.path.join(self.getSkinPath(element),action_name+'.pt'),0)
                if f:
                    templdir=os.path.join(sys.path[0],'templates')
                    viewTemplate=open(os.path.join(templdir,'action_view.pt')).read()
                    f.write(viewTemplate)

            elif m.hasStereoType('form'):
                f=self.makeFile(os.path.join(self.getSkinPath(element),action_name+'.cpt'),0)
                if f:
                    templdir=os.path.join(sys.path[0],'templates')
                    viewTemplate=open(os.path.join(templdir,'action_view.pt')).read()
                    f.write(viewTemplate)

        res=outfile.getvalue()
        return res

    MODIFY_FTI = """\
def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in [%(hideactions)s]:
            a['visible'] = 0
    return fti
""" 

    def generateModifyFti(self,element):
        hide_actions=element.getTaggedValue('hide_actions', '').strip()
        if not hide_actions:
            return ''
        hide_actions=', '.join(["'"+a.strip()+"'" for a in hide_actions.split('\n')])
        
        print 'hide actions: ', hide_actions
        
        return self.MODIFY_FTI % {'hideactions':hide_actions, }
        

    def generateFti(self,element,subtypes):
        ''' '''

        actTempl='''
    actions= %s (
        '''
        base_actions=element.getTaggedValue('base_actions', '').strip()
        if base_actions:
            base_actions += ' + '
            actTempl = actTempl % base_actions
        else:
            actTempl = actTempl % ''
        
        if self.generateDefaultActions or element.getTaggedValue('default_actions'):
            actTempl += '''
           {'action': 'string:${object_url}/portal_form/base_edit',
          'category': 'object',
          'id': 'edit',
          'name': 'Edit',
          'permissions': ('Manage portal content',)},

           {'action': 'string:${object_url}/base_view',
          'category': 'object',
          'id': 'view',
          'name': 'View',
          'permissions': ('View',)},

        '''
            if subtypes:
                actTempl=actTempl+'''
           {'action': 'folder_listing',
          'category': 'object',
          'id': 'folder_listing',
          'name': 'Folder Listing',
          'permissions': ('View',)},

        '''
    
        method_actions=self.generateMethodActions(element)
        actTempl +=method_actions
        actTempl+='''
          )
        '''
            
        ftiTempl='''

    # uncomment lines below when you need
    factory_type_information={
        'allowed_content_types':%(subtypes)s %(parentsubtypes)s,
        'allow_discussion': %(discussion)s,
        %(has_content_icon)s'content_icon':'%(content_icon)s',
        'immediate_view':'%(immediate_view)s',
        'global_allow':%(global_allow)d,
        'filter_content_types':%(filter_content_types)d,
        }

        '''
        if self.generateActions:
            ftiTempl += actTempl

        #collect the allowed_subtypes from the parents
        parentsubtypes=''
        if element.getGenParents():
            parentsubtypes = '+ ' + ' + '.join(tuple([p.getCleanName()+".factory_type_information['allowed_content_types']" for p in element.getGenParents()]))
        
        immediate_view=element.getTaggedValue('immediate_view') or 'base_view'

        global_allow=not element.isDependent()
        #print 'dependent:',element.isDependent(),element.getName()
        if element.hasStereoType(self.portal_tools) or element.isAbstract():
            global_allow=0

        has_content_icon=''
        content_icon=element.getTaggedValue('content_icon')
        if not content_icon:
            has_content_icon='#'
            content_icon = element.getCleanName()+'.gif'

        res=ftiTempl % {'subtypes':repr(tuple(subtypes)),
            'has_content_icon':has_content_icon,'content_icon':content_icon,
            'discussion':element.getTaggedValue('allow_discussion','0'),
            'parentsubtypes':parentsubtypes,'global_allow':global_allow,'immediate_view':immediate_view,
            'filter_content_types': not isTGVFalse(element.getTaggedValue('filter_content_types'))}

        return res

    # TypeMap for Fields, format is 
    #   type: {field: 'Y',
    #          lines: [key1=value1,key2=value2, ...]
    #   ...
    #   } 
    typeMap= {
        'string': {
            'field': 'StringField',
            'map': {},
        },
        'text':  {
            'field': 'TextField',
            'map': {},
        },
        'richtext':  {
            'field': 'TextField',
            'map': {
                'default_output_type':'text/html',
                'allowable_content_types': "('text/plain','text/structured','text/html','application/msword',)",
            },
        },
        'integer': {
            'field': 'IntegerField',
            'map': {},
        },
        'float': {
            'field': 'FloatField',
            'map': {},
        },
        'fixedpoint': {
            'field': 'FixedPointField',
            'map': {},
        },
        'lines': {
            'field': 'LinesField',
            'map': {},
        },
        'date': {
            'field': 'DateTimeField',
            'map': {},
        },
        'image': {
            'field': 'ImageField',
            'map': {
                'storage':'AttributeStorage()',
            },
        },
        'file': {
            'field': 'FileField',
            'map': {
                'storage':'AttributeStorage()',
            },
        },
        'reference': {
            'field': 'ReferenceField',
            'map': {},
        },
        'boolean': {
            'field': 'BooleanField',
            'map': {},
        },
        'computed': {
            'field': 'ComputedField',
            'map': {},
        },
        'photo': {
            'field': 'PhotoField',
            'map': {},
        },
        'generic': {
            'field': '%(type)sField',
            'map': {},
        },
    }

    widgetMap={
        'fixedpoint': 'DecimalWidget' ,
        'float': 'DecimalWidget' ,
        'text': 'TextAreaWidget' ,
        'richtext': 'RichWidget' ,
        'file': 'FileWidget',
        'date' : 'CalendarWidget'
    }

    coerceMap={
        'xs:string':'string',
        'xs:int':'integer',
        'xs:integer':'integer',
        'xs:byte':'integer',
        'xs:double':'float',
        'xs:float':'float',
        'xs:boolean':'boolean',
        'ofs.image':'image',
        'ofs.file':'file',
        'xs:date':'date',
        'datetime':'date',
        'list':'lines',
        'liste':'lines',
        'image':'image',
        'int':'integer',
        'bool':'boolean',
        'dict':'string',
        'String':'string',
        '':'string',     #
        None:'string',
    }

    def coerceType(self, typename):
        #print 'coerceType:',typename,
        typename=typename.lower()
        if typename in self.typeMap.keys():
            return typename

        if self.unknownTypesAsString:
            ctype=self.coerceMap.get(typename.lower(),'string')
        else:
            ctype=self.coerceMap.get(typename.lower(),None)
            if not ctype:
                return 'generic' #raise ValueError,'Warning: unknown datatype : >%s< (use the option --unknown-types-as-string to force unknown types to be converted to string' % typename

        #print ctype
        return ctype

    def getFieldAttributes(self,element):
        ''' converts the tagged values of a field into extended attributes for the archetypes field '''
        noparams=['documentation','element.uuid','transient','volatile','widget']
        convtostring=['expression']
        map={}
        tgv=element.getTaggedValues()
        for k in tgv.keys():
            if k not in noparams and not k.startswith('widget:'):
                v=tgv[k]
                if k not in self.nonstring_tgvs:
                    v=getExpression(v)
                formatted=''
                for line in v.split('\n'):
                    formatted+=line
                map.update( {k:formatted.strip()} )
        return map
            
    def getWidget(self, type, element, fieldname, elementclass):
        """ returns either default widget, widget according to
        attributes or no widget.
        
        atributes/tgv's can be: 
            * widget and a whole widget code block or
            * widget:PARAMETER which will be rendered as a PARAMETER=value
        
        """
        tgv=element.getTaggedValues()
        widgetcode = type.capitalize()+'Widget('
        widgetmap={}
        custom = 0 #is there a custom setting for widget?
        widgetoptions=[t for t in tgv.items() if t[0].startswith('widget:')]
        
        modulename= elementclass.getPackage().getProductName()
        check_map = {
            'label':            "'%s'" % fieldname.capitalize(),
            'label_msgid':      "'%s_label_%s'" % (modulename,fieldname),
            'description_msgid':"'%s_help_%s'" % (modulename,fieldname),
            'description':      "'Enter a value for %s.'" % fieldname,
            'i18n_domain':      "'%s'" % modulename,
        }
        
        if tgv.has_key('widget'):
            # Custom widget defined in attributes
            custom=1
            formatted=''
            for line in tgv['widget'].split('\n'):
                if formatted:
                    line=indent(line.strip(),1)
                formatted+=line+'\n'
            widgetcode =  formatted
            
        elif self.widgetMap.has_key(type):
            # Standard widget for this type found in widgetMap
            custom=1
            widgetcode = self.widgetMap[type]
                    
        if ')' not in widgetcode:
            
            for tup in widgetoptions:
                key=tup[0][7:]
                val=tup[1]
                if key not in self.nonstring_tgvs:
                    val=getExpression(val)
                widgetmap.update({key:val})
                      
            if '(' not in widgetcode:
                widgetcode += '('

            ## before update the widget mapping, try to make a 
            ## better description based on the given label
            if widgetmap.has_key('label'):
                check_map['description'] = "\'Enter a value for %s.\'" % widgetmap['label'][3:-3].lower()
                
            for k in check_map:                    
                if not (k in widgetmap.keys()): # XXX check if disabled
                    widgetmap.update( {k: check_map[k]} )
            if 'label_msgid' in widgetmap.keys() and has_enhanced_strip_support:
                self.addMsgid(widgetmap['label_msgid'].strip("'"),
                    (widgetmap.has_key('label') and widgetmap['label'].strip("'")) or fieldname,
                    elementclass,
                    fieldname
                )
            if 'description_msgid' in widgetmap.keys() and has_enhanced_strip_support:
                self.addMsgid(widgetmap['description_msgid'].strip("'"),
                    (widgetmap.has_key('description') and widgetmap['description'].strip("'")) or fieldname,
                    elementclass,
                    fieldname
                )


            map_keys=widgetmap.keys()
            map_keys.sort()
            widgetcode += indent( \
                ',\n'.join(['%s=%s' % (key,widgetmap[key]) for key in map_keys]),
                1,
                skipFirstRow=1) \
                + ',\n'        
            widgetcode +=')'
                
        return widgetcode

    def getFieldFormatted(self,name,fieldtype,map={},doc=None,indent_level=0):
        ''' returns the formatted field definitions for the schema '''
        res = ''
        # add comment
        if doc:
            res+=indent(doc,indent_level,'#')+'\n'+res        
        res+=indent("%s('%s',\n" % (fieldtype,name), indent_level)
        map_keys=map.keys()
        map_keys.sort()
        res+=indent(',\n'.join(['%s=%s' % (key,map[key]) for key in map_keys]),indent_level+1) + ',\n'        
        res+=indent('),\n',indent_level)
        
        return res
    
    def getFieldString(self, element, classelement):
        ''' gets the schema field code '''
        typename=str(element.type)

        if element.getMaxOccurs()>1:
            ctype='lines'
        else:
            ctype=self.coerceType(typename)

        res=self.getFieldFormatted(element.getCleanName(),
            self.typeMap[ctype]['field'].copy(), 
            self.typeMap[ctype]['map'].copy() )

        return res

    def getFieldStringFromAttribute(self, attr, classelement):
        ''' gets the schema field code '''
        #print 'typename:%s:'%attr.getName(),attr.type,
        if not hasattr(attr,'type') or attr.type=='NoneType':
            ctype='string'
        else:
            ctype=self.coerceType(str(attr.type))

        if ctype != 'generic':
            atype=attr.getType()
            if self.i18n_support and attr.isI18N():
                atype='I18N'+atype
        else:
            atype=attr.getType().lower().capitalize()
            
        map=self.typeMap[ctype]['map'].copy()
        if attr.hasDefault():
            map.update( {'default':attr.getDefault()} )       
        map.update(self.getFieldAttributes(attr))
        map.update( {
            'widget': self.getWidget( \
                ctype, 
                attr, 
                attr.getName(),
                classelement )
        } )
            
        doc=attr.getDocumentation(striphtml=self.striphtml)                
        res=self.getFieldFormatted(attr.getName(),
            self.typeMap[ctype]['field'],
            map,
            doc )
        
        return res

    def getFieldStringFromAssociation(self, rel, classelement):
        ''' gets the schema field code '''
        multiValued=0
        map=self.typeMap['reference']['map'].copy()
        obj=rel.toEnd.obj
        name=rel.toEnd.getName()
        relname=rel.getName()
        field=rel.getTaggedValue('reference_field') or self.typeMap['reference']['field'] #the relation can override the field
        field=rel.toEnd.getTaggedValue('reference_field') or self.typeMap['reference']['field'] #the relation can override the field

        if obj.isAbstract():
            allowed_types= tuple(obj.getGenChildrenNames())
        else:
            allowed_types=(obj.getName(), ) + tuple(obj.getGenChildrenNames())

        if int(rel.toEnd.mult[1]) == -1:
            multiValued=1
        if name == None:
            name=obj.getName()+'_ref'

        map.update({
            'allowed_types': repr(allowed_types),
            'multiValued':   multiValued,
            'relationship':  "'%s'" % relname,
            }
        )
        map.update(self.getFieldAttributes(rel.toEnd))
        map.update( {'widget':self.getWidget('Reference', rel.toEnd, name, classelement)} )
        doc=rel.getDocumentation(striphtml=self.striphtml)                
        res=self.getFieldFormatted(name,field,map,doc)
        return res

    # Generate get/set/add member functions.
    def generateArcheSchema(self, outfile, element, base_schema):
        parent_schemata=[p.getCleanName()+'.schema' for p in element.getGenParents()]

        base_schema = element.getTaggedValue('base_schema', base_schema)
        if parent_schemata:
            parent_schemata_expr=' + '+' + '.join(parent_schemata)
        else:
            parent_schemata_expr=''

        if self.i18n_support and element.isI18N():
            schemastmt='    schema=I18NBaseSchema %s + Schema((' % parent_schemata_expr
        else:
            schemastmt='    schema=BaseSchema %s + Schema((' % parent_schemata_expr

        #tagged vaues for base-schema overrule
        if base_schema:
            schemastmt='    schema=%s %s + Schema((' % (base_schema, parent_schemata_expr)
            
        print >>outfile, schemastmt
        refs=[]

        for attrDef in element.getAttributeDefs():
            name = attrDef.getName()
            #if name in self.reservedAtts:
            #    continue
            mappedName = mapName(name)

            print >> outfile, indent(self.getFieldStringFromAttribute(attrDef, element),2)
        for child in element.getChildren():
            name = child.getCleanName()
            if name in self.reservedAtts:
                continue
            unmappedName = child.getUnmappedCleanName()
            if child.getRef():
                refs.append(str(child.getRef()))

            if child.isIntrinsicType():
                print >> outfile, indent(self.getFieldString(child, element),2)

        #print 'rels:',element.getName(),element.getFromAssociations()
        # and now the associations
        for rel in element.getFromAssociations():
            #print 'rel:',rel
            if 1 or rel.toEnd.mult==1: #XXX: for mult==-1 a multiselection widget must come
                name = rel.fromEnd.getName()

                if name in self.reservedAtts:
                    continue
                print >> outfile
                print >> outfile, indent(self.getFieldStringFromAssociation(rel, element),2)


        print >> outfile,'    ),'
        marshaller=element.getTaggedValue('marshaller') or element.getTaggedValue('marshall')
        if marshaller:
            print >> outfile, '    marshall='+marshaller

        print >> outfile,'    )'

    TEMPL_CONSTR_TOOL="""
    #toolconstructors have no id argument, the id is fixed
    def __init__(self):
        %s.__init__(self,'%s')
        """

    def generateMethods(self,outfile,element,mode='class'):

        print >> outfile

        print >> outfile,'    #Methods'
        
        generatedMethods=[]
        allmethnames=[m.getName() for m in element.getMethodDefs(recursive=1)]
        
        for m in element.getMethodDefs():
            self.generateMethod(outfile,m,element,mode=mode)
            allmethnames.append(m.getName())
            generatedMethods.append(m)
            
        for interface in element.getRealizationParents():
            meths=[m for m in interface.getMethodDefs(recursive=1) if m.getName() not in allmethnames]
            # i dont want to extra generate methods that are already defined in the class
            if meths:
                print >>outfile,'    #methods from Interface %s'%interface.getName()
                for m in meths:
                    self.generateMethod(outfile,m,element,mode=mode)
                    generatedMethods.append(m)
                    allmethnames.append(m.getName())

        #contains _all_ generated method names
        method_names=[m.getName() for m in generatedMethods]
        
        #if __init__ has to be generated for tools i want _not_ __init__ to be preserved
        #if it is added to method_names it wont be recognized as a manual method (hacky but works)
        if element.hasStereoType(self.portal_tools) and '__init__' not in method_names:
            method_names.append('__init__')
            
        if self.method_preservation:
            cl=self.parsed_class_sources.get(element.getName(),None)
            if cl:
                manual_methods=[mt for mt in cl.methods.values() if mt.name not in method_names]
                if manual_methods:
                    print >> outfile, '    #manually created methods\n'
                    
                for mt in manual_methods:
                    print >> outfile, mt.src
                    print >> outfile
        

    def generateMethod(self,outfile,m,klass,mode='class'):
        #ignore actions and views here because they are
        #generated separately
        if m.hasStereoType(['action','view','form']):
            return
        
        #print 'generatemethod:',m.getStereoType(),m.getName()
        if m.hasStereoType('portlet_view'):
            view_name=m.getTaggedValue('view').strip() or m.getName()
            print 'generating portlet:',view_name
            autoinstall=m.getTaggedValue('autoinstall')
            #print 'autoinstall:',autoinstall,m.getTaggedValues()
            portlet='here/%s/macros/portlet' % view_name
            #print 'portlet:',portlet
            if autoinstall=='left':
                self.left_slots.append(portlet)
            if autoinstall=='right':
                self.right_slots.append(portlet)
                
            f=self.makeFile(os.path.join(self.getSkinPath(klass),view_name+'.pt'),0)
            if f:
                templdir=os.path.join(sys.path[0],'templates')
                viewTemplate=open(os.path.join(templdir,'portlet_template.pt')).read()
                f.write(viewTemplate % {'method_name':m.getName()})
            return
            
        
        paramstr=''
        params=m.getParamExpressions()
        if params:
            paramstr=','+','.join(params)
            #print paramstr
        print >> outfile

        if mode == 'class':
            permission=getExpression(m.getTaggedValue('permission'))
            if permission:
                print >> outfile,indent("security.declareProtected(%s,'%s')" % (permission,m.getName()),1)
            
        cls=self.parsed_class_sources.get(klass.getName(),None)
        
        if cls:
            method_code=cls.methods.get(m.getName())
        else:
            #print 'method not found:',m.getName()
            method_code=None
            
        if self.method_preservation and method_code:
            #print 'preserve method:',method_code.name
            print >>outfile, method_code.src
        else:
            if mode=='class':
                print >> outfile,'    def %s(self%s):' % (m.getName(),paramstr)
            elif mode=='interface':
                print >> outfile,'    def %s(%s):' % (m.getName(),paramstr[1:])

            code=m.taggedValues.get('code','')
            doc=m.getDocumentation(striphtml=self.striphtml) 
            if doc is not None:
                print >> outfile, indent("'''\n%s\n'''" % doc ,2)
    
            if code and mode=='class':
                print >> outfile, indent('\n'+code,2)
            else:
                print >> outfile, indent('\n'+'pass',2)

        print >> outfile

    TEMPL_APE_HEADER='''
from Products.Archetypes.ApeSupport import constructGateway,constructSerializer


def ApeGateway():
    return constructGateway(%(class_name)s)

def ApeSerializer():
    return constructSerializer(%(class_name)s)

'''

    TEMPL_TOOL_HEADER='''
from Products.CMFCore.utils import UniqueObject

    '''
    def generateDependentImports(self,outfile,element):
        package=element.getPackage()
        
        parents = element.getGenParents()
        for p in parents:
            print >> outfile,'from %s import %s' % (p.getQualifiedModuleName(package),p.getName())

        reparents = element.getRealizationParents()
        for p in reparents:
            print >> outfile,'from %s import %s' % (p.getQualifiedModuleName(package),p.getName())

    def generateProtectedSection(self,outfile,element,section,ind=0):
        print >> outfile,indent(PyParser.PROTECTED_BEGIN,ind),section,'#fill in your manual code here'
        cl=self.parsed_class_sources.get(element.getName(),None)
        if cl:
            sectioncode=cl.getProtectedSection(section)
            if sectioncode:
                print >>outfile,sectioncode

        print >> outfile,indent(PyParser.PROTECTED_END,ind),section
        print >> outfile

    def generateClass(self, outfile, element, delayed):
        wrt = outfile.write
        wrt('\n')

        parentnames = [p.getCleanName() for p in element.getGenParents()]
        self.generateDependentImports(outfile,element)
        
        additionalImports=element.getTaggedValue('imports')
        self.generateProtectedSection(outfile,element,'module-header')
        
        if additionalImports:
            wrt(additionalImports)
            wrt('\n')

        refs = element.getRefs() + element.getSubtypeNames(recursive=1)

        if element.getTaggedValue('allowed_content_types'):
            refs=refs+element.getTaggedValue('allowed_content_types').split(',')
            
        #also check if the parent classes can have subobjects
        baserefs=[]
        for b in element.getGenParents():
            baserefs.extend(b.getRefs())
            baserefs.extend(b.getSubtypeNames(recursive=1))
            
        if not element.isComplex():
            return
        if element.getType() in AlreadyGenerated:
            return

        AlreadyGenerated.append(element.getType())
        name = element.getCleanName()

        wrt('\n')

        additionalParents=element.getTaggedValue('additional_parents')
        if additionalParents:
            parentnames=list(parentnames)+additionalParents.split(',')

        baseclass='BaseContent'
        baseschema='BaseSchema'            
        if refs or baserefs or isTGVTrue(element.getTaggedValue('folderish')):                
            # folderish
            baseclass='BaseFolder'
            baseschema='BaseFolderSchema'

            if self.i18n_support and element.isI18N():
                baseclass='I18NBaseFolder'
                baseschema='I18NBaseFolderSchema'

            #tagged vaues for base-schema overrule
            folder_base_class=element.getTaggedValue('base_class') or element.getTaggedValue('folder_base_class') # folder_base_class is deprecated and for backward compability only
            if folder_base_class:
                baseclass=folder_base_class
                
                        
        else:
            #contentish
            if self.i18n_support and element.isI18N():
                baseclass='I18NBaseContent'
                baseschema='I18NBaseSchema'
            
            #tagged vaues for base-schema overrule
            content_base_class=element.getTaggedValue('base_class')
            if content_base_class:
                baseclass=content_base_class        

        
        parentnames.insert(0,baseclass)
        if element.hasStereoType(self.portal_tools):
            print >>outfile,self.TEMPL_TOOL_HEADER
            parentnames.insert(0,'UniqueObject')


        parents=','.join(parentnames)
        if self.ape_support:
            print >>outfile,self.TEMPL_APE_HEADER % {'class_name':name}

        s1 = 'class %s%s(%s):\n' % (self.prefix, name, parents)

        wrt(s1)
        doc=element.getDocumentation(striphtml=self.striphtml)
        if doc:
            print >>outfile,indent("'''\n%s\n'''" % doc, 1)

        print >>outfile,indent('security = ClassSecurityInfo()',1)

        header=element.getTaggedValue('class_header')
        if header:
            print >>outfile,indent(header, 1)

        archetype_name=element.getTaggedValue('archetype_name') or element.getTaggedValue('label')
        if not archetype_name: archetype_name=name

        print >> outfile,'''    portal_type = meta_type = '%s' ''' % name
        print >> outfile,'''    archetype_name = '%s'   #this name appears in the 'add' box ''' %  archetype_name
        
        
        #handle realization parents
        reparents=element.getRealizationParents()
        if reparents:
            reparentnames=[p.getName() for p in reparents]
            
            print >> outfile
            print >> outfile, '''    __implements__ = %(baseclass_interfaces)s + (%(realizations)s,)''' % \
                {'baseclass_interfaces' : ' + '.join(["getattr(%s,'__implements__',())" % i for i in parents.split(',')]),
                 'realizations' : ','.join(reparentnames)}
        
        print >>outfile
        
        self.generateProtectedSection(outfile,element,'class-header',1)    
        self.generateArcheSchema(outfile,element,baseschema)

        if element.hasStereoType(self.portal_tools):
            tool_instance_name=element.getTaggedValue('tool_instance_name') or 'portal_'+element.getName().lower()
            print >> outfile,self.TEMPL_CONSTR_TOOL % (baseclass,tool_instance_name)
            print >> outfile

        self.generateMethods(outfile,element)

        #generateGettersAndSetters(outfile, element)
        fti=self.generateFti(element,refs)
        print >> outfile,fti 
        
        
        print >> outfile, self.generateModifyFti(element)   

        wrt('registerType(%s)\n' % name)
        wrt('# end of class %s\n\n'   % name)

        self.generateProtectedSection(outfile,element,'module-footer')

    def generateInterface(self, outfile, element, delayed):
        wrt = outfile.write
##        print 'Interface:',element.getName()
##        print 'parents:',element.getGenParents()
    
        parentnames = [p.getCleanName() for p in element.getGenParents()]

        self.generateDependentImports(outfile,element)
        
        print >> outfile,'from Interface import Base'
        
        additionalImports=element.getTaggedValue('imports')
        if additionalImports:
            wrt(additionalImports)

        refs = element.getRefs() + element.getSubtypeNames(recursive=1)

        AlreadyGenerated.append(element.getType())
        name = element.getCleanName()

        wrt('\n')

        additionalParents=element.getTaggedValue('additional_parents')
        if additionalParents:
            parentnames=list(parentnames)+additionalParents.split(',')

        if not [c for c in element.getGenParents() if c.isInterface()]:
            parentnames.insert(0,'Base')
        parents=','.join(parentnames)

        s1 = 'class %s%s(%s):\n' % (self.prefix, name, parents)

        wrt(s1)
        doc=element.getDocumentation(striphtml=self.striphtml)
        print >>outfile,indent("'''\n%s\n'''" % doc, 1)

        header=element.getTaggedValue('class_header')
        if header:
            print >>outfile,indent(header, 1)

        self.generateMethods(outfile,element,mode='interface')

        wrt('# end of class %s\n'   % name)


    MODULE_INFO_HEADER = """\
# File: %(filename)s 
\"""\\
%(purpose)s 

RCS-ID $Id: ArchetypesGenerator.py,v 1.3 2004/05/01 21:27:26 yenzenz Exp $
\"""
# %(copyright)s
#
# Generated: %(date)s 
# Generator: ArchGenXML Version %(version)s http://sf.net/projects/archetypes/
#
# %(licence)s
#
__author__  = '%(author)s <%(email)s>'
__docformat__ = 'plaintext'

"""

    GPLTEXT = """\
GNU General Public Licence (GPL)

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA"""

    def generateModuleInfoHeader(self, outfile, modulename, element): 
        if not self.module_info_header:
            return
        
        #deal with multiline docstring
        purposeline=('\n').join( \
            (element.getDocumentation(striphtml=self.striphtml,wrap=79) or 'unknown').split('\n') )
        
        author= element.getTaggedValue('author',  self.author) or 'unknown'

        copyright = "Copyright (c) %s by %s" % \
            (str(time.localtime()[0]),
             element.getTaggedValue('copyright', self.copyright) or author)
        
        licence = ('\n# ').join( \
            wrap((element.getTaggedValue('licence', self.licence) or self.GPLTEXT),77).split('\n') )

        fileheaderinfo = {'filename': modulename+'.py',
                          'purpose':  purposeline,
                          'author':   author,
                          'email':    element.getTaggedValue('email', self.email) or 'unknown',
                          'version':  self.version,
                          'date':     time.ctime(),
                          'copyright':'\n# '.join(wrap(copyright,77).split('\n')),
                          'licence':  licence,
        }        
        outfile.write(self.MODULE_INFO_HEADER % fileheaderinfo)

    def generateHeader(self, outfile, i18n=0):
        if i18n:
            s1 = self.TEMPLATE_HEADER_I18N 
        else:
            s1 = self.TEMPLATE_HEADER 
            
        outfile.write(s1)


    TEMPL_TOOLINIT='''
    tools=[%s]
    utils.ToolInit( PROJECTNAME+' Tools',
                tools = tools,
                product_name = PROJECTNAME,
                icon='tool.gif'
                ).initialize( context )'''

    TEMPL_CONFIGLET_INSTALL='''
    portal_control_panel.registerConfiglet( '%(tool_name)s' #id of your Product
        , '%(configlet_title)s' # Title of your Product
        , 'string:${portal_url}/%(configlet_url)s/'
        , '%(configlet_condition)s' # a condition
        , 'Manage portal' # access permission
        , '%(configlet_section)s' # section to which the configlet should be added: (Plone,Products,Members)
        , 1 # visibility
        , '%(tool_name)sID'
        , '%(configlet_icon)s' # icon in control_panel
        , '%(configlet_description)s'
        , None
        )
    # set title of tool:
    tool=getToolByName(self, '%(tool_instance)s')
    tool.title='%(configlet_title)s'

    # dont allow tool listed as content in navtree
    try:
        idx=self.portal_properties.navtree_properties.metaTypesNotToList.index('%(tool_name)s')
        self.portal_properties.navtree_properties._p_changed=1        
    except ValueError:
        self.portal_properties.navtree_properties.metaTypesNotToList.append('%(tool_name)s')
    except:
        raise'''

    TEMPL_CONFIGLET_UNINSTALL='''
    portal_control_panel.unregisterConfiglet('%(tool_name)s')

    # remove prodcut from navtree properties
    try:
        self.portal_properties.navtree_properties.metaTypesNotToList.remove('%(tool_name)s')
        self.portal_properties.navtree_properties._p_changed=1        
    except ValueError:
        pass
    except:
        raise'''

    def getGeneratedTools(self,package):
        ''' returns a list of  generated tools '''
        return [c for c in self.getGeneratedClasses(package) if c.hasStereoType(self.portal_tools)]

    TEMPL_DETAILLED_CREATION_PERMISSIONS='''
    # and now give it some extra permissions so that i
    # can control them on a per class limit
    for i in range(0,len(content_types)):
        perm='Add '+ capitalize(ftis[i]['id'])+'s'
        methname='add'+capitalize(ftis[i]['id'])
        meta_type = ftis[i]['meta_type']

        context.registerClass(
            meta_type=meta_type,
            constructors = (
                            getattr(locals()[meta_type],'add'+capitalize(meta_type)),
                               )
            , permission = perm
            )
'''
    def generateStdFiles(self,target,package):
        if package.isRoot():
            self.generateStdFilesForProduct(target,package)
        else:
            self.generateStdFilesForPackage(target,package)
            
    def generateStdFilesForPackage(self,target,package):
        if target[-1] in ('/','\\'):
            target=target[:-1]

        templdir=os.path.join(sys.path[0],'templates')
        initTemplate=open(os.path.join(templdir,'__init_package__.py')).read()
        imports_packages='\n'.join(['import '+m for m in package.generatedPackages])
        imports_classes='\n'.join(['import '+m for m in package.generatedModules])

        init_params = {'imports_packages':imports_packages,'imports_classes':imports_classes}
        initTemplate=initTemplate % init_params
        of=self.makeFile(os.path.join(target,'__init__.py'))
        of.write(initTemplate)
        of.close()
        

    def generateStdFilesForProduct(self, target,package):
        generatedModules=package.generatedModules
        #generates __init__.py, Extensions/Install.py and the skins directory
        #the result is a QuickInstaller installable product
        #print 'standard-files for ',package.getName()
        #remove trailing slash
        if target[-1] in ('/','\\'):
            target=target[:-1]

        templdir=os.path.join(sys.path[0],'templates')
        initTemplate=open(os.path.join(templdir,'__init__.py')).read()
        imports_packages='\n'.join(['    import '+m for m in package.generatedPackages])
        imports_classes='\n'.join(['    import '+m for m in generatedModules])

        imports=imports_packages+'\n\n'+imports_classes
        tool_classes=self.getGeneratedTools(package)

        if tool_classes:
            toolinit=self.TEMPL_TOOLINIT % ','.join([c.getQualifiedName(package) for c in self.getGeneratedClasses(package) if c.hasStereoType(self.portal_tools)])
        else: toolinit=''

        add_content_permission = self.creation_permission or 'Add %s content' % package.getProductName()
        init_params={'project_name':package.getProductName(),'add_content_permission': getExpression(add_content_permission),'imports':imports, 'toolinit':toolinit }

        if self.detailled_creation_permissions:
            init_params['extra_perms']=self.TEMPL_DETAILLED_CREATION_PERMISSIONS
        else:
            init_params['extra_perms']=""

        initTemplate=initTemplate % init_params
        of=self.makeFile(os.path.join(package.getFilePath(),'__init__.py'))
        of.write(initTemplate)
        of.close()

        installTemplate=open(os.path.join(templdir,'Install.py')).read()
        extDir=os.path.join(package.getFilePath(),'Extensions')
        self.makeDir(extDir)
        of=self.makeFile(os.path.join(extDir,'Install.py'))

        #handling of hide_folder_tabs
        hide_folder_tabs=''
        for c in [cn for cn in self.getGeneratedClasses(package) if cn.getTaggedValue('hide_folder_tabs',None)]:
            hide_folder_tabs+="'"+c.getName()+"', "

        #handling of tools
        autoinstall_tools=[c.getName() for c in self.getGeneratedClasses(package) if c.hasStereoType(self.portal_tools) and isTGVTrue(c.getTaggedValue('autoinstall')) ]

        if self.getGeneratedTools(package):
            copy(os.path.join(templdir,'tool.gif'), os.path.join(self.targetRoot,package.getFilePath(),'tool.gif') )

        #handling of tools with configlets
        register_configlets='#auto build\n'
        unregister_configlets='#auto build\n'
        for c in [cn for cn in self.getGeneratedClasses(package)
                            if cn.hasStereoType(self.portal_tools) and
                               isTGVTrue(cn.getTaggedValue('autoinstall','0') ) and
                               cn.getTaggedValue('configlet', None)
                 ]:
            configlet_title=    c.getTaggedValue('configlet_title',c.getName())
            configlet_section=  c.getTaggedValue('configlet_section', 'Products')
            if not configlet_section in ['Plone','Products','Members']:
                configlet_section='Products'

            configlet_condition=c.getTaggedValue('configlet_condition','')
            configlet_icon=     c.getTaggedValue('configlet_icon','site_icon.gif')
            configlet_view=     '/'+c.getTaggedValue('configlet_view')
            configlet_descr=    c.getTaggedValue('configlet_description',
                                                 'ArchGenXML generated Configlet "'+configlet_title+'" in Tool "'+c.getName()+'".')

            tool_instance_name = c.getTaggedValue('tool_instance_name', 'portal_'+ c.getName().lower() )
            register_configlets+=self.TEMPL_CONFIGLET_INSTALL % {
                'tool_name':c.getName(),
                'tool_instance': tool_instance_name,
                'configlet_title':configlet_title,
                'configlet_url':tool_instance_name+configlet_view,
                'configlet_condition':configlet_condition,
                'configlet_section':configlet_section,
                'configlet_icon':configlet_icon,
                'configlet_description':configlet_descr,
                } + '\n'

            unregister_configlets+=self.TEMPL_CONFIGLET_UNINSTALL % {
                'tool_name':c.getName()
                } + '\n'

        of.write(installTemplate % {'project_dir':package.getProductName(),
                                    'no_use_of_folder_tabs':'['+hide_folder_tabs+']',
                                    'autoinstall_tools':repr(autoinstall_tools),
                                    'register_configlets':register_configlets,
                                    'unregister_configlets':unregister_configlets,
                                    'left_slots':repr(self.left_slots),
                                    'right_slots':repr(self.right_slots)
                                   })
        of.close()
        
    TEMPL_APECONFIG_BEGIN='''<?xml version="1.0"?>

<!-- Basic Zope 2 configuration for Ape. -->

<configuration>'''
    def generateApeConf(self, target,package):
        #generates apeconf.xml

        #remove trailing slash
        if target[-1] in ('/','\\'):
            target=target[:-1]

        templdir=os.path.join(sys.path[0],'templates')
        apeconfig_object=open(os.path.join(templdir,'apeconf_object.xml')).read()
        apeconfig_folder=open(os.path.join(templdir,'apeconf_folder.xml')).read()

        of=self.makeFile(os.path.join(target,'apeconf.xml'))
        print >> of,self.TEMPL_APECONFIG_BEGIN
        for el in self.root.getClasses():
            if el.isInternal() or el.hasStereoType(self.stub_stereotypes):
                continue

            print >>of
            if el.getRefs() + el.getSubtypeNames(recursive=1):
                print >>of,apeconfig_folder % {'project_name':package.getProductName(),'class_name':el.getCleanName()}
            else:
                print >>of,apeconfig_object % {'project_name':package.getProductName(),'class_name':el.getCleanName()}

        print >>of,'</configuration>'
        of.close()

    def getGeneratedClasses(self,package):
        classes=package.generatedClasses
        for p in package.getPackages():
            if not p.isProduct():
                classes.extend(self.getGeneratedClasses(p))
            
        res=[]
        for c in classes:
            if c not in res:
                res.append(c)
                
        return res
    
    def generatePackage(self,package,recursive=1):
        package.generatedModules=[]
        package.generatedClasses=[]
        if package.getName() == 'java':
            #to suppress these unneccesary implicit created java packages (ArcgoUML and Poseidon)
            return
        
        self.makeDir(package.getFilePath())
        
        for element in package.getClasses()+package.getInterfaces():
            #skip stub and internal classes
            if element.isInternal() or element.hasStereoType(self.stub_stereotypes):
                continue

            module=element.getName()
            package.generatedModules.append(module)
            outfilepath=os.path.join(package.getFilePath(),module+'.py')
            #print 'writing class:',outfilepath
            
            if self.method_preservation:
                try:
                    #print 'existing sources found for:',element.getName(),outfilepath
                    mod=PyParser.PyModule(os.path.join(self.targetRoot,outfilepath))
                    #mod.printit()
                    self.parsed_sources.append(mod)
                    for c in mod.classes.values():
                        #print 'found class:',c.name
                        self.parsed_class_sources[c.name]=c
                    
                except IOError:
                    #print 'no source found'
                    pass
                except :
                    print
                    print '***'
                    print '***Error while reparsing the file '+outfilepath
                    print '***'
                    print
                    
                    raise

            try:
                outfile=StringIO()
                self.generateModuleInfoHeader(outfile, module, element)
                if not element.isInterface():
                    self.generateHeader(outfile, i18n=self.i18n_support and element.isI18N()) 
                    self.generateClass(outfile, element, 0)
                    package.generatedClasses.append(element)
                else:
                    self.generateInterface(outfile,element,0)
                
                
                classfile=self.makeFile(outfilepath)
                buf=outfile.getvalue()
                print >> classfile,buf
                classfile.close()
            except:
                #roll back the changes
                # and dont swallow the exception    
                raise
        
        #generate subpackages
        package.generatedPackages=[]
        for p in package.getPackages():
            #print 'generating package:',p.getName()
            #print '================================'
            if p.isProduct():
                print
                print 'generating product:',p.getName()
                print '-------------------------'
                self.generateProduct(p)
            else:
                self.generatePackage(p,recursive=1)
                package.generatedPackages.append(p.getName())

        self.generateStdFiles(package.getFilePath(),package)

    def generateProduct(self, root, ):
        dirMode=0
        outfile=None

        dirMode=1
        
        READMEHIGHEST = """\
Directory 'skins/%s_public':

This skin layer has highest priority, put templates and scripts here that are 
supposed to overload existing ones. 

I.e. if you want to change want a site-wide change of Archetypes skins 
base_edit, base_view, etc or also Plone skins like main_template or 
document_view, put it in here."""
        
        READMELOWEST = """\
Directory 'skins/%s':

This skin layer has low priority, put unique templates and scripts here.

I.e. if you to want to create own unique views or forms for your product, this 
is the right place."""


        #create the directories
        self.makeDir(root.getFilePath())
        self.makeDir(os.path.join(root.getFilePath(),'skins'))
        self.makeDir(os.path.join(root.getFilePath(),'skins',
            root.getProductName()))
        self.makeDir(os.path.join(root.getFilePath(),'skins',
            root.getProductName()+'_public'))

        of=self.makeFile(os.path.join(root.getFilePath(),'skins',
            root.getProductName()+'_public','readme.txt')
        )
        print >> of, READMEHIGHEST % root.getProductName()
        of.close()

        of=self.makeFile(os.path.join(root.getFilePath(),'skins',
                                root.getProductName(),'readme.txt'))
        print >> of, READMELOWEST % root.getProductName()
        of.close()

        # prepare messagecatalog
        if has_i18ndude and self.build_msgcatalog:
            self.makeDir(os.path.join(root.getFilePath(),'i18n'))
            filepath=os.path.join(root.getFilePath(),'i18n','generated.pot')
            if not os.path.exists(filepath):
                templdir=os.path.join(sys.path[0],'templates')
                PotTemplate = open(os.path.join(sys.path[0],'templates','generated.pot')).read()
                PotTemplate = PotTemplate % {
                    'author':self.author or 'unknown author',
                    'email':self.email or 'unknown@email.address',
                    'year': str(time.localtime()[0]),
                    'datetime': time.ctime(),
                    'charset':sys.getdefaultencoding(),
                    'package': root.getProductName(),
                }
                of=self.makeFile(filepath)                
                of.write(PotTemplate)
                of.close()
            self.msgcatstack.append(msgcatalog.MessageCatalog( filename=filepath ))
                
        
        package=root

        self.generatePackage(root)

        if self.ape_support:
            self.generateApeConf(root.getFilePath(),root)

        # write messagecatalog
        if has_i18ndude and self.build_msgcatalog:
            filepath=os.path.join(root.getFilePath(),'i18n','generated.pot')
            of=self.makeFile(filepath) or open(filepath,'w')
            pow=msgcatalog.POWriter(of,self.msgcatstack.pop() )
            pow.write()
            of.close()
            

    def parseAndGenerate(self):
        
        # and now start off with the class files
        self.generatedModules=[]

        suff=os.path.splitext(self.xschemaFileName)[1].lower()
        print 'Parsing...'
        print '==============='
        if not self.noclass:
            if suff.lower() in ('.xmi','.xml'):
                print 'opening xmi'
                self.root=root=XMIParser.parse(self.xschemaFileName,packages=self.packages)
            elif suff.lower() in ('.zargo','.zuml'):
                print 'opening zargo'
                zf=ZipFile(self.xschemaFileName)
                xmis=[n for n in zf.namelist() if os.path.splitext(n)[1].lower()=='.xmi']
                assert(len(xmis)==1)
                buf=zf.read(xmis[0])
                self.root=root=XMIParser.parse(xschema=buf,packages=self.packages)
            elif suff.lower() == '.xsd':
                self.root=root=XSDParser.parse(self.xschemaFileName)
            else:
                raise TypeError,'input file not of type .xsd, .xmi, .xml, .zargo, .zuml'

            if self.outfileName:
                root.setName(os.path.split(self.outfileName)[1])

            print 'outfile:',self.outfileName
        else:
            self.root=root=XMIParser.XMIElement() #create empty element

        print 'Generating...'
        print '=============='
        if self.method_preservation:
            print 'method bodies will be preserved'
        else:
            print 'method bodies will be overwritten'
        if not has_enhanced_strip_support:
            print "Warning: Can't build message catalog. Needs 'python 2.3' or later."
        if self.build_msgcatalog and not has_i18ndude:
            print "Warning: Can't build message catalog. Module 'i18ndude' not found."
        if not XMIParser.has_stripogram:
            print "Warning: Can't strip html from doc-strings. Module 'stripogram' not found."
            
        self.generateProduct(root)
    
    TEMPLATE_HEADER = """\
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *

    """

    TEMPLATE_HEADER_I18N = """\
from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *
from Products.I18NArchetypes.public import *

    """
