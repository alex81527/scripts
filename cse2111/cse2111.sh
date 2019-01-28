#!/usr/bin/env bash

author="Author: Wei-Han Chen, PhD student\n"\
"Co-Sy-Ne Communication Systems and Networking group\n"\
"Dept. of Computer Science and Engineering\n"\
"The Ohio State University\n"\
"Sun Jan 27 18:08:28 EST 2019"


# Parameters
##############################################################################
# grader list
graderA="Reagan(section A)"
graderB="Junboem(section B)"
graderC="Tanner(section C)"
graderD="Yinuo(section D)"
# working directory
WD="$HOME/Downloads/CSE2111_7600"
if [[ $# -ne 1 || ! -d "$1" ]]; then
  echo "$#"
  echo "Usage: $0 DIRECTORY" >&2
  echo -e "\n$author"
  exit 1
fi
output_d="$1/output"
error="Student Names Directory: $WD\nMake sure it contains the lists of"\
" student names in each section. \n(Sec_A.txt, Sec_B.txt, Sec_C.txt, Sec_D.txt)"
# student names in four sections
[ ! -f "$WD/Sec_A.txt" ] && echo -e "$error" >&2 && exit 1
sec_A="`cat $WD/Sec_A.txt`"
sec_B="`cat $WD/Sec_B.txt`"
sec_C="`cat $WD/Sec_C.txt`"
sec_D="`cat $WD/Sec_D.txt`"
##############################################################################

[ -d "$output_d" ] && rm -rf "$output_d"
mkdir -p "$output_d/$graderA"
mkdir -p "$output_d/$graderB"
mkdir -p "$output_d/$graderC"
mkdir -p "$output_d/$graderD"
file="missed_submissions.txt"
touch "$output_d/$file"
echo "`date`" > "$output_d/$file"

# loop through all folders under working directory
while read directory; do
    if [[ "$directory" == "cse2111.sh" || "$directory" == "output" ]] ; then
        continue
    fi

    echo "Processing $directory" | tee -a "$output_d/$file"
    echo "Missing List:"
    mkdir -p "$output_d/$graderA/$directory"
    mkdir -p "$output_d/$graderB/$directory"
    mkdir -p "$output_d/$graderC/$directory"
    mkdir -p "$output_d/$graderD/$directory"

    i=0
    # section A
    while IFS= read -r p; do
        student="`ls \"$1/$directory\" | grep -i \"$p\" `"
        [ -z "$student" ] && echo "$p" | tee -a "$output_d/$file"
        [ -n "$student" ] && cp -r "$1/$directory/$student" "$output_d/$graderA/$directory" && i=$(($i+1))
    done <<< "$sec_A"

    # section B
    while IFS= read -r p; do
        student="`ls \"$1/$directory\" | grep -i \"$p\" `"
        [ -z "$student" ] && echo "$p" | tee -a "$output_d/$file"
        [ -n "$student" ] && cp -r "$1/$directory/$student" "$output_d/$graderB/$directory" && i=$(($i+1))
    done <<< "$sec_B"

    # section C
    while IFS= read -r p; do
        student="`ls \"$1/$directory\" | grep -i \"$p\" `"
        [ -z "$student" ] && echo "$p" | tee -a "$output_d/$file"
        [ -n "$student" ] && cp -r "$1/$directory/$student" "$output_d/$graderC/$directory" && i=$(($i+1))
    done <<< "$sec_C"

    # section D
    while IFS= read -r p; do
        student="`ls \"$1/$directory\" | grep -i \"$p\" `"
        [ -z "$student" ] && echo "$p" | tee -a "$output_d/$file"
        [ -n "$student" ] && cp -r "$1/$directory/$student" "$output_d/$graderD/$directory" && i=$(($i+1))
    done <<< "$sec_D"
    
    echo -e "Total Submissions: $i\n"
done <<< "`ls $1`"

echo "====================================================="
echo "No error found."
echo "Output summary:"
tree -L 1 "$output_d"
echo -e "\n$author"
echo "====================================================="