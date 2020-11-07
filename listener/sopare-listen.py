#!/usr/bin/env python3

"""
Listen to recognized sound patterns sent via plugin from sopare.
"""

import socket
import struct
from tempfile import gettempdir
from argparse import ArgumentParser
import os
from os.path import join, exists
from datetime import datetime as dt


# constants need to be kept in sync with sopare plugin send_output
# todo: create file that both can import
SOCKET_FILE = join(gettempdir(), 'sopare-send-output.sock')
BUF_SIZE = 4096
MSG_FORMAT = 'LLdHHI{}s'
MSG_START_SIZE = 32    # byte required for fixed-len start of msg format
ENCODING = 'utf8'
MASK_IS_FIRST = 1
MASK_IS_LAST = 2



def decode_msg(msg, expect_no):
    """Extract message from byte-representation; checks things."""
    # extract info
    msg_no, msg_len, timestamp, flags, unused1, unused2 = \
            struct.unpack(MSG_FORMAT[:6], msg[:MSG_START_SIZE])
    text_b = struct.unpack(MSG_FORMAT.format(msg_len), msg)[-1]

    # run some checks
    if unused1 != 0 or unused2 != 0:
        print('WARN message from future implementation it seems')
    if msg_no != expect_no:
        print('WARN Seem to have missed messages. Received no {} '
              'but expected no {}'.format(msg_no, expect_no))
    return text_b.decode(ENCODING), msg_no, dt.fromtimestamp(timestamp), \
            (flags & MASK_IS_FIRST) > 0, (flags & MASK_IS_LAST) > 0


def main():
    """
    Main function, called when running this as script.

    Parses args, creates socket, calls appropriate other main_*.
    """
    # parse cmd line args
    parser = ArgumentParser()
    args = parser.parse_args()

    # create socket
    sock = None
    did_bind = False
    expect_no = 0
    try:
        print('Creating socket')
        sock = socket.socket(family=socket.AF_UNIX,
                             type=socket.SOCK_DGRAM)   # UDP
        print(f'Binding to socket file {SOCKET_FILE}')
        sock.bind(SOCKET_FILE)
        did_bind = True     # this means we created the file
        print('Listening for data...')
        while True:
            msg, sender = sock.recvfrom(BUF_SIZE)
            word, msg_no, timestamp, is_first, is_last = \
                    decode_msg(msg, expect_no)
            print(f'Received message {msg_no} from {timestamp} '
                  f'(first={is_first}, last={is_last}): {word}')
            expect_no = msg_no + 1
    except KeyboardInterrupt:
        print('Stopped by user')
    finally:
        if sock is not None:
            print('Closing socket')
            sock.close()
        if did_bind and exists(SOCKET_FILE):
            print('Removing socket file')
            os.unlink(SOCKET_FILE)    # we have created it
    return 0


if __name__ == '__main__':
    main()
