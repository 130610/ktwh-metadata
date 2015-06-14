import sys
import codecs
import mutagen

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

fields = ['artist', 'album', 'date', 'label', 'genre', 'cddb']

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

for f in fields:
	try:
		print md[f][0], u'\t',
	except KeyError:
		print u'', u'\t',
print

#print "%s\t%s\t%s\t%s\t%s\t%s" % (md['artist'][0], md['album'][0], md['date'][0], "", md['genre'][0], md['cddb'][0])
#print md['artist'][0], "\t", md['album'][0], "\t", md['date'][0], "\t", "", "\t", md['genre'][0], "\t", md['cddb'][0]
