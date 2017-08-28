#!/usr/bin/env python3
import subprocess
import time

iperf_cmd = 'iperf3 -c 140.113.207.245 -t 0 -R'.split()
get_rssi_cmd = 'tail -1 /var/log/kern.log'.split()
# TODO
change_route = 'ip route del 140.113.207.245 && ip route add 140.113.207.245 dev {0}'.format('wlx2c4d54ce1065')
threshold = -76

# run in background
with subprocess.Popen(iperf_cmd) as proc:
	pid = proc.pid
	print('iperf pid:', pid)
	
	while True: 
		tmp = subprocess.run(get_rssi_cmd, check=True, stdout=subprocess.PIPE).stdout.decode()
		while not 'ML RSSI' in tmp:
			time.sleep(0.05)
			tmp = subprocess.run(get_rssi_cmd, check=True, stdout=subprocess.PIPE).stdout.decode()
		
		start = tmp.find('ML RSSI')+9    
		cur_rssi = int(tmp[start:tmp.find(',', start)])
		if cur_rssi <= threshold:
			proc.kill()
			print('{0}: iperf killed'.format(pid))
			print('Modify routing table:', change_route)
			subprocess.run(change_route.split(), check=True)
			break

subprocess.run(iperf_cmd, check=True)
