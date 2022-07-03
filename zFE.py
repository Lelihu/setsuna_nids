import os
import subprocess
import sys
import csv
import numpy as np
import netStat as ns

class FE:
    def __init__(self, file_path, limit):
        self.path = file_path
        self.limit = limit
        self.parse_type = None
        self.curPacketIndx = 0
        self.tsvin = None
        self.__prep__()

        # prepare AfterImage
        maxHost = 100000000000
        maxSess = 100000000000
        self.nstat = ns.netStat(np.nan, maxHost, maxSess)

    def _get_tshark_path(self):
        if 'win' in sys.platform:
            return './tsk/tshark.exe'
        else:
            system_path = os.environ['PATH']
            for path in system_path.split(os.pathsep):
                filename = os.path.join(path, 'tshark')
                if os.path.isfile(filename):
                    return filename
        return

    def __prep__(self):
        if not os.path.isfile(self.path):
            raise RuntimeError("[!] Kit-NET FeExtractor>_ File " + self.path + " does not exist")

        # Check file extension
        type = self.path.split('.')[-1]
        self._tshark = self._get_tshark_path()

        if type == "tsv":
            self.parse_type = "tsv"

        elif type == "pcap" or type == "pcapng":
            if os.path.isfile(self._tshark):
                self.pcap2tsv()
                self.path += ".tsv"
                self.parse_type = "tsv"
        else:
            raise RuntimeError("[!] Kit-NET FeExtractor>_ File " + self.path + " is not a tsv or pcap file")

        if self.parse_type == "tsv":
            maxInt = sys.maxsize
            decrement = True
            while decrement:
                decrement = False
                try:
                    csv.field_size_limit(maxInt)
                except OverflowError:
                    maxInt = int(maxInt / 10)
                    decrement = True

            num_lines = sum(1 for line in open(self.path, 'rt', encoding="utf8"))
            print("[!] Kit-NET FeExtractor>_ Loading file...")
            print("[!] Kit-NET FeExtractor>_ Total " + str(num_lines) + " packets.")
            self.limit = min(self.limit, num_lines - 1)
            self.tsvinf = open(self.path, 'rt', encoding="utf8")
            self.tsvin = csv.reader(self.tsvinf, delimiter='\t')
            row = self.tsvin.__next__()

    def get_next_vector(self):
        if self.curPacketIndx == self.limit:
            if self.parse_type == 'tsv':
                self.tsvinf.close()
            return []

        # Parse next packet
        row = self.tsvin.__next__()
        IPtype = np.nan
        timestamp = row[0]
        framelen = row[1]
        srcIP = ''
        dstIP = ''

        def ipv4():
            srcIP = row[4]
            dstIP = row[5]
            IPtype = 0

        def ipv6():
            srcIP = row[17]
            dstIP = row[18]
            IPtype = 1

        def lowlevel_arp():
            srcproto = 'arp'
            dstproto = 'arp'
            srcIP = row[14]
            dstIP = row[16]
            IPtype = 0

        def lowlevel_icmp():
            srcproto = 'icmp'
            dstproto = 'icmp'
            IPtype = 0
    
        def lowlevel_other():
            srcIP = row[2]
            dstIP = row[3]
    
        FUNC_MAP = {row[4] != '': ipv4, row[17] != '': ipv6,row[12] != '': lowlevel_arp, row[10] != '': lowlevel_icmp,}
        
        FUNC_MAP[row[4] != '']()
        FUNC_MAP[row[17] != '']()

        srcproto = row[6] + row[8]  # UDP or TCP port
        dstproto = row[7] + row[9]  # UDP or TCP port
        srcMAC = row[2]
        dstMAC = row[3]

        if srcproto == '':                # For L2/L1 level protocol
            FUNC_MAP[row[12] != '']()
            FUNC_MAP[row[10] != '']()
            if srcIP + srcproto + dstIP + dstproto == '':  # For other protocol
                srcIP = row[2]  # source MAC
                dstIP = row[3]  # destination MAC

        self.curPacketIndx = self.curPacketIndx + 1

        # Extract features
        try:
            return self.nstat.updateGetStats(IPtype, srcMAC, dstMAC, srcIP, srcproto, dstIP, dstproto, int(framelen), float(timestamp))
        except Exception as e:
            print(e)
            return []

    def pcap2tsv(self):
        print("[!] Kit-NET FeExtractor>_ Parsing packet with tshark...")
        command = '"' + self._tshark + '" -r ' + self.path + " -T fields -e frame.time_epoch -e frame.len -e eth.src -e eth.dst -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport -e udp.srcport -e udp.dstport -e icmp.type -e icmp.code -e arp.opcode -e arp.src.hw_mac -e arp.src.proto_ipv4 -e arp.dst.hw_mac -e arp.dst.proto_ipv4 -e ipv6.src -e ipv6.dst -E header=y -E occurrence=f > " + self.path + ".tsv"
        subprocess.call(command, shell=True)
        print("[!] Kit-NET FeExtractor>_ Parsing complete")#". Saved as: " + self.path + ".tsv")

    def get_num_features(self):
        return len(self.nstat.getNetStatHeaders())
