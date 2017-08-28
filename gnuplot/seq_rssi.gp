reset
# set style data points
#set xrange [0:1]
set y2range [-80:-30]

set xlabel "Epoch (second)"
set ylabel "Sequence Number"
set y2label "RSSI (dBm)"
set y2tics
set ytics nomirror
set key right bottom
set title ARG1
# set autoscale 
plot ARG2 using 1:2 title "Handoff" with point pointsize 1 lc 'red' pt 15 axis x1y1, \
    ARG3 using 1:2 title "WiGig" with points ls 3 axis x1y1, \
    ARG4 using 1:2 title "Wi-Fi" with points ls 4 axis x1y1, \
    ARG5 using 1:2 title "RSSI" with linespoints ls 8 axis x1y2
    # THROUGHPUT using 1:2 title "Throughput" with linespoints ls 1 axis x1y2 
#plot RSSI using 1:2 title "RSSI" with linespoints 

# output to file, save as png format
# set term png
# set terminal postscript eps enhanced color font 'Helvetica,10'
set terminal png size 800,600 enhanced 
set output ARG6
replot
