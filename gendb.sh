#/bin/bash
SAVEIFS=$IFS
IFS=$(echo -en "\n\b")

function output_md {
	IFS=' '
	md=$(python2 query_metadata.py "$1")
	mb_md=$(python2 query_musicbrainz.py -n "$(echo "$md" | cut -f2)" -a \""$(echo "$md" | cut -f3)"\" -t \""$(echo "$md" | cut -f4)"\" -d \""$(echo "$md" | cut -f5)"\")
	fdb_md=$(exec ./query_freedb $(echo "$md" | cut -f8) $(echo "$md" | cut -f7) $(echo "$md" | cut -f2))
	echo "$md$mb_md$fdb_md"
}

function get_files {
	shopt -s nocasematch

	for file in $(find "$1"); do
		if [[ "$file" =~ .*\.flac$ ]] || [[ "$file" =~ .*\.mp3$ ]] ; then
			echo "$file"
		fi
	done
}


files=$(get_files "$1")
#get_files "$1"

for file in $files; do
	while : ;do
		md=$(output_md "$file")
		[[ $? == 2 ]] || break
		echo "--- 503 Error: denial of service, waiting for 5 second ---" 1>&2 && sleep 5
	done
	echo "$file	$md"
done
