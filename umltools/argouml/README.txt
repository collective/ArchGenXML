The archgenxml_profile.xmi file should be fed to the ArgoUML profile settings to make it aware of the Plone-related stereotypes, tagged values, etc.

For ArgoUML 0.24, to start with this profile::

    java -Dargo.defaultModel=archgenxml_profile.xmi -jar argouml.jar

For ArgoUML >= 0.26.2, add the profile via:

    Edit -> Settings -> Preferences -> Profile File

Remove the UML 1.4 profile for your created project to be sure to not use stereotypes or tagged values from it.
To generate your product, use the --profile-dir/-p option to specify the directory where xmiparser can find the profile::

    archgenxml -p /path/to/src/archgenxml/umltools/argouml/ MyProject.zargo

Don't use an old argouml_profle.xmi with ArgoUML >= 0.26.2.
Be sure to use the archgenxml_profile.xmi file
or you will have problems updating your models with a newer profile in the future.
