set style data linespoints
#set xrange [0:1]
set yrange [900:1000]
set xlabel "time (seconds)"
set ylabel "Throughput (Mbps)"

# using column 1 for plotting x axis, column 2 for y axis
plot INPUT using 1:2 title "Throughput"

# output to file, save as png format
set term png
set output OUTPUT
replot
