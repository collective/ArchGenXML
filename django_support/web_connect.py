import xml.dom.minidom
from urllib import urlopen
"""This Module handles variuos Internet Connection Settings for us"""



def get_dict_from_url(url, default=False):
	"""This Function is for Getting an Dict from XML on an Server (e.g. an Wiki)
	Default is an fallback"""

	dict=False

	try:
		con=urlopen(url)

		if con:
			txt=con.read()
			con.close()

			dom = xml.dom.minidom.parseString(txt)

			dict={}
			#getting Dict Data
			for node in dom.getElementsByTagName('entry'):
				id=node.getAttribute('id')

				dict[id]={}
				for key in node.attributes.keys():
					dict[id][key]=node.attributes[key]


	except IOError:
		pass

	return dict or default

def get_list_from_url(url, default=False):
	"""This Function is for Getting an Dict from XML on an Server (e.g. an Wiki)
	Default is an fallback"""
	dict=False

	try:
		con=urlopen(url)

		if con:
			txt=con.read()
			con.close()

			dom = xml.dom.minidom.parseString(txt)

			dict={}
			#getting Dict Data
			for node in dom.getElementsByTagName('entry'):
				id=node.nodeValue
	except IOError:
		pass

	return dict or default

