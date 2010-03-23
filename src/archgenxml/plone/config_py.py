import os

from zope import interface
from zope import component

from archgenxml.interfaces import IOptions
from archgenxml.plone.interfaces import IConfigPyView
from xmiparser.interfaces import IPackage
from archgenxml import utils
from zope.documenttemplate import HTML


class ConfigPyView(object):
    """A view for the toplevel config.py file

      >>> from xmiparser.xmiparser import XMIPackage
      >>> package = XMIPackage(None)
      >>> adapter = IConfigPyView(package)
      >>> from archgenxml.plone.config_py import ConfigPyView
      >>> isinstance(adapter, ConfigPyView)
      True
    """
    
    component.adapts(IPackage)
    interface.implements(IConfigPyView)

    def __init__(self, package):
        self.package = package

    def run(self, generator=None): 
        options = component.getUtility(IOptions, name='options')
        configpath = os.path.join(self.package.getFilePath(),
                                  'config.py')
        parsed_config = utils.parsePythonModule(
            options.option('targetRoot'),
            self.package.getFilePath(),
            'config.py')
        creation_permission = generator.getOption('creation_permission',
                                             self.package, None)

        if creation_permission:
            default_creation_permission = creation_permission
        else:
            default_creation_permission = options.option(
                'default_creation_permission')

        roles = []
        creation_roles = []
        for perm in generator.creation_permissions:
            if not perm[1] in roles and perm[2] is not None:
                roles.append(perm[1])
                creation_roles.append( (perm[1], perm[2]) )

        # prepare (d)TML variables
        d = {'package': self.package,
             'generator': generator,
             'builtins': __builtins__,
             'utils': utils,
             'default_creation_permission': default_creation_permission,
             'creation_permissions': generator.creation_permissions,
             'creation_roles': creation_roles,
             'parsed_config': parsed_config,
             }
        d.update(__builtins__)

        templ = generator.readTemplate(['config.pydtml'])
        dtml = HTML(templ,d)
        res = dtml()

        of = generator.makeFile(configpath)
        of.write(res.encode('utf-8'))
        of.close()


component.provideAdapter(ConfigPyView)
