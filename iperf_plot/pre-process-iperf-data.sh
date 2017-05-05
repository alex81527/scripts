#!/usr/bin/env bash

USAGE="Usage: ./pre-process-iperf-data.sh row_begin row_end \
end_linenumber_before_ten_sec input_file output_file"

if [ $# -ne 5 ]; then
    echo $USAGE
    exit
fi

ROW_BEGIN=$1
ROW_END=$2
COL_1=3
COL_2=7
FIRST_TEN=$3
INPUT="$4"
OUTPUT="$5"

tail -n +"$ROW_BEGIN" "$INPUT" | head -"`expr $ROW_END + 1 - $ROW_BEGIN`" > tmp
if [ $ROW_END -le $FIRST_TEN ]; then
    head -"`expr $ROW_END + 1 - $ROW_BEGIN`" tmp | \
    awk '{print $C1, $C2}' C1="`expr $COL_1 + 1`" C2="`expr $COL_2 + 1`" | \
    grep -v received | sed s/".*-"/""/ > "$OUTPUT"
elif [ $ROW_BEGIN -le $FIRST_TEN ]; then
    head -"`expr $FIRST_TEN + 1 - $ROW_BEGIN`" tmp | \
    awk '{print $C1, $C2}' C1="`expr $COL_1 + 1`" C2="`expr $COL_2 + 1`" | \
    grep -v received | sed s/".*-"/""/ > "$OUTPUT"
   
    tail -n +"`expr $FIRST_TEN + 1 - $ROW_BEGIN + 1`" tmp | \
    awk '{print $C1, $C2}' C1="$COL_1" C2="$COL_2" | \
    grep -v received | sed s/".*-"/""/ >> "$OUTPUT"
else
    cat tmp | awk '{print $C1, $C2}' C1="$COL_1" C2="$COL_2" | \
    grep -v received | sed s/".*-"/""/ > "$OUTPUT"    
fi

rm -f tmp


 
