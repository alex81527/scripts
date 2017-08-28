#!/usr/bin/env python3
import sys
import os
import argparse
import subprocess

# Define column mapping here. Order matters
FIELDS = ['frame_num', 'epoch', 'ip_proto', 'dst_ip', 'frame_len', 'data', 'tcp_seq']
COLUMN_MAP = {y: x for x, y in enumerate(FIELDS)}
# Define SEQ DIGITS
SEQ_DIGITS = 9
DEBUG_MODE = False

# constants generated from FIELDS
FRAME_NUM = COLUMN_MAP['frame_num']
EPOCH = COLUMN_MAP['epoch']
IP_PROTO = COLUMN_MAP['ip_proto']
DST_IP = COLUMN_MAP['dst_ip']
FRAME_LEN = COLUMN_MAP['frame_len']
SEQ = COLUMN_MAP['data']
TCP_SEQ = COLUMN_MAP['tcp_seq']


class LogParser():

    def __init__(self, filename, use_tunnel):
        self.filename = filename
        self.with_tunnel = use_tunnel
        
        # 0: tunnel with udp
        # 1: tunnel with tcp
        # 2: tunnel control msg
        # 3: no tunnel with udp
        # 4: no tunnel with tcp
        # 5: udp dport 8989 --> timing anchor point
        self.type = []
        self.handoffs = []
        self.timing_anchors = []

        self.lines = []
        with open(self.filename, 'r') as f:
            self.preprocess_data(f)

        self.pkt_loss_wigig_to_wifi = []
        self.pkt_loss_wifi_to_wigig = []
        self.delay_wigig_to_wifi = []
        self.delay_wifi_to_wigig = []
        self.length = len(self.lines)
        self.pkt_count = 0

        self.handoff_plot_data = []
        self.wigig_plot_data = []
        self.wifi_plot_data = []
        self.throughput_plot_data = []
        self.rssi_plot_data = []
        self.rssi_slope_plot_data = []
        self.rssi_for_overlapping = []
        self.h1_weight = [ 1.0, 0.5, 0.25, 0.125 ]

    def preprocess_data(self, f):
        first = True
        tcp_seq_anchor = None
        
        # 0: tunnel with udp
        # 1: tunnel with tcp
        # 2: tunnel control msg
        # 3: no tunnel with udp
        # 4: no tunnel with tcp
        # 5: udp dport 8989 --> timing anchor point
        lines = f.readlines()
        len_f = len(lines)
        for i in range(len_f):
            line = lines[i]
            tmp = line.split()
            # print(line[:85])

            # timing anchor
            if tmp[IP_PROTO] == '17':
                self.lines.append(tmp)
                self.type.append(5)
                self.timing_anchors.append(len(self.lines)-1)
            # icmp tunnel msg
            elif self.with_tunnel and tmp[IP_PROTO] == '1':
                try:
                    x = tmp[SEQ].split(':')
                except IndexError:
                    continue

                # udp, hex = 11
                if x[9] == '11':
                    y = []
                    if len(x) < (28 + SEQ_DIGITS):
                        tmp[SEQ] = -1
                        self.lines.append(tmp)
                        self.type.append(0)
                        continue

                    sth_wrong = False
                    for i in x[28:37]:
                        z = int(i, 16) 
                        if z >= 48 and z <= 57:
                            y.append(str(z-48))
                        else:
                            tmp[SEQ] = -1
                            self.lines.append(tmp)
                            self.type.append(0)
                            sth_wrong = True
                            break
                    
                    if sth_wrong:
                        continue
                            
                    tmp[SEQ] = int("".join(y))
                    self.lines.append(tmp)
                    self.type.append(0)
                # tcp, hex = 06
                elif x[9] == '06':
                    tmp[SEQ] = int("".join(x[24:28]), 16)
                    if first:
                        tcp_seq_anchor = tmp[SEQ]
                        first = False

                    tmp[SEQ] -= tcp_seq_anchor
                    self.lines.append(tmp)
                    self.type.append(1)

            # icmp tunnel, wifi control msg, tcp; filter out tcp retransmission
            elif self.with_tunnel and tmp[IP_PROTO] == '6':
                self.lines.append(tmp)
                self.type.append(2)
                self.handoffs.append(len(self.lines)-1) 
            # no tunnel, udp
            elif not self.with_tunnel and tmp[IP_PROTO] == '17':
                try:
                    x = tmp[SEQ].split(':')
                except IndexError:
                    continue

                y = []
                if len(x) < (SEQ_DIGITS):
                    tmp[SEQ] = -1
                    self.lines.append(tmp)
                    self.type.append(3)
                    continue

                sth_wrong = False
                for i in x[0:9]:
                    z = int(i, 16) 
                    if z >= 48 and z <= 57:
                        y.append(str(z-48))
                    else:
                        tmp[SEQ] = -1
                        self.lines.append(tmp)
                        self.type.append(3)
                        break

                if sth_wrong:
                    continue
                    
                tmp[SEQ] = int("".join(y))
                self.lines.append(tmp)
                self.type.append(3)           
            # no tunnel, tcp
            elif not self.with_tunnel and tmp[IP_PROTO] == '6':
                self.lines.append(tmp)
                self.type.append(4)
            # something else, garbage
            else:
                continue


            # if self.with_tunnel and traffic_type == 2:
            #     self.handoffs.append(i) 
            #     print('put into handoff', line)
            #     print(i)

            # if traffic_type == 5:
            #     self.timing_anchors.append(i)

    def gen_plot_data(self, time_begin=-1, time_end=-1):
        # unit: second
        time_begin = time_begin if time_begin != -1 else 0
        time_end = time_end if time_end != -1 else float(self.lines[-1][EPOCH]) - float(self.lines[0][EPOCH])
        
        sample_interval = 0.5
        # output directory 
        directory = "./plot_data/"
        filename = os.path.basename(self.filename)
        
        dot = self.filename.rfind(".")
        rssi_data = None
        rssi_timing_anchors = None
        with open(self.filename[:dot] + ".tshark.rssi") as f:
            rssi_data = f.readlines()
            rssi_timing_anchors = [i for i in range(len(rssi_data)) if 'timing anchor' in rssi_data[i]]


        throughput_calc_interval = 0.5
        # n: number of points in 0.5s interval
        number_of_points = 1
        # throughput
        # print(self.timing_anchors)
        for i in range(len(self.timing_anchors) - 1):
            idx_cur_timing_anchor = self.timing_anchors[i]
            idx_next_timing_anchor = self.timing_anchors[i + 1]

            count = 1
            received_bytes = 0
            t0 = float(self.lines[idx_cur_timing_anchor+1][EPOCH])
            j = idx_cur_timing_anchor + 1
            n = number_of_points
            while True:
                if j == idx_next_timing_anchor:
                    while count <= n:
                        throughput = (received_bytes*8)/(throughput_calc_interval*1000000)
                        self.throughput_plot_data.append("{0:.3f} {1}".format(i*sample_interval+throughput_calc_interval*count, throughput))
                        count += 1
                        received_bytes = 0

                    break
                        
                t = float(self.lines[j][EPOCH])
                # 0: tunnel with udp
                # 1: tunnel with tcp
                # 2: tunnel control msg
                # 3: no tunnel with udp
                # 4: no tunnel with tcp
                # 5: udp dport 8989 --> timing anchor point
                if self.type[j] == 1:
                    header_len = 16 + 20 + 8 + 20 +20
                    received_bytes += int(self.lines[j][FRAME_LEN]) - header_len
                elif self.type[j] == 4:
                    header_len = 16 + 20 + 20
                    received_bytes += int(self.lines[j][FRAME_LEN]) - header_len

                if count < n and t - t0 > throughput_calc_interval*count:
                    throughput = (received_bytes*8)/(throughput_calc_interval*1000000)
                    self.throughput_plot_data.append("{0:.3f} {1}".format(i*sample_interval+throughput_calc_interval*count, throughput))
                    count += 1
                    received_bytes = 0
                
                j += 1

            # print("{0:.3f} {1}".format((i+1)*sample_interval, throughput))



        # rssi
        for i in range(len(rssi_timing_anchors) - 1):
            idx_cur_rssi_timing_anchor = rssi_timing_anchors[i]
            idx_next_rssi_timing_anchor = rssi_timing_anchors[i + 1]
            # get rssi 
            count = 0
            rssi_values = []

            for k in range(idx_next_rssi_timing_anchor-1, idx_cur_rssi_timing_anchor, -1):
                line = rssi_data[k]
                start = line.find('ML RSSI')
                if start != -1:
                    start += 9
                    rssi_values.append(line[start:line.find(',', start)])
                    count +=1    
                
                if count == 5:
                    break

            while len(rssi_values) < 5:
                rssi_values.append(0)
            
            rssi_values.reverse()
            tic = 0.1
            for k in range(len(rssi_values)):
                # slope of rssi
                # if n == 0:
                #     if k >=1:
                #         slope = (int(rssi_values[k]) - int(rssi_values[k-1]))/tic
                #         self.rssi_slope_plot_data.append("{0:.3f} {1:.3f}".format(n*sample_interval+tic*(k+1), slope))
                # else:
                #     if k==0:
                #         slope = (int(rssi_values[k]) - int(self.rssi_plot_data[-1].split()[1]))/tic
                #         self.rssi_slope_plot_data.append("{0:.3f} {1:.3f}".format(n*sample_interval+tic*(k+1), slope))               
                #     else:
                #         slope = (int(rssi_values[k]) - int(rssi_values[k-1]))/tic
                #         self.rssi_slope_plot_data.append("{0:.3f} {1:.3f}".format(n*sample_interval+tic*(k+1), slope))
                
                # rssi
                self.rssi_plot_data.append("{0:.3f} {1}".format(i*sample_interval+tic*(k+1), rssi_values[k]))
                self.rssi_for_overlapping.append(int(rssi_values[k]))
                # print("{0:.3f} {1}".format(n*sample_interval+tic*(k+1), rssi_values[k]))



        # rssi moving average
        self.h1_weight = [ 1.0, 0.5, 0.25, 0.125 ]

        for h1_w in self.h1_weight:
            h0 = self.rssi_for_overlapping[0]
            rssi_moving_avg = []
            rssi_moving_avg.append(h0)
            h0_weight = 1 - h1_w
            for i in range(1, len(self.rssi_for_overlapping)):
                h1 = h1_w*self.rssi_for_overlapping[i] + h0_weight*h0
                h0 = h1
                rssi_moving_avg.append(h0)
            # rssi overlapping
            for i in range(len(rssi_moving_avg) -2 ):
                if rssi_moving_avg[i] > rssi_moving_avg[i+1] and rssi_moving_avg[i] > rssi_moving_avg[i+2] and \
                    rssi_moving_avg[i] > rssi_moving_avg[i+3] and rssi_moving_avg[i] > rssi_moving_avg[i+4] and rssi_moving_avg[i+4] < -45:
                    t0 = float(self.rssi_plot_data[i].split()[0])
                    tmp = []
                    for j in range(i, len(self.rssi_plot_data)):
                        line = self.rssi_plot_data[j].split()
                        t = float(line[0])
                        rssi = rssi_moving_avg[j]
                        tmp.append('{0:.3f} {1:.3f}'.format(t-t0, rssi))
                    
                    break

            with open(directory + filename + ".rssi_overlap.weight" + str(h1_w), "w") as ro:
                ro.write("\n".join(tmp))

        # write all plot data into files
        with open(directory + filename + ".handoff", "w") as ho, open(
                directory + filename + ".wigig", "w") as wg, open(
                directory + filename + ".wifi", "w") as wf, open(
                directory + filename + ".throughput", "w") as th, open(
                directory + filename + ".rssi", "w") as rs: 
                # open(directory + filename + ".rssi_slope", "w") as rsl:
            ho.write("\n".join(self.handoff_plot_data))
            wg.write("\n".join(self.wigig_plot_data))
            wf.write("\n".join(self.wifi_plot_data))
            th.write("\n".join(self.throughput_plot_data))
            rs.write("\n".join(self.rssi_plot_data))
            # rsl.write("\n".join(self.rssi_slope_plot_data))


    def plot_data(self):
        directory = "./plot_data/"
        filename = os.path.basename(self.filename)
        handoff = directory + filename + ".handoff"
        wigig = directory + filename + ".wigig"
        wifi = directory + filename + ".wifi"
        throughput = directory + filename + ".throughput"
        rssi = directory + filename + ".rssi"
        rssi_slope = directory + filename + ".rssi_slope"
        title = "{0}".format(filename.replace("_", "-"))
        # output file path
        output1 = "~/0714/" + filename + ".seq_throughput.png"
        output2 = "~/0714/" + filename + ".seq_rssi.png"
        output3 = "~/0722/" + filename + ".rssi_throughput.png"
        output4 = "~/0720/" + filename + ".rssi_slope.png"
        output5 = "~/0720/" + filename + ".rssi_overlap.png"
        # plot scripts
        seq_and_throughput_gp = "./plot_script/seq_throughput.gp"
        seq_and_rssi_gp = "./plot_script/seq_rssi.gp"
        rssi_and_throughput_gp = "./plot_script/rssi_throughput.gp"
        rssi_slope_gp = "./plot_script/rssi_slope.gp"
        rssi_overlap_gp = "./plot_script/rssi_overlap.gp"
        # HANDOFF=$1; WIGIG=$2; WIFI=$3; THROUGHPUT=$4; RSSI=$5; OUTPUT=$6; TITLE=$7 SCRIPT=$8
        # cmd1 = "./plot_script/plot.sh {0} {1} {2} {3} {4} {5} {6} {7}".format(
        #         handoff, wigig, wifi, throughput, rssi, output1, title, seq_and_throughput).split()
        # subprocess.run(cmd1, check=True)
        
        # cmd2 = "./plot_script/plot.sh {0} {1} {2} {3} {4} {5} {6} {7}".format(
        #         handoff, wigig, wifi, throughput, rssi, output2, title, seq_and_rssi).split()
        # subprocess.run(cmd2, check=True)

        # cmd3 = "./plot_script/plot.sh {0} {1} {2} {3} {4} {5} {6} {7}".format(
        #         handoff, wigig, wifi, throughput, rssi, output3, title, throughput_and_rssi).split()
        # subprocess.run(cmd3, check=True)

        cmd = "gnuplot -p -c {0} {1} {2} {3} {4}".format(rssi_and_throughput_gp, title, rssi, throughput, output3).split()
        subprocess.run(cmd, check=True)

        # cmd = "gnuplot -p -c {0} {1} {2} {3} {4}".format(rssi_slope_gp, title, rssi, rssi_slope, output4).split()
        # subprocess.run(cmd, check=True)

        # option = ['shift', 'rotate']
        # for mcs in [ '7' ]:
        #     for method in ['shift']:#, 'rotate']:
        #         # method = option[0]
        #         date = '0721'
        #         for weight in self.h1_weight:
        #             # mcs = '7'
        #             cmd = "gnuplot -p -c {0} {1} {2} {3} {4} {5}".format(rssi_overlap_gp, 
        #                 'mcs{0}-{1}-case/moving-average/h1-weight-{2}'.format(mcs, method, weight), 
        #                 directory+'{0}_mcs{1}_block2s.log.rssi_overlap.weight{2}'.format(date, mcs, weight), 
        #                 directory+'{0}_mcs{1}_{2}_back.log.rssi_overlap.weight{3}'.format(date, mcs, method, weight),
        #                 directory+'{0}_mcs{1}_{2}_away.log.rssi_overlap.weight{3}'.format(date, mcs, method, weight), 
        #                 '~/{0}/{0}_mcs{1}_{2}_rssi_overlap.weight{3}.png'.format(date, mcs, method, weight)).split()
        #             subprocess.run(cmd, check=True)

    def print_throughput(self):
        interval = []
        pkt_size = []
        for i in range(2, 10000):
            if self.lines[i][IP_PROTO] == '6':
                continue

            interval.append(float(self.lines[i][EPOCH]) - float(self.lines[i - 1][EPOCH]))
            pkt_size.append(int(self.lines[i][FRAME_LEN]) - 73)

        avg_interval = sum(interval) / len(interval)
        avg_pkt_size = sum(pkt_size) / len(pkt_size)

        print('Avg inter-arrival time: {0:.6f}s'.format(avg_interval))
        print('Avg packet size: {0:.3f} byte'.format(avg_pkt_size))
        print('Approx. throughput: {0:.3f} Mbps'.format(8 * avg_pkt_size / (
            avg_interval * 1000000)))
        # print(interval[-10:-1])
        print('=' * 80)

    def calc_delay(self):
        if DEBUG_MODE:
            print(self.handoffs)
        
        for i in range(len(self.handoffs) - 1):
            idx_cur_handoff = self.handoffs[i]
            idx_next_handoff = self.handoffs[i + 1]

            if i == 0:
                for j in range(idx_cur_handoff-1, -1, -1):
                    if self.type[j] != 5:
                        cur_link = 'wigig' if self.lines[j][DST_IP] == '140.113.207.243' else 'wifi'
                        break
                
                next_link = 'wigig' if cur_link == 'wifi' else 'wifi'   
            else:
                cur_link = next_link
                next_link = 'wifi' if next_link == 'wigig' else 'wigig'

            # Handoff delay = t2(first packet after handoff) - t1(client
            # sends control msg)

            # Packet loss = seq2(the smallest seq from the new link after
            # handoff) - seq1(the largest seq from previous link before
            # handoff)

            # Get the first packet received at client after handoff
            idx_first_packet = None
            check_first_packet = True
            
            for j in range(idx_cur_handoff + 1, idx_next_handoff):
                # timing anchors
                if self.type[j] == 5:
                    continue

                link = 'wigig' if self.lines[j][DST_IP] == '140.113.207.243' else 'wifi'

                # t2
                if check_first_packet and link == next_link:
                    idx_first_packet = j
                    check_first_packet = False
                    break


            if idx_first_packet == None:
                print('Something wrong!')
                print('idx_first_packet=', idx_first_packet)
                print('-' * 80)
            else:
                t2 = float(self.lines[idx_first_packet][EPOCH])
                t1 = float(self.lines[idx_cur_handoff][EPOCH])

                if DEBUG_MODE:
                    print('{0} to {1}'.format(cur_link, next_link))
                    print('HO:\t', self.lines[idx_cur_handoff])
                    print('first:\t', self.lines[idx_first_packet])
                    print('delay = {0} - {1} = {2}'.format(t2, t1, t2 - t1))
                    print('-' * 80)

                if next_link == 'wifi':
                    self.delay_wigig_to_wifi.append(t2 - t1)
                elif next_link == 'wigig':
                    self.delay_wifi_to_wigig.append(t2 - t1)

        print('wigig to wifi')
        print('handoff delay: ', self.delay_wigig_to_wifi)
        if len(self.delay_wigig_to_wifi) != 0:
            print('avg handoff delay: {0:.6f}s'.format(sum(self.delay_wigig_to_wifi) / len(self.delay_wigig_to_wifi)))
        print('=' * 80)
        print('wifi to wigig')
        print('handoff delay: ', self.delay_wifi_to_wigig)
        if len(self.delay_wifi_to_wigig) != 0:
            print('avg handoff delay: {0:.6f}s'.format(sum(self.delay_wifi_to_wigig) / len(self.delay_wifi_to_wigig)))
        print('=' * 80)     

    def calc_handoff_statistics(self):
        if DEBUG_MODE:
            print(self.handoffs)
        
        cur_link = None
        next_link = None
        for i in range(len(self.handoffs) - 1):
            idx_cur_handoff = self.handoffs[i]
            idx_next_handoff = self.handoffs[i + 1]

            if i == 0:
                for j in range(idx_cur_handoff-1, -1, -1):
                    if self.type[j] != 5:
                        cur_link = 'wigig' if self.lines[j][DST_IP] == '140.113.207.243' else 'wifi'
                        break
                
                next_link = 'wigig' if cur_link == 'wifi' else 'wifi'   
                last_max_seq = 0
                for j in range(idx_cur_handoff):
                    if self.type[j] != 5:
                        tmp_seq = self.lines[j][SEQ]
                        if j == 0 or tmp_seq > last_max_seq:
                            idx_last_max_seq = j
                            last_max_seq = tmp_seq
            else:
                cur_link = next_link
                next_link = 'wifi' if next_link == 'wigig' else 'wigig'

            # Handoff delay = t2(first packet after handoff) - t1(client
            # sends control msg)

            # Packet loss = seq2(the smallest seq from the new link after
            # handoff) - seq1(the largest seq from previous link before
            # handoff)

            # Get the first packet received at client after handoff
            idx_first_packet = None
            check_first_packet = True
            # Get the smallest seq from the new link after handoff
            idx_seq2 = None
            min_seq2 = None
            # Get the largest seq from previous link before handoff
            idx_seq1 = None
            max_seq1 = None

            # Get current max seq btw
            cur_max_seq = None
            idx_cur_max_seq = None
    
            if DEBUG_MODE:
                print('last_max_seq {0}'.format(last_max_seq))
            
            for j in range(idx_cur_handoff + 1, idx_next_handoff):
                # timing anchors
                if self.type[j] == 5:
                    continue

                seq = self.lines[j][SEQ]
                link = 'wigig' if self.lines[j][DST_IP] == '140.113.207.243' else 'wifi'
                self.pkt_count += 1

                # filter out-pf-order packets
                try:
                    if seq < last_max_seq:
                        continue
                except TypeError:
                    print(self.lines[j])
                    print(self.type[j])
                    for x in range(518561, 518567):
                        print(self.lines[x])

                # t2
                if check_first_packet and link == next_link:
                    idx_first_packet = j
                    check_first_packet = False

                # seq2
                if link == next_link and (min_seq2 == None or seq < min_seq2):
                    min_seq2 = seq
                    idx_seq2 = j

                # seq1
                if link == cur_link and (max_seq1 == None or seq > max_seq1):
                    max_seq1 = seq
                    idx_seq1 = j

                # collect max_seq btw
                if j == idx_cur_handoff + 1 or seq > cur_max_seq:
                    idx_cur_max_seq = j
                    cur_max_seq = seq

            if idx_seq1 == None:
                if DEBUG_MODE:
                    print('idx_seq1 None')
                idx_seq1 = idx_last_max_seq

            idx_last_max_seq = idx_cur_max_seq
            last_max_seq = cur_max_seq

            if idx_first_packet == None or idx_seq2 == None or idx_seq1 == None:
                print('Something wrong!')
                print('idx_first_packet=', idx_first_packet)
                print('idx_seq2=', idx_seq2)
                print('idx_seq1=', idx_seq1)
                print('-' * 80)
            else:
                t2 = float(self.lines[idx_first_packet][EPOCH])
                t1 = float(self.lines[idx_cur_handoff][EPOCH])
                seq2 = self.lines[idx_seq2][SEQ]
                seq1 = self.lines[idx_seq1][SEQ]

                if DEBUG_MODE:
                    print('{0} to {1}'.format(cur_link, next_link))
                    print('HO:\t', self.lines[idx_cur_handoff])
                    print('first:\t', self.lines[idx_first_packet])
                    print('seq2:\t', self.lines[idx_seq2])
                    print('seq1:\t', self.lines[idx_seq1])
                    print('delay = {0} - {1} = {2}'.format(t2, t1, t2 - t1))
                    print('pkt loss = {0} - {1} -1 = {2}'.format(
                        seq2, seq1, seq2 - seq1 - 1))
                    print('-' * 80)

                if next_link == 'wifi':
                    self.pkt_loss_wigig_to_wifi.append(seq2 - seq1 - 1)
                    self.delay_wigig_to_wifi.append(t2 - t1)
                elif next_link == 'wigig':
                    self.pkt_loss_wifi_to_wigig.append(seq2 - seq1 - 1)
                    self.delay_wifi_to_wigig.append(t2 - t1)

        # print out statistics
        print(self.filename)
        print('=' * 80)

        if len(self.pkt_loss_wigig_to_wifi) != 0:
            print('handoff from wigig to wifi')
            print('packet loss: ', self.pkt_loss_wigig_to_wifi)
            print('handoff delay: ', self.delay_wigig_to_wifi)
            print('avg packet loss: {0:.2f}'.format(
                sum(self.pkt_loss_wigig_to_wifi) / len(
                    self.pkt_loss_wigig_to_wifi)))
            print('avg handoff delay: {0:.6f}s'.format(
                sum(self.delay_wigig_to_wifi) / len(self.delay_wigig_to_wifi)))
        else:
            print('No data for handoff from wigig to wifi')

        print('=' * 80)

        if len(self.pkt_loss_wifi_to_wigig) != 0:
            print('handoff from wifi to wigig')
            print('packet loss: ', self.pkt_loss_wifi_to_wigig)
            print('handoff delay: ', self.delay_wifi_to_wigig)
            print('avg packet loss: {0:.2f}'.format(
                sum(self.pkt_loss_wifi_to_wigig) / len(
                    self.pkt_loss_wifi_to_wigig)))
            print('avg handoff delay: {0:.6f}s'.format(
                sum(self.delay_wifi_to_wigig) / len(self.delay_wifi_to_wigig)))
        else:
            print('No data for handoff from wifi to wigig')

        print('=' * 80)

        print('avg inter arrival time:',  (float(self.lines[self.handoffs[-1]-1][EPOCH]) - float(self.lines[self.handoffs[0]+1][EPOCH]))/(self.pkt_count -1) )

        print('=' * 80)
def main():
    parser = argparse.ArgumentParser(description='Parser for tshark logs.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
            '-s',
            '--statistics',
            action='store_true',
            help='calculate packet loss and handoff delay from the log')
    parser.add_argument(
            '-t',
            '--throughput',
            action='store_true',
            help='print throughput and average inter-arrival time')
    parser.add_argument(
            '-g',
            '--generate',
            nargs=2,
            metavar=('time_begin', 'time_end'),
            action='store',
            help='generate plot data for gnuplot')
    parser.add_argument(
            '-p',
            '--plot',
            action='store_true',
            help='plot figure and save output to a file')
    parser.add_argument(
            '-i',
            '--icmptunnel',
            action='store_true',
            help='indicate whether icmp tunnel is used')
    parser.add_argument(
            '-d',
            '--delay',
            action='store_true',
            help='calculate handoff delay only')
    parser.add_argument('filename', action='store', help='log file to parse')
    args = parser.parse_args(sys.argv[1:])
    # parser.print_help()
    
    test = LogParser(args.filename, args.icmptunnel)
    if args.statistics:
        test.calc_handoff_statistics()
    if args.delay:
        test.calc_delay()
    if args.throughput:
        test.print_throughput()
    if args.generate:
        test.gen_plot_data(int(args.generate[0]), int(args.generate[1]))
    if args.plot:
        test.plot_data()
    return


if __name__ == "__main__":
    main()
