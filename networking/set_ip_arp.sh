if [ "$#" -lt 1 ]; then 
	echo "Usage: ./set_ip_arp [set | reset]"
	exit 0
elif [ "$1" == "set" ]; then
	echo 1 > /proc/sys/net/ipv4/conf/eth0/proxy_arp
	echo 1 > /proc/sys/net/ipv4/ip_forward
	printf "/proc/sys/net/ipv4/conf/eth0/proxy_arp = %d\n" $(cat /proc/sys/net/ipv4/conf/eth0/proxy_arp) 
	printf "/proc/sys/net/ipv4/ip_forward = %d\n" $(cat /proc/sys/net/ipv4/ip_forward) 
elif [ "$1" == "reset" ]; then
	echo 0 > /proc/sys/net/ipv4/conf/eth0/proxy_arp
	echo 0 > /proc/sys/net/ipv4/ip_forward
	printf "/proc/sys/net/ipv4/conf/eth0/proxy_arp = %d\n" $(cat /proc/sys/net/ipv4/conf/eth0/proxy_arp) 
	printf "/proc/sys/net/ipv4/ip_forward = %d\n" $(cat /proc/sys/net/ipv4/ip_forward) 

fi
