#!/usr/bin/python

# Copyright 2016 Seth VanHeulen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import array
import re
import socket
import time

class Application:
    def __init__(self, host):
        self._sequence = 0
        self._payload_sent = False
        self._payload_written = False
        self._process_requested = False
        self._process = None
        self._key = None
        self._host = host

    def _read_packet(self):
        packet_header = self._socket.recv(84)
        if len(packet_header) == 0:
            return
        while len(packet_header) < 84:
            packet_header += self._socket.recv(84 - len(packet_header))
        packet_header = array.array('I', packet_header)
        packet_data = b''
        while len(packet_data) < packet_header[20]:
            packet_data += self._socket.recv(packet_header[20] - len(packet_data))
        if packet_header[3] == 0:
            if re.search(b'finishedfinished', packet_data):
                self._payload_written = True
                print('    proceed to download section')
                return
            m = re.search(b'pid: 0x([0-9a-f]{8}), pname: Festa_Ro', packet_data)
            if m:
                self._process = int(m.group(1), 16)
                print('    process id is {}'.format(self._process))
        elif packet_header[3] == 9:
            self._key = packet_data.decode().strip('\x00')
            if self._key == '':
                self._key = None

    def _send_packet(self, packet_type, command, args=[], data=b''):
        self._sequence += 1000
        packet_header = array.array('I', (0x12345678, self._sequence, packet_type, command))
        packet_header.extend(args)
        packet_header.extend([0] * (16 - len(args)))
        packet_header.append(len(data))
        self._socket.sendall(packet_header.tostring() + data)

    def run(self):
        print('connecting ...')
        self._socket = socket.create_connection((self._host, 8000))
        print('    connected to {} port {}'.format(*self._socket.getpeername()))
        self._send_packet(0, 0)
        while True:
            packet = self._read_packet()
            if self._key is not None:
                print('    key is {}'.format(self._key))
                print('use the home button to close MHX without saving')
                return
            elif not self._process_requested:
                print('getting process ...')
                self._send_packet(0, 5)
                self._send_packet(0, 0)
                self._process_requested = True
            elif self._process is not None and not self._payload_sent:
                print('writing hook ...')
                #self._send_packet(0, 10, [self._process, 0xc01e9c, 36], b'\xf0G-\xe9\x00@\xa0\xe1\xeb\xab\xf6\xeb\x08 \x94\xe5\x04\x10\x94\xe5\x04\x00\x9f\xe5p\xeb\xdb\xeb\xf0\x87\xbd\xe8\x00\xce\xe5\x00')
                self._send_packet(0, 10, [self._process, 0xc01ffc, 32], b'\xf0G-\xe9\x00@\xa0\xe1\xd7\xad\xf6\xeb\x08 \x94\xe5\x04\x10\x94\xe5\xe5\x08\xa0\xe3\x1a\xeb\xdb\xeb\xf0\x87\xbd\xe8')
                #self._send_packet(0, 10, [self._process, 0x2488e0, 4], b'm\xe5&\xeb')
                self._send_packet(0, 10, [self._process, 0x2488e8, 4], b'\xc3\xe5&\xeb')
                self._send_packet(0, 0)
                self._payload_sent = True
            elif self._payload_written and self._sequence % 5000 == 0:
                print('checking for key ...')
                self._send_packet(0, 9, [self._process, 0xe50000, 60])
                self._send_packet(0, 0)
            else:
                self._send_packet(0, 0)
            time.sleep(1)

parser = argparse.ArgumentParser(description='Gets DLC encryption key from MHX using NTR debugger.')
parser.add_argument('host', help='host name or IP address of your 3DS')
args = parser.parse_args()

app = Application(args.host)
try:
    raw_input("enabled the NTR debugger and go to the MHX main title menu, then press enter")
except:
    input("enabled the NTR debugger and go to the MHX main title menu, then press enter")
app.run()

