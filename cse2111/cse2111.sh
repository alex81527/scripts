#!/usr/bin/env bash

# Author: Wei-Han Chen, PhD student
# Co-Sy-Ne Communication Systems and Networking group
# Dept. of Computer Science and Engineering
# The Ohio State University
# Sun Jan 27 18:08:28 EST 2019

# Parameters
##############################################################################
# grader list
graderA="Reagan(section A)"
graderB="Junboem(section B)"
graderC="Tanner(section C)"
graderD="Yinuo(section D)"
# working directory
WD="$HOME/Downloads"
# student names in four sections
sec_A="`cat $WD/Sec_A.txt`"
sec_B="`cat $WD/Sec_B.txt`"
sec_C="`cat $WD/Sec_C.txt`"
sec_D="`cat $WD/Sec_D.txt`"
##############################################################################

[ -d "output" ] && rm -rf "outpout"
mkdir -p "output/$graderA"
mkdir -p "output/$graderB"
mkdir -p "output/$graderC"
mkdir -p "output/$graderD"
file="missed_submissions.txt"
touch "output/$file"
echo "`date`" > "output/$file"

# loop through all folders under working directory
while read directory; do
    if [[ "$directory" == "cse2111.sh" || "$directory" == "output" ]] ; then
        continue
    fi

    echo -n "Processing $directory" | tee -a "output/$file"
    mkdir -p "output/$graderA/$directory"
    mkdir -p "output/$graderB/$directory"
    mkdir -p "output/$graderC/$directory"
    mkdir -p "output/$graderD/$directory"

    i=1
    # section A
    while IFS= read -r p; do
        student="`ls \"$directory\" | grep -i \"$p\" `"
        [ -z "$student" ] && echo "$p" >> "output/$file"
        [ -n "$student" ] && cp -r "$directory/$student" "output/$graderA/$directory" && i=$(($i+1))
    done <<< "$sec_A"

    # section B
    while IFS= read -r p; do
        student="`ls \"$directory\" | grep -i \"$p\" `"
        [ -z "$student" ] && echo "$p" >> "output/$file"
        [ -n "$student" ] && cp -r "$directory/$student" "output/$graderB/$directory" && i=$(($i+1))
    done <<< "$sec_B"

    # section C
    while IFS= read -r p; do
        student="`ls \"$directory\" | grep -i \"$p\" `"
        [ -z "$student" ] && echo "$p" >> "output/$file"
        [ -n "$student" ] && cp -r "$directory/$student" "output/$graderC/$directory" && i=$(($i+1))
    done <<< "$sec_C"

    # section D
    while IFS= read -r p; do
        student="`ls \"$directory\" | grep -i \"$p\" `"
        [ -z "$student" ] && echo "$p" >> "output/$file"
        [ -n "$student" ] && cp -r "$directory/$student" "output/$graderD/$directory" && i=$(($i+1))
    done <<< "$sec_D"
    
    echo -e "\t submissions: $i"
done <<< "`ls ./`"
