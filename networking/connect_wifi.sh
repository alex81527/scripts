if [ "$#" -lt 3 ]; then 
	echo "Usage: connect_wifi <interface> <essid> <passphrase> [bssid]"
	exit 0
fi

killall wpa_supplicant
killall dhclient
echo "Connecting to $2..."

if [ "$#" -eq 3 ]; then
	wpa_passphrase $2 $3 > /etc/wpa_supplicant/$2.conf
	wpa_supplicant -B -i$1 -c/etc/wpa_supplicant/$2.conf
	dhclient $1
elif [ "$#" -eq 4 ]; then
	wpa_passphrase $2 $3 > /etc/wpa_supplicant/$2.conf
	arg=`printf "bssid=%s" $4`
	sed -i "/network={/ a $arg" /etc/wpa_supplicant/$2.conf
	wpa_supplicant -B -i$1 -c/etc/wpa_supplicant/$2.conf
	dhclient $1
fi
echo "Wifi connection successfully esatblished"
