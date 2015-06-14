gendb="/home/bryan/source/metadata/gendb.sh"
declare -a mydirs=("/home/bryan/music/Cyrille_Aimée_-_Live_at_Birdland" "/home/bryan/music/Miles_Davis-Kind_of_Blue")
echo ${mydirs[@]}
tmpdir="/tmp/parallel_gendb_data"

function process {
	local num_queries=0
	local max_queries=$1
	echo ${mydirs[@]}
	rm -r "$tmpdir" 2> /dev/null
	mkdir "$tmpdir"
	for d in "${mydirs[@]}"; do
		echo processing "$d" ...
		if [ $num_queries -le $max_queries ]; then
			$gendb "$d" > "$tmpdir/$num_queries" &
			let num_queries=$num_queries+1
		fi
	done
	wait
}

process 5
