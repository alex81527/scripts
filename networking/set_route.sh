if [ "$#" -lt 3 ]; then 
	echo "Usage: set_route <interface> {set|reset} <tunnel_ip>"
	exit 0
elif [ "$1" == "wlan0" ] && [ "$2" == "set" ]; then
	#ip route del 140.113.240.0/24 dev eth0
	#ip route del default via 140.113.240.254 dev eth0
	#ip route add 140.113.240.0/24 dev wlan5

	MY_IP=$(ifconfig wlan0 | grep 'inet addr' | sed s/'.*inet addr:'//g | sed s/'  Bcast.*'//ig)
	
	iptunnel add mytun mode ipip remote 10.0.0.4 local 10.0.0.5 dev wlan5
	ifconfig mytun up
	ifconfig mytun $MY_IP
	ifconfig mytun pointopoint $3

elif [ "$1" == "wlan0" ] && [ "$2" == "reset" ]; then
	#ip route del 140.113.240.0/24 dev wlan5
	#ip route add 140.113.240.0/24 dev eth0	
	#ip route add default via 140.113.240.254 dev eth0

	iptunnel del mytun

fi
