#!/usr/bin/env python3
# -*- coding: utf_8 -*-

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

# network performance tester - client/server

import libnetperf

# handle arguments
import argparse
parser = argparse.ArgumentParser(description='Test network performance')

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-s', '--server', 
                    type=str,
                    nargs=1,
                    help='Server mode: IP address or subnet to listen on',
)
group.add_argument('-c', '--client', 
                    type=str,
                    nargs=1,
                    help='Client mode: IP address or subnet to connect to',
)

parser.add_argument('-b', '--buffer',
                    type=str,
                    default='32K',
                    help='Network read/write buffer size in bytes (optional K or M suffix)',
)

parser.add_argument('-k', '--chunk',
                    type=str,
                    default='256M',
                    help='Network throughput test chunk size in Mbytes (optinal M or G suffix)',
)

parser.add_argument('-p', '--parallel',
                    type=int,
                    default=32767,
                    help='Maximum number of parallel threads to test',
)

parser.add_argument('-m', '--min-parallel',
                    type=int,
                    default=1,
                    help='Minimum number of parallel threads to test',
)

parser.add_argument('-i', '--parallel-skip',
                    type=str,
                    default=list(libnetperf.skip_actions.keys())[0],
                    choices=libnetperf.skip_actions.keys(),
                    help='Skip mode between min and max parallel',
)

parser.add_argument('-t', '--tests',
                    type=str,
                    default=list(libnetperf.test_actions.keys()),
                    nargs='*',
                    choices=libnetperf.test_actions.keys(),
                    help='Which tests to run',
)

parser.add_argument('-u', '--udp',
                    default=False,
                    action='store_true',
                    help='Use UDP protocol instead of TCP',
)

parser.add_argument('-o', '--port',
                    type=int,
                    default=12311,
                    help='TCP or UDP port to communicate on',
)

args = parser.parse_args()

buffer_arg = args.buffer
buffer_last_char = buffer_arg[-1:]
if buffer_last_char.isdigit():
    buffer=int(buffer_arg)
else:
    if buffer_last_char=='K':
        buffer=int(buffer_arg[:-1])*1024
    elif buffer_last_char=='M':
        buffer=int(buffer_arg[:-1])*1024*1024
    else:
        raise ValueError('Buffer must be in bytes, or with a K or M suffix')

chunk_arg = args.chunk
chunk_last_char = chunk_arg[-1:]
if chunk_last_char.isdigit():
    chunk=int(chunk_arg)
else:
    if chunk_last_char=='K':
        chunk=int(chunk_arg[:-1])*1024
    elif chunk_last_char=='M':
        chunk=int(chunk_arg[:-1])*1024*1024
    elif chunk_last_char=='G':
        chunk=int(chunk_arg[:-1])*1024*1024*1024
    else:
        raise ValueError('Chunk must be in bytes, or with a K, M or G suffix')

if buffer > chunk:
    buffer = chunk

import ipaddress
if __name__ == '__main__':
    if args.server != None:
        # i'm a server - most of the smarts is in the client
        listen_address = ipaddress.ip_network(args.server[0], strict=True)
        server = libnetperf.Server(listen_address, args.udp, args.port)

    if args.client != None:
        # i'm a client
        connect_address = ipaddress.ip_network(args.client[0], strict=True)
        client = libnetperf.Client(connect_address, buffer, chunk, args.parallel, args.min_parallel, args.parallel_skip, args.tests, args.udp, args.port)
