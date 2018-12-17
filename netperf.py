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
                    help='Skip mode between min and max parallel - 1=i+1; 2=i*2; 3=i+1,2,3,5,10; 4=fibonacci',
)

parser.add_argument('-t', '--tests',
                    type=str,
                    default=libnetperf.test_actions.keys(),
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

print(args)

print(libnetperf.skip_actions[args.parallel_skip](args.min_parallel, args.parallel))

if args.server != None:
    # i'm a server
    listen_address = args.server[0]
    print("I'm a server, listening on:")
    print(listen_address)
    server = libnetperf.Server()

if args.client != None:
    # i'm a client
    connect_address = args.client[0]
    print("I'm a client, connecting to:")
    print(connect_address)
    client = libnetperf.Client()
