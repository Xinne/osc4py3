#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# File: osc4py3/demos/rundemo.py
# <pep8 compliant>
help = """
Common demo script - the same script, with different scheduling options.

Usage: ./rundemo.py as_eventloop
            To run the whole osc process in a single event loop.
   or  ./rundemo.py as_allthreads
            To run all in ad-hoc threads.
   or  ./rundemo.py as_comthreads
            To run communications (read/write, encoding, pattern matching) in
            threads, but have OSC methods called in the event loop context.

Add a parameter nolog to avoid creation of the debugging logger.
"""

import sys
import threading
import logging

if len(sys.argv) < 2 or sys.argv[1] not in ('as_eventloop',
                                            'as_allthreads',
                                            'as_comthreads'):
    print(help)
    sys.exit()

# Make osc4py3 available.
from os.path import abspath, dirname
PACKAGE_PATH = dirname(dirname(dirname(abspath(__file__))))
if PACKAGE_PATH not in sys.path:
    sys.path.insert(0, PACKAGE_PATH)
import time

# <<<<<<<<<<<<<<<<<<<<<<<<<<< osc4py3 imports <<<<<<<<<<<<<<<<<<<<<<<<<<<
from osc4py3 import oscbuildparse       # <<<<< Needed to create OSC messages.
#from osc4py3.as_xxxx import *          # <<<<< Make functions available.
# <<<<<<<<<<<<<<<<<<<<<<<<<<< osc4py3 imports <<<<<<<<<<<<<<<<<<<<<<<<<<<
# The previous commented import is done dynamically here with command-line
# parameter:
print("Importing functions from osc4py3 interface:", sys.argv[1])
_fctslist = [
    # Same as __all__ of as_xxx modules.
    "osc_startup",
    "osc_terminate",
    "osc_process",
    "osc_method",
    "osc_send",
    "osc_udp_server",
    "osc_udp_client",
    ]
_itfmod = __import__("osc4py3." + sys.argv[1], globals(), fromlist=_fctslist)
for _fct in _fctslist:
    globals()[_fct] = getattr(_itfmod, _fct)

# Logging for test/debug.
if "nolog" in sys.argv[1:]:
    logger = None
else:
    from demoslogger import logger

# Parameters for a local UDP server, contacted by out own client.
IP = "127.0.0.1"
PORT = 6503

# Numbering of messages(inserted as message parameter).
msgcount = 0


# The function called to handle matching messages.
hlock = threading.Lock()
hcount = 0
def handlerfunction(*args):
    global hlock, hcount
    with hlock:
        hcount += 1
        if logger and logger.isEnabledFor(logging.INFO):
            logger.info("##### %d handler function called with: %r",
                    hcount, args)
        else:
            print("##### {} handler function called with: {!r}".format(hcount
            , args))

# <<<<<<<<<<<<<<<<<<<<<<<<<<< osc4py3 setup <<<<<<<<<<<<<<<<<<<<<<<<<<<<<
osc_startup(logger=logger)              # <<<<< Start needed services.
osc_udp_server(IP, PORT, "udplisten")   # <<<<< Create UDP server channel.
osc_udp_client(IP, PORT, "udpclient")   # <<<<< Create peer to reach via UDP.

osc_method("/test", handlerfunction)    # <<<<< Register method handler(s).
# <<<<<<<<<<<<<<<<<<<<<<<<<<< osc4py3 setup <<<<<<<<<<<<<<<<<<<<<<<<<<<<<

finished = False
while not finished:
    print("\n" + time.asctime())
    print("""Au menu
    S-simple send message
    M-multiple (5 calls) send message
    B-simple send bundle (3 messages) with immediate timetag
    F-future send bundle (3 messages) with timetag now+10 sec
    L-local dispatch send message
    K-multiple (100 calls) local dispatch send message
    A-all targets send message
    Q-quit
    """)
    act = input("Action:")
    if act:
        act = act[0].lower()
        if act == 'q':
            finished = True
        elif act == 's':
            msgcount += 1
            msg = oscbuildparse.OSCMessage("/test/here", ",si",
                    ["message", msgcount])
            #<<<<<<<<<<<<<<<< osc4py3 send message <<<<<<<<<<<<<<<<<<<<<<
            osc_send(msg, "udpclient")
            #<<<<<<<<<<<<<<<< osc4py3 send message <<<<<<<<<<<<<<<<<<<<<<
        elif act == 'm':
            for n in range(5):
                msgcount += 1
                msg = oscbuildparse.OSCMessage("/test/multiple/" + \
                        str(msgcount), ",sii",
                        ["nth message", n + 1, msgcount])
                osc_send(msg, "udpclient")
        elif act == 'b':
            msg1 = oscbuildparse.OSCMessage("/test/here", None,
                    ["immediate message in bundle", msgcount])
            msg2 = oscbuildparse.OSCMessage("/test/2", None,
                    ["Nice weather"])
            msg3 = oscbuildparse.OSCMessage("/test/yes", None,
                    ["Yes, sunny, but cold"])
            bun = oscbuildparse.OSCBundle(
                    oscbuildparse.OSC_IMMEDIATELY,
                    [msg1, msg2, msg3])
            osc_send(bun, "udpclient")
        elif act == 'f':
            exectime = time.time() + 10   # execute in 10 seconds
            msg1 = oscbuildparse.OSCMessage("/test/here", None,
                    ["timed message in bundle", msgcount, exectime])
            msg2 = oscbuildparse.OSCMessage("/test/2", None,
                    ["Hello You"])
            msg3 = oscbuildparse.OSCMessage("/test/yes", None,
                    ["Its time to go"])
            bun = oscbuildparse.OSCBundle(
                    oscbuildparse.unixtime2timetag(exectime),
                    [msg1, msg2, msg3])
            osc_send(bun, "udpclient")
        elif act == 'l':
            msgcount += 1
            msg = oscbuildparse.OSCMessage("/test/locally", None,
                    ["a local dispatched message", msgcount])
            osc_send(msg, "_local")
        elif act == 'k':
            for i in range(100):
                msgcount += 1
                msg = oscbuildparse.OSCMessage("/test/locally", None,
                        ["a local dispatched message", msgcount])
                osc_send(msg, "_local")
        elif act == 'a':
            msgcount += 1
            msg = oscbuildparse.OSCMessage("/test/forall", None,
                    ["a message for all targets", msgcount])
            osc_send(msg, "_all")

    # <<<<<<<<<<<<<<<<<<<<<<< osc4py3 in-main processing <<<<<<<<<<<<<<<<
    osc_process()                       # <<<<< Process OSC in the loop.
    # <<<<<<<<<<<<<<<<<<<<<<< osc4py3 in-main processing <<<<<<<<<<<<<<<<

# <<<<<<<<<<<<<<<<<<<<<<<<<<< osc4py3 termination <<<<<<<<<<<<<<<<<<<<<<<
osc_terminate()                         # <<<<< Terminate OSC stuff.
# <<<<<<<<<<<<<<<<<<<<<<<<<<< osc4py3 termination <<<<<<<<<<<<<<<<<<<<<<<
