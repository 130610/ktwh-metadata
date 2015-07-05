import sys
import time
import signal
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

class TimeoutError(Exception):
	def __init__(self, message="a timeout occured"):
		self.message = message
	def __str__(self):
		print repr(self.message)

def setTrackNumber(num=1):
	global tracknumber
	if (num):
		tracknumber = num
	else:
		tracknumber = 1

def setArtist(name=None):
	global artist
	artist = name

def setAlbum(name=None):
	global album
	album = name

def setDate(num=None):
	global date
	date = str(num)

options = {
	   "-n":setTrackNumber,
	   "-a":setArtist,
	   "-t":setAlbum,
	   "-d":setDate
	  }

def rateLimited(min, max, func, *args, **kargs):
	def _handle_timeout(sig, frm):
		raise TimeoutError("musicbrainz query took too long")

	signal.signal(signal.SIGALRM, _handle_timeout)
	signal.alarm(max)
	before = time.time()
	try:
		ret = func(*args, **kargs)
	except TimeoutError:
		raise
		sys.exit(4)
	finally:
		signal.alarm(0)
	elapsed = time.time() - before
	if elapsed < float(min):
		time.sleep(min - elapsed)
	return ret

def bestTag(tags):
	'''
	chooses tag from list with highest score
	tags: list of musicbrainz2.model.Tag
	return: musicbrainz2.model.Tag
	'''
	maxScore = 0
	best = None
	for tag in tags:
		if tag.count > 0:
			maxScore = tag.count
			best = tag
	return best

def makeLuceneQuery(artist, album, date):
	terms = []
	if (artist) and (artist != u''):
		terms.append(u'artist:"{}"'.format(artist))
	if (album) and (album != u''):
		terms.append(u'release:"{}"'.format(album))
	if (date) and (album != ''):
		terms.append(u'date:"{}"'.format(date))

	if (len(terms) > 0):
		ret = ""
		for term in terms:
			ret += (term + ", ")
		return ret
	else:
		return None

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
	queryString = makeLuceneQuery(artist, album, date)
	if not queryString:
		sys.stderr.write("query failed: no metadata provided\n")
		sys.exit(3)
	searchTerms = ws.ReleaseFilter(query=queryString)
	try:
		results = rateLimited(1, 10, query.getReleases, searchTerms)
	except ws.WebServiceError:
		sys.stderr.write("query failed: 503 error\n")
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
		release = rateLimited(1, 10, query.getReleaseById, results[0].release.id, releaseInclude)
	except ws.WebServiceError:
		sys.stderr.write("query failed: 503 error\n")
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
			sys.stdout.write(unicode(md[f]) + u'\t')
		except KeyError:
			sys.stdout.write(u'\t')

printFields()
