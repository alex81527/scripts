if [ "$#" -lt 2 ]; then 
	echo "Usage: ./via_ue2 {set|reset} <tunnel_ip>"
	exit 0
elif [ "$1" == "set" ]; then
	echo 1 > /proc/sys/net/ipv4/conf/eth0/proxy_arp
	echo 1 > /proc/sys/net/ipv4/ip_forward
	echo 1 > /proc/sys/net/ipv4/ip_nonlocal_bind
	printf "/proc/sys/net/ipv4/conf/eth0/proxy_arp = %d\n" $(cat /proc/sys/net/ipv4/conf/eth0/proxy_arp) 
	printf "/proc/sys/net/ipv4/ip_forward = %d\n" $(cat /proc/sys/net/ipv4/ip_forward) 
	printf "/proc/sys/net/ipv4/ip_nonlocal_bind = %d\n" $(cat /proc/sys/net/ipv4/ip_nonlocal_bind) 
	./set_route.sh wlan0 set $2
	arping -c 4 -A 140.113.240.19
elif [ "$1" == "reset" ]; then
	echo 0 > /proc/sys/net/ipv4/conf/eth0/proxy_arp
	echo 0 > /proc/sys/net/ipv4/ip_forward
	echo 0 > /proc/sys/net/ipv4/ip_nonlocal_bind
	printf "/proc/sys/net/ipv4/conf/eth0/proxy_arp = %d\n" $(cat /proc/sys/net/ipv4/conf/eth0/proxy_arp) 
	printf "/proc/sys/net/ipv4/ip_forward = %d\n" $(cat /proc/sys/net/ipv4/ip_forward) 
	./set_route.sh wlan0 reset
	printf "/proc/sys/net/ipv4/ip_nonlocal_bind = %d\n" $(cat /proc/sys/net/ipv4/ip_nonlocal_bind) 
fi
