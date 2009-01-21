ArchGenXML - Python/Zope/Plone code generator

  Generates Plone/Archetypes applications from UML.

  This product includes a command-line utility that can examine the
  output files of many UML editors and create a complete application.
  It supports many rich features, such as Archetypes schemas, tools
  generation, references, parent-child relationships, and more.

  It works with UML editors that can output the XMI interchange format
  (most do). It can also work with the native formats of some UML
  editors. (argouml, poseidon, for instance).

  For information on the authors and supporters, see the file CREDITS.

SVN notice

  **Warning**: svn trunk is now for the development of the 2.0
    version. The stable 1.5 is now in the 1.5 branch. The almost stable 1.6
    is in the 1.6 branch.

Supported Features

  The XMI parser/generator supports the following UML entities:

    - Classes

    - Interfaces

    - Attributes

    - Methods

    - Associations (Aggregation and Composite)

    - generation of associations using Archetypes' ReferenceEngine

    - Generalization

    - Realization

    - State-Diagrams



Requirements & Optional

  Required:

	- Python 2.4 (might work with different versions too)

  Required to run generated code

    - Plone 2.5.x

    - Plone >3.1.x <4 (prefered)

  Optional:

    - i18ndude 2.0+

      Required for translation POT file generation.

      You can find it at::

        svn co https://svn.plone.org/svn/collective/i18ndude/trunk/ i18ndude

      Then install it into your python: enter the directory and::

        python setup.py install

        Or, better, use "easy_install i18ndude" and be done with it.


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

  Optional to run generated code:

    - ATBackRef

      A field type for backreferences in Archetypes. You can download
      from http://pypi.python.org/pypi/Products.ATBackRef
      Required to use backreferences feature.

    - ATVocabularyManager 1.4+ or better trunk
    
      Dynamic ttw vocabularies:

      http://plone.org/products/atvocabularymanager

    - Relations

      Relations allows for the definition of sets of rules for validation, creation
      and lifetime of Archetypes references.

      http://plone.org/products/relations

    - remember

    - CompoundField


Quick Start

  1) See INSTALL.txt for installation instructions. This should result
     in an 'archgenxml' script somewhere in your path.

  2) Run 'archgenxml' to convert an input file to a product. For
     example::

       $ archgenxml samples/SimpleSample.xmi

     This converts the Poseidon-created UML diagrams in
     "samples/SimpleSample.xmi to a new product, ArchGenXMLSimpleSample,
     stored in the current directory.

  3) Copy the ArchGenXMLSimpleSample product directory into your Plone
     Products directory and restart Plone. ArchGenXMLSimpleSample
     should now be an installable product.

  ArchGenXML ships with some demo files in samples/test-examples.


Documentation

  A tutorial and manual is located at

    http://plone.org/documentation/manual/archgenxml2


Known Limitations

  See the file TODO.txt for information on planned work for
  ArchGenXML.


License

  This software is licensed under the General Public License.  See
  LICENSE.txt for full information.

  (c) Philipp Auersperg, phil at bluedynamics.com


