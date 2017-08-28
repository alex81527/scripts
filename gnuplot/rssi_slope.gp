reset
# set style data points
# set xrange [0:24]
set yrange [-80:-30]
# set y2range [0:800]

set xlabel "Epoch (second)"
set ylabel "RSSI (-dBm)"
set y2label "Slope"
# set y2tics 0, 100
set ytics -80, 10
set ytics nomirror
set xtics 0, 2
set y2tics

set key right bottom
set title ARG1
# set autoscale
plot ARG2 using 1:2 title "RSSI" with linespoints ls 4 axis x1y1, \
    ARG3 using 1:2 title "Slope" with linespoints ls 8 axis x1y2 
    #RSSI using 1:2 title "RSSI" with linespoints axis x1y1
#plot RSSI using 1:2 title "RSSI" with linespoints 

# output to file, save as png format
# set term png
# set terminal postscript eps enhanced color font 'Helvetica,10'
set terminal png size 800,600 enhanced 
set output ARG4
replot
