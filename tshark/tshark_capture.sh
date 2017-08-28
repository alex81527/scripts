if [ $# -ne 1 ]; then
    echo "usage: ./tshark_capture.sh save_filename"
    exit
fi

DIRECTORY="$(dirname $1)"
FILE="$DIRECTORY/$(basename $1 | cut -d '.' -f 1).tshark.rssi"

trap_control_c ()
{
	# RSSI_END="$(tail -1 /var/log/kern.log | grep 'ML RSSI')"
	# while [ -z "$RSSI_END" ]; do
	# 	sleep 0.1
	# 	RSSI_END="$(tail -1 /var/log/kern.log | grep 'ML RSSI')"
	# done

	# echo "$DIRECTORY"
	# echo $RSSI_END
	# echo "$RSSI_BEGIN" > "$FILE"
	# echo "$RSSI_END" >> "$FILE"
    # echo "$EPOCH" >> "$FILE"
	# echo "RSSI data is saved in $FILE"
    # kill -INT $TSHARK_PID
    echo "[$TAIL_PID] tail -1 /var/log/kern.log killed"
    kill $TAIL_PID
}

trap trap_control_c 2

# EPOCH=$(date +%s.%N)
# RSSI_BEGIN="$(tail -1 /var/log/kern.log | grep 'ML RSSI')"
# while [ -z "$RSSI_BEGIN" ]; do
# 	sleep 0.1
#     EPOCH=$(date +%s.%N)
# 	RSSI_BEGIN="$(tail -1 /var/log/kern.log | grep 'ML RSSI')"
# done

# echo $RSSI_BEGIN

# with tunnel 
TUNNEL="tshark -i any -s 200 -w $1 -n \( icmp and \( dst host 140.113.207.244 or dst host 140.113.207.243\) \) or \( dst host 140.113.207.245 and tcp \)"

# wigig, tcp, no handoff
TCP_IPERF="tshark -i any -s 200 -w $1 -n dst host 140.113.207.243 and tcp port 5201"

# wigig, udp, no handoff
UDP_IPERF="tshark -i any -s 200 -w $1 -n dst host 140.113.207.243 and udp port 5201"

# iperf3
echo $(date +%s.%N) > "$FILE"
tail -f /var/log/kern.log >> "$FILE" &
TAIL_PID=$!
eval "$TUNNEL"
# TSHARK_PID=$!


