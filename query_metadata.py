import sys
import codecs
import re
import mutagen

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

fields = ['title', 'tracknumber', 'artist', 'album', 'date', 'label', 'genre', 'cddb']

def cleanTrackNumber(numString):
	match = re.search("^[0-9]+", str(numString))
	try:
		return match.group()
	except AttributeError:
		return None

def getData():
	try:
		path = sys.argv[1]
	except:
		print "usage: python2 query_metadata.py <filename>"
		sys.exit()

	try:
		metadata = mutagen.File(path, easy=True)
	except:
		print "file \"", path, "\" doesn't exist."
		sys.exit()

	return metadata

md = getData()
fields = populateFields(fields, md)

for f in fields:
	try:
		print md[f][0], u'\t',
	except KeyError:
		print u'', u'\t',
print

#print "%s\t%s\t%s\t%s\t%s\t%s" % (md['artist'][0], md['album'][0], md['date'][0], "", md['genre'][0], md['cddb'][0])
#print md['artist'][0], "\t", md['album'][0], "\t", md['date'][0], "\t", "", "\t", md['genre'][0], "\t", md['cddb'][0]
