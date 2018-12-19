#!/usr/bin/env python3
# -*- coding: utf_8 -*-

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

# libnetperf: the heavy lifting for netperf testing
import ipaddress
import multiprocessing
import asyncio
import socket
import uuid
import datetime

def skip_p1(min,max):
    # add 1 and return
    return list(range(min,max + 1))

def skip_x2(min,max):
    # n^2 exponential skip
    
    if min == max:
        return [max]

    range = []
    if min == 1:
        min = 0
    else:
        range.append(min)
    i=1
    while min + i <= max:
        range.append(min + i)
        i = i * 2

    if min + i != max:
        range.append(max)

    return range

def skip_1235(min,max):
    # skip in the pattern of 1,2,3,5,10,20,50,100 etc

    if min == max:
        return [max]

    range = []
    if min == 1:
        min = 0
    else:
        range.append(min)
    o_sel=1
    x_mul=0
    i=o_sel * (10 ** x_mul)
    while min + i <= max:
        range.append(min + i)
        if o_sel == 1:
            o_sel = 2
        elif o_sel == 2:
            o_sel = 3
        elif o_sel == 3:
            o_sel = 5
        elif o_sel == 5:
            o_sel = 1
            x_mul = x_mul + 1
        i=o_sel * (10 ** x_mul)

    if min + i != max:
        range.append(max)

    return range

def skip_fib(min,max):
    # skip in the fibonacci pattern

    if min == max:
        return [max]

    range = []
    if min == 1:
        min = 0
    else:
        range.append(min)
    last=1
    i=1
    while min + i <= max:
        range.append(min + i)
        j = i
        i = i + last
        last = j

    if min + i != max:
        range.append(max)
    
    return range

class Server():
    def __init__(self, listen_address, udpmode, port):
        # start a new listener in a new process on every address
        self.listen_address = listen_address
        self.udpmode = udpmode
        self.port = port

        print("I'm a server, listening on:")
        print(self.listen_address)
        self.server_procs = []
        for addr in ipaddress.ip_network(self.listen_address):
            p = multiprocessing.Process(target=self._Run(addr), daemon=False)
            p.start()
            self.server_procs.append(p)
    def _Run(self, addr):
        if self.udpmode:
            asyncio.run(self._StartUdp(addr))
        else:
            asyncio.run(self._StartTcp(addr))
    async def _StartTcp(self, addr):
        self.server = await asyncio.start_server(self._HandleTcp,host=str(addr),port=self.port)
        async with self.server:
            await self.server.serve_forever()
    async def _StartUdp(self, addr):
        pass
    async def _HandleTcp(self, reader, writer):
        hello = await reader.readline()
        current_datetime = datetime.datetime.utcnow()

        request_timestamp, request_uuid, request_command, request_buff, request_chunk = hello.decode().split('**')
        request_datetime = datetime.datetime.fromisoformat(request_timestamp)
        recv_network_latency = current_datetime - request_datetime

        if request_command not in test_actions.keys():
            writer.write('{}**{}**{}**{}**{}\n'.format(current_datetime.isoformat(), request_uuid, 'ERROR', 'FAIL', 'Unknown request command "{}"'.format(request_command)).encode())
            await writer.drain()
            writer.close()
        else:
            test_actions[request_command][0](reader,writer,current_datetime,request_uuid,request_buff,request_chunk)
            await writer.drain()
            writer.close()
    async def _HandleUdp(self, reader, writer):
        pass

class Client():
    def __init__(self, connect_address, buffer, chunk, parallel, min_parallel, iterator, tests, udpmode, port):
        self.buffer = buffer
        self.chunk = chunk
        self.iterator = skip_actions[iterator]
        self.tests = tests
        self.udpmode = udpmode
        self.port = port

        self.client_procs = []

        for test in self.tests:
            for in_parallel in self.iterator(min_parallel, parallel):
                running = 0
                while running < in_parallel:
                    for addr in ipaddress.ip_network(connect_address):
                        running = running + 1
                        p = multiprocessing.Process(target=self._Run(addr,test), daemon=True)
                        p.start()
                        self.client_procs.append(p)
                        if running >= in_parallel:
                            break
                for job in self.client_procs:
                    job.join()
                self.client_procs = []

    def _Run(self, addr, test):
        if self.udpmode:
            pass
        else:
            sock = socket.create_connection((str(addr),self.port),10)
            test_actions[test][1](sock,self.buffer,self.chunk)
            sock.close()


def s_test_download(reader, writer, current_datetime, uuid, buff, chunk):
    # test downloads
    pass

def c_test_download(sock, buff, chunk):
    # test downloads
    pass

def s_test_upload(reader, writer, current_datetime, uuid, buff, chunk):
    # test uploads
    pass

def c_test_upload(sock, buff, chunk):
    # test uploads
    pass

def s_test_bidir(reader, writer, current_datetime, uuid, buff, chunk):
    # test both ways simultaneously
    pass

def c_test_bidir(sock, buff, chunk):
    # test both ways simultaneously
    pass

def s_test_ping(reader, writer, current_datetime, uuid, buff, chunk):
    # test latency
    writer.write('{}**{}**{}**{}**{}\n'.format(current_datetime.isoformat(),uuid,'PING','OK', 'Ping reply').encode())

def c_test_ping(sock, buff, chunk):
    # test latency
    send_datetime = datetime.datetime.utcnow()
    sock.sendall('{}**{}**{}**{}**{}\n'.format(send_datetime.isoformat(),uuid.uuid4(),'PING',0,0).encode())
    data = sock.recv(buff)
    recv_datetime = datetime.datetime.utcnow()
    latency = recv_datetime - send_datetime
    print('Send time: {}'.format(send_datetime.isoformat()))
    print('Recv time: {}'.format(recv_datetime.isoformat()))
    print('Time delta (network latency +/- clock sync): {}'.format(latency))
    response_timestamp, request_uuid, request_command, request_status, status_info = data.decode().split('**')

test_actions = {
        'DOWN':[s_test_download,c_test_download],
        'UP':[s_test_upload,c_test_upload],
        'BIDI':[s_test_bidir,c_test_bidir],
        'PING':[s_test_ping,c_test_ping],
    }

skip_actions = {
        '+1':skip_p1,
        'x2':skip_x2,
        '+1-2-3-5-10':skip_1235,
        'fibonacci':skip_fib,
    }
