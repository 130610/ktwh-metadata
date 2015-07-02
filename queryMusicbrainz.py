import sys
import time
import codecs
import musicbrainz2.webservice as ws

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

UTF8Reader = codecs.getreader('utf8')
sys.stdin = UTF8Reader(sys.stdin)

fields = ['title', 'tracknumber', 'artist', 'album', 'date', 'label', 'genre', 'cddb']
fieldDict = {key: None for key in fields}

# default values
tracknumber = 1
artist = None
album = None
date = None

def setTrackNumber(num=1):
	global tracknumber
	tracknumber=num
	return 1

def setArtist(name=None):
	global artist
	artist = u"artist:" + name
	return 1

def setAlbum(name=None):
	global album
	album = u"release:" + name
	return 1

def setDate(num=None):
	global date
	date = u"date:" + str(num)
	return 1

options = {
	   "-n":setTrackNumber,
	   "-a":setArtist,
	   "-t":setAlbum,
	   "-d":setDate
	  }

def rateLimited(minimum, func, *args, **kargs):
	before = time.time()
	ret = func(*args, **kargs)
	elapsed = time.time() - before
	if elapsed < float(minimum):
		time.sleep(minimum - elapsed)
	return ret

def bestTag(tags):
	'''
	chooses tag from list with highest score
	tags: list of musicbrainz2.model.Tag
	return: musicbrainz2.model.Tag"
	'''
	maxScore = 0
	best = None
	for tag in tags:
		if tag.count > 0:
			maxScore = tag.count
			best = tag
	return best

def search(tracknumber=1, artist=None, album=None, date=None):
	query = ws.Query()
	searchTerms = ws.ReleaseFilter(title=album, artistName=artist, query=date)
	try:
		results = rateLimited(1.0, query.getReleases, searchTerms)
	except:
		print "query failed" >> sys.stderr
		sys.exit(2)
	releaseInclude = ws.ReleaseIncludes(artist=True,
	                                    counts=True,
	                                    releaseEvents=True,
	                                    discs=True, 
	                                    tracks=True, 
	                                    artistRelations=True, 
	                                    releaseRelations=True, 
	                                    trackRelations=True, 
	                                    urlRelations=True, 
	                                    labels=True, 
	                                    tags=True, 
	                                    isrcs=True, 
	                                    releaseGroup=True)
	try:
		release = rateLimited(1.0, query.getReleaseById, results[0].release.id, releaseInclude)
	except:
		print "query failed" >> sys.stderr
		sys.exit(2)


	try:
		Id = release.id
	except AttributeError:
		Id = None
	try:
		Track = release.tracks[int(tracknumber) - 1].title
	except:
		Track = None
	try:
		Title = release.title
	except:
		Title = None
	try:
		Artist = release.artist.name
	except AttributeError:
		Artist = None
	try:
		Date = release.releaseEvents[0].date
	except AttributeError:
		Date = None
	except IndexError:
		Date = None
	try:
		Label = release.releaseEvents[0].label.name
	except AttributeError:
		Label = None
	except IndexError:
		Label = None
	try:
		Genre = bestTag(release.tags)
	except AttributeError:
		Genre = None
	return {
		"title":Track,
		"id":Id,
		"album":Title,
		"artist":Artist,
		"date":Date,
		"label":Label,
		"genre":Genre
	}
def parseOptions():
	'''
	legacy feature to parse command line options from gendb.sh
	'''
	for i in range(len(sys.argv)):
		if sys.argv[i] in options:
			options[sys.argv[i]](unicode(sys.argv[i+1], 'utf-8'))

def printFields():
	'''
	legacy/debugging function to directly print data from musicbrainz
	'''
	parseOptions()
	md = search(tracknumber, artist, album, date)
	for f in FIELDS:
		try:
			print md[f], '\t',
		except KeyError:
			print '', '\t',

printFields()
