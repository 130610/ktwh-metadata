import sys
import musicbrainz2.webservice
import audiotools

filePath = sys.argv[1]

track = audiotools.open(filePath)
metadata = track.get_metadata()
print metadata.album_name
print metadata.artist_name

q = musicbrainz2.webservice.Query()
filt = musicbrainz2.webservice.ReleaseFilter(title=metadata.album_name, artistName=metadata.artist_name)
results = q.getReleases(filt)
releaseInclude = musicbrainz2.webservice.ReleaseIncludes(artist=True, releaseEvents=True, tracks=True, labels=True)
release = q.getReleaseById(results[0].release.id, releaseInclude)


print results[0].release.id, '\t', release.title, '\t', release.artist.name, '\t', release.releaseEvents[0].date, '\t', release.releaseEvents[0].label.name
