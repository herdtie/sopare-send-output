#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SoPaRe plugin that sends results via unix domain socket

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

import socket
from tempfile import gettempdir
from os.path import join
import struct
import time


# keep these constants in sync with sopare-listen.py
SOCKET_FILE = join(gettempdir(), 'sopare-send-output.sock')
BUF_SIZE = 4096
MSG_FORMAT = 'LLdHHI{}s'
MSG_START_SIZE = 32    # byte required for fixed-len start of msg format
ENCODING = 'utf8'
MASK_IS_FIRST = 1
MASK_IS_LAST = 2

sock = None
msg_no = 0



def encode_msg(word, msg_no, timestamp, is_first, is_last):
    """Converts input from sopare to bytes for sending to socket."""
    # no need to convert to unicode, we are python2, so is ascii anyway
    msg_b = word.encode(ENCODING)
    msg_len = len(msg_b)
    flags = is_first * MASK_IS_FIRST + is_last * MASK_IS_LAST
    unused1 = 0    # some day make this a checksum or uid or so
    unused2 = 0    # likewise
    msg = struct.pack(MSG_FORMAT.format(msg_len), msg_no, msg_len, timestamp,
                      flags, unused1, unused2, msg_b)
    if len(msg) < BUF_SIZE:
        return msg

    # message is too long!
    # TODO: could split and send chunks, incrementing msg_no here
    print('WARN message is too long ({}), try sending half of it'
          .format(len(msg)))
    return encode_msg(word[:(len(word)-1)/2], timestamp, is_first, is_last)


def run(readable_results, data, rawbuf):
    """Called when sopare has detected familiar input."""
    global sock
    global msg_no

    timestamp = time.time()
    words = [word for word in readable_results if word]   # eliminate empty words
    n_words = len(words)
    for idx, word in enumerate(words):
        msg = encode_msg(word, msg_no, timestamp, idx==0, idx==n_words-1)
        try:
            sock.sendto(msg, SOCKET_FILE)
            print('Sent message number {}: "{}"'.format(msg_no, word))
        except socket.error:
            print('WARN Failed to write to socket, maybe no-one is listening?')
        msg_no += 1


def init():
    """Called when importing this file. Initializes socket."""
    global sock
    global msg_no

    print('Initializing socket at {}'.format(SOCKET_FILE))
    sock = socket.socket(family=socket.AF_UNIX,
                         type=socket.SOCK_DGRAM)     # UDP
    msg_no = 0


# call init() when importing this
init()
