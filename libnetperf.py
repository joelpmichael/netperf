#!/usr/bin/env python3
# -*- coding: utf_8 -*-

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

# libnetperf: the heavy lifting for netperf testing

def skip_p1(min,max):
    # add 1 and return
    return list(range(min,max + 1))

def skip_x2(min,max):
    # multiply by 2 and return
    
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
    pass

class Client():
    pass

def test_download(mode,socket):
    # test downloads
    pass

def test_upload(mode,socket):
    # test uploads
    pass

def test_bidir(mode,socket):
    # test both ways simultaneously
    pass

def test_latency(mode,socket):
    # test latency
    pass

test_actions = {'DOWN':test_download,'UP':test_upload,'BIDI':test_bidir,'LATENCY':test_latency}
skip_actions = {'+1':skip_p1, 'x2':skip_x2, '+1-2-3-5-10':skip_1235, 'fibonacci':skip_fib}

