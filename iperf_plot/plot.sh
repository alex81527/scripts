#!/usr/bin/env bash 

USAGE="Usage: ./plot.sh input_file output_file"

if [ $# -ne 2 ]; then
    echo $USAGE
    exit
fi

gnuplot -persist -e "INPUT=\"$1\"; OUTPUT=\"$2\"" plot_iperf.gnuplot 
