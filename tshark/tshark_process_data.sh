if [ $# -ne 1 ]; then
    echo "usage: ./tshark_capture.sh input_file"
    exit
fi

if [ ! -d log ]; then
    mkdir log
fi

BASENAME="$(basename $1 | cut -d "." -f 1)"
OUTPUT="$BASENAME.log"
tshark -r "$1" -T fields -e frame.number -e frame.time_epoch -e ip.proto \
    -e ip.dst -e frame.len -e data.data -e tcp.seq -E separator=" " \
    -Y "not tcp.analysis.retransmission and not tcp.analysis.fast_retransmission" > log/"$OUTPUT"
#cp ~/"$BASENAME.client.rssi" log
cp ~/"$BASENAME.tshark.rssi" log
# -R "frame.number < 3" -2
