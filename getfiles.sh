SAVEIFS=$IFS
IFS=$(echo -en "\n\b")

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

get_files "$1" > "$2"
sort "$2" -o "$2"
