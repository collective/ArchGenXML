ArchGenXML

  Generates Plone/Archetypes applications from UML.

  This product includes a command-line utility that can examine the
  output files of many UML editors and create a complete application.
  It supports many rich features, such as Archetypes schemas, tools
  generation, references, parent-child relationships, and more.

  It works with UML editors that can output the XMI interchange format
  (most do). It can also work with the native formats of some UML
  editors.

  In addition, it can generate applications from XSD (XMLSchema)
  files, though this format is less expressive than XMI from UML.

  For information on the authors and supporters, see the file CREDITS.


Supported Features

  The XMI parser/generator supports the following UML entities:

    - Classes
    
    - Attributes

    - Methods

    - Associations (Aggregation and Composite)

    - generation of associations using Archetypes' ReferenceEngine

    - Generalization

    - State-Diagrams


UML Editors

  ObjectDomain (commercial, free demo for <= 30 classes)
    
    www.objectdomain.com
    
    ObjectDomain can export its diagrams in XMI. At this time,
    ObjectDomain's workflow diagrams cannot be turned into workflow by
    the tool, however class creation works fine.

  ArgoUML   (free and Open Source)
    
    argouml.tigris.org

    ArgoUML stores the model natively as XMI, along with diagram
    information. This file format, a .zargo file, is just a zip with
    these two files in it. It uses XMI version 1.0.

  Poseidon  (commercial, based on ArgoUML)

    www.gentleware.com

    Poseidon uses .zargo files, as ArgoUML does. It uses XMI version
    1.2.

    There is a Community Edition of Poseidon, which is free to use,
    but not Open Source.

  Sybase Powerdesigner (commercial, demo download)

    www.sybase.com

    Supports model export as XMI (XMI version 1.1).

  Umbrello  (free and Open Source)

    www.umbrello.org

    Umbrello is a native KDE application for creating UML. It stores
    the model natively in XMI.

    As of Umbrello 1.3.2, the XMI generated is not standards
    compliant, and cannot be used with ArchGenXML. This may be changed
    in version 1.4 or later of Umbrello.


Requirements & Optional

  Required:
  
    - PyXML

      An XML parser for Python. 

      You can find it at:

        http://pyxml.sourceforge.net/

      Then, unpack the PyXML archive and enter the directory,   
      the regular Distutils commands should work::

        python setup.py build
        python setup.py install

  Optional:

    - i18ndude

      Required for translation POT file generation.

      You can find it at::

        cvs -d:pserver:anonymous@cvs.sourceforge.net:/cvsroot/plone-i18n login
        cvs -z3 -d:pserver:anonymous@cvs.sourceforge.net:/cvsroot/plone-i18n \
            co i18ndude

      Then install it into your python: enter the directory and::
   
        python setup.py install

    - ATBackRef

      A field type for backreferences in Archetypes. You can download
      from http://cvs.bluedynamics.org/viewcvs/ATBackRef/. Required to
      use backreferences feature.

    - stripogram

      A tool to remove HTML tags from strings.

      Some UML editors (most notably, Poseidon) create documentation
      with embedded HTML tags. This may be useful for creating
      documentation within their tools, but is not helpful for actual
      product creation. If stripogram is installed and "strip-html"
      option is chosen, these will be removed.

      You can find this at:

        http://sourceforge.net/project/showfiles.php?group_id=1083&package_id=34645

    and install it into your python: unpack it, enter the directory
    and::

        python setup.py install


Quick Start

  1) Unpack the ArchGenXML product. It is not actually a product for
     Zope, but is run directly from the command line. Therefore, it
     does not have to be installed in your $INSTANCE_HOME/Products.

  2) Use the ArchGenXML.py script to convert an input file to a
     product. For example::

       $ ./ArchGenXML.py -o Outline samples/test-examples/outline.zargo

     This converts the Poseidon-created UML diagrams in
     "outline.zargo" to a new product, Outline, stored in the current
     directory.

  3) Copy the Outline product directory into your Plone Products
     directory and restart Plone. Outline should now be an installable
     product.

  ArchGenXML ships with many demo files in samples/test-examples.
  There is a script there, mkdemo, which makes several products from
  the sample UML/XSD files.



Additional Documentation

  See the docs directory for reference information. A tutorial is
  being created at
  
    http://plone.org/documentation/tutorial/archgenxml-getting-started/view?searchterm=archgenxml
  



Known Limitations

  The XSD Parser is just a design study, and should be overhauled.

  See the file TODO.txt for information on planned work for
  ArchGenXML.


License

  This is licensed under the General Public License. See LICENSE.txt
  for full information.

  (c) Philipp Auersperg, phil at bluedynamics.com


