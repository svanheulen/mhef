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
import base64
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
        self._id = None
        self._object1 = 0
        self._object2 = 0
        self._key = None
        self._pubkey = None
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
            m = re.search(b'pid: 0x([0-9a-f]{8}), pname: Festa_Ro, tid: ([0-9a-f]{16}), ', packet_data)
            if m:
                self._process = int(m.group(1), 16)
                self._id = m.group(2)
                print('    process id is {}'.format(self._process))
        elif packet_header[3] == 9:
            if self._object1 == 0:
                self._object1 = array.array('I', packet_data)[0]
            elif self._object2 == 0:
                self._object2 = array.array('I', packet_data)[0]
            elif self._key is None:
                self._key = packet_data.decode().strip('\x00')
                if self._key == '':
                    self._key = None
                elif self._id == b'0004000000155400':
                    print('    MHX JPN key = {}'.format(self._key))
                elif self._id == b'0004000000187000':
                    print('    MHGen USA key = {}'.format(self._key))
                elif self._id == b'0004000000185b00':
                    print('    MHGen EUR key = {}'.format(self._key))
            elif self._pubkey is None and self._id != b'0004000000155400':
                self._pubkey = packet_data.strip(b'\x00')
                if self._pubkey == b'':
                    self._pubkey = None
                elif self._id == b'0004000000187000':
                    print('    MHGen USA pubkey = {}'.format(base64.b64encode(self._pubkey).decode()))
                elif self._id == b'0004000000185b00':
                    print('    MHGen EUR pubkey = {}'.format(base64.b64encode(self._pubkey).decode()))

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
            if not self._process_requested:
                print('getting process ...')
                self._send_packet(0, 5)
                self._send_packet(0, 0)
                self._process_requested = True
            elif self._process and self._sequence % 5000 == 0:
                if self._object1 == 0:
                    print('checking for object 1 ...')
                    if self._id == b'0004000000155400':
                        self._send_packet(0, 9, [self._process, 0xdba8f4, 4])
                    else:
                        self._send_packet(0, 9, [self._process, 0xda28f4, 4])
                elif self._object2 == 0:
                    print('checking for object 2 ...')
                    self._send_packet(0, 9, [self._process, self._object1 + 0x34, 4])
                elif self._key is None:
                    print('checking for key ...')
                    if self._id == b'0004000000155400':
                        self._send_packet(0, 9, [self._process, self._object2 + 0x2a1, 128])
                    else:
                        self._send_packet(0, 9, [self._process, self._object2 + 0x5a0, 128])
                elif self._pubkey is None and self._id != b'0004000000155400':
                    print('checking for pubkey ...')
                    self._send_packet(0, 9, [self._process, self._object2 + 0x6b0, 294])
                else:
                    return
                self._send_packet(0, 0)
            else:
                self._send_packet(0, 0)
            time.sleep(1)

parser = argparse.ArgumentParser(description='Gets DLC encryption key from MHX using NTR debugger.')
parser.add_argument('host', help='host name or IP address of your 3DS')
args = parser.parse_args()

app = Application(args.host)
try:
    raw_input("enabled the NTR debugger and go to the MHX/Gen download section, then press enter")
except:
    input("enabled the NTR debugger and go to the MHX/Gen download section, then press enter")
app.run()

