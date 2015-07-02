import sys
import codecs
import re
import mutagen

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

fields = ['title', 'tracknumber', 'artist', 'album', 'date', 'label', 'genre', 'cddb']
fieldDict = {key : None for key in fields}

def cleanTrackNumber(numString):
	'''
	removes any extra characters from track number
	numString: string of digits
	return: int
	'''
	match = re.search("^[0-9]+", str(numString))
	try:
		return match.group(0)
	except AttributeError:
		return None

def getDataOld():
	'''
	legacy support for getting path from command line
	'''
	try:
		path = sys.argv[1]
	except:
		print "usage: python2 query_metadata.py <filename>"
		sys.exit()
	metadata = mutagen.File(path, easy=True)
	return metadata

def getData(path):
	'''
	path: string
	returns: mutagen.Metadata
	'''
	return mutagen.File(path, easy=True)

def populateFields(fields, md):
	'''
	fields: dict of None value field name keys
	md: mutagen.Metadata
	returns: dict of populated field name keys (based on md)
	'''
	for f in fields:
		try:
			fields[f] = md[f][0]
		except KeyError:
			fields[f] = ""
	fields['tracknumber'] = cleanTrackNumber(fields['tracknumber'])

	return fields

def printFields():
	'''
	legacy support for gendb.sh (call python scripts from bash script)
	'''
	md = getDataOld()
	fieldDict = populateFields(fieldDict, md)

	for f in fields:
		print fieldDict[f], u'\t',

# uncomment to use with gendb.sh (old method)
#printFields()
