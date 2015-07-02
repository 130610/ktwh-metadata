import sys
import time
import codecs
import musicbrainz2.webservice as ws

UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

UTF8Reader = codecs.getreader('utf8')
sys.stdin = UTF8Reader(sys.stdin)

FIELDS = ['title', 'tracknumber', 'artist', 'album', 'date', 'label', 'genre', 'cddb', 'isrc']

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
	'''
	searches musicbrainz database for metadata based on artist, album, date,
	and tracknumber
	tracknumber: int
	artist: string or None
	album: string or None
	date: string or None
	returns: dict of metadata with keys derived from FIELDS
	'''
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

	ret = {key: None for key in FIELDS}
	ret["id"] = release.getId()
	tracks = release.getTracks()
	if (len(tracks) >= int(tracknumber)):
		track = tracks[int(tracknumber) - 1]
		ret["title"] = track.getTitle()
		isrcs = track.getISRCs()
		if (len(isrcs) > 0):
			ret["isrc"] = isrcs[0]
	ret["tracknumber"] = tracknumber
	ret["album"] = release.getTitle()
	artist = release.getArtist()
	if (artist):
		ret["artist"] = release.getArtist().getName()
	event = release.getEarliestReleaseEvent()
	if (event):
		ret["date"] = event.getDate()
		label = event.getLabel()
		if (label):
			ret["label"] = label.getName()
	ret["genre"] = bestTag(release.getTags())
	return ret

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
