ifconfig wlan5 192.168.1.1/24 up
ifconfig eth0 192.168.30.1/24 up
iptables -t nat -F
killall hostapd
killall dnsmasq
ip route add default via 192.168.30.4 dev eth0 
echo "nameserver 8.8.8.8" > /etc/resolv.conf
iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -o eth0 -j MASQUERADE
cd /home/alex/Downloads/RTL8812AU_linux_v4.3.2_11100.20140411-2014-10-11/RTL8812AU_linux_v4.3.2_11100.20140411/WiFi_Direct_User_Interface/
./hostapd ./rtl_hostapd_2G.conf &
dnsmasq -d &

