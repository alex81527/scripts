#!/usr/bin/env python3
import subprocess
import time
import sys
import signal 
import socket

filename = sys.argv[1]
# wigig='tcwigig'
# wifi='wlx2c4d54ce1065'
interval = 0.5
# with tunnel 
tshark_tunnel = "tshark -i any -s 200 -w {0} -n ( icmp and ( dst host 140.113.207.244 or dst host 140.113.207.243 ) ) or ( dst host 140.113.207.245 and tcp ) or udp dst port 8989".format(filename).split()
# "tshark -i {0} -i {1} -i lo -s 200 -w {2} -n \( icmp and \( dst host 140.113.207.244 or dst host 140.113.207.243\) \) or \( dst host 140.113.207.245 and tcp \) or dst udp port 8989".format(wigig, wifi, filename).split()
# wigig, tcp, no handoff
tshark_tcp_iperf = "tshark -i any -s 200 -w {0} -n ( dst host 140.113.207.243 and tcp port 5201 ) or udp dst port 8989".format(filename).split()
# wigig, udp, no handoff
# UDP_IPERF="tshark -i any -s 200 -w $1 -n dst host 140.113.207.243 and udp port 5201"
tshark_cmd = tshark_tcp_iperf
nc = 'nc -n -l -u 8989'.split()
get_rssi_cmd = 'tail -20 /var/log/kern.log'.split()

n = 0
rssi_data = []

def signal_handler(self, signal):
        print('You pressed Ctrl+C!')
        dot = filename.rfind(".")
        with open(filename[:dot] + ".tshark.rssi", 'w') as f:
        	f.write(''.join(rssi_data))
        
        proc_nc.kill()
        proc_tshark.kill()
        sys.exit(0)

if __name__ == '__main__':
	signal.signal(signal.SIGINT, signal_handler)

	sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	dst = ('140.113.207.243', 8989)

	# run in background
	proc_nc = subprocess.Popen(nc)
	proc_tshark = subprocess.Popen(tshark_cmd)
	
	wait = 2
	print('tshark pid: {0}, wait {1} seconds'.format(proc_tshark.pid, wait))
	time.sleep(wait)

	while True: 
		sk.sendto('1'.encode(), dst)
		rssi_data.append('timing anchor\n')
		# subprocess.run(nc, shell=True)
		# subprocess.run(get_rssi_cmd)
		tmp = subprocess.run(get_rssi_cmd, stdout=subprocess.PIPE).stdout.decode()
		# for line in tmp:
			# print(line)
		rssi_data.append(tmp)	

		n += 1
		time.sleep(interval)