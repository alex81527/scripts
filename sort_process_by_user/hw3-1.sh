ps -aux | sed -e '1d' | awk '{ print $1"\t"$2"\t"$8}' | sort -n -k 2,2 | \
sort -s -k 3,3 | sort -s -k 1,1 | awk -f "hw3-1.awk"
