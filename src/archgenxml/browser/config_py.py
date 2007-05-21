import os

from zope import interface
from zope import component

from archgenxml.browser.interfaces import IConfigPyView
from archgenxml.interfaces import uml
from archgenxml import utils
from archgenxml.documenttemplate.documenttemplate import HTML


class ConfigPyView(object):
    """A view for the toplevel config.py file
    """
    
    component.adapts(uml.IPackage)
    interface.implements(IConfigPyView)

    def __init__(self, package):
        self.package = package

    def run(self, generator=None): 
        configpath = os.path.join(self.package.getFilePath(),
                                  'config.py')
        parsed_config = utils.parsePythonModule(
            generator.targetRoot,
            self.package.getFilePath(),
            'config.py')
        creation_permission = generator.getOption('creation_permission',
                                             self.package, None)

        if creation_permission:
            default_creation_permission = creation_permission
        else:
            default_creation_permission = generator.default_creation_permission

        roles = []
        creation_roles = []
        for perm in generator.creation_permissions:
            if not perm[1] in roles and perm[2] is not None:
                roles.append(perm[1])
                creation_roles.append( (perm[1], perm[2]) )

        # prepare (d)TML varibles
        d={'package': self.package,
           'generator': generator,
           'builtins': __builtins__,
           'utils': utils,
           'default_creation_permission': default_creation_permission,
           'creation_permissions': generator.creation_permissions,
           'creation_roles': creation_roles,
           'parsed_config': parsed_config,
           }
        d.update(__builtins__)

        templ=generator.readTemplate('config.py')
        dtml=HTML(templ,d)
        res=dtml()

        of=generator.makeFile(configpath)
        of.write(res)
        of.close()


component.provideAdapter(ConfigPyView)
