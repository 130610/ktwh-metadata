#/bin/bash
tmp_file="/tmp/ktwh-tmp.txt"
SAVEIFS=$IFS
IFS=$(echo -en "\n\b")

function output_md {
	IFS=' '
	md=$(python2 queryMetadata.py "$1")
	mb_md=$(python2 queryMusicbrainz.py -n "$(echo "$md" | cut -f2)" -a "$(echo "$md" | cut -f3)" -t "$(echo "$md" | cut -f4)" -d "$(echo "$md" | cut -f5)")
	ret=$?
	#fdb_md=$(exec timeout .2 ./query_freedb $(echo "$md" | cut -f8) $(echo "$md" | cut -f7) $(echo "$md" | cut -f2))
	fdb_md=""
	if [[ -z "$fdb_md" ]]; then
		fdb_md="$(echo -e "\t\t\t\t\t\t")"
	fi
	echo "$md$mb_md$fdb_md"
	return $ret
}

function get_files {
	shopt -s nocasematch

	for file in $(find "$1"); do
		if ( [[ "$file" =~ .*\.flac$ ]] ||\
		   [[ "$file" =~ .*\.mp3$ ]] ) &&\
		   [[ "$(basename "$file")" =~ ^[^\.][^_-].*$ ]]; then
			echo "$file"
		fi
	done
}

get_files "$1" > $tmp_file
sort $tmp_file -o $tmp_file

for file in $(cat $tmp_file); do
	count=1
	while [[ $count < 5 ]] ; do
		let "count++"
		md=$(output_md "$file")
		[[ $? == 2 ]] || break
		echo "--- 503 Error: denial of service, waiting for 5 seconds ---" 1>&2 && sleep 5
	done
	echo "$file	$md"
done
