#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# File: osc4py3/as_comthreads.py
# <pep8 compliant>
"""Use of osc4py3 in own created threads for communication.

Functions defined here allow to use OSC with a mixed scheduling whehre
communications and encoding/decoding are realized in background
threads, but methods calls are processed in an event loop.
"""

from . import oscscheduling
from . import oscdispatching
from . import oscchannel
from . import oscmethod
from . import osctoolspools
from . import oscdistributing
from . import as__common                 # All doc strings are shared here.

# Useful methods of this module.
__all__ = [
    "osc_startup",
    "osc_terminate",
    "osc_process",
    "osc_method",
    "osc_send",
    "osc_udp_server",
    "osc_udp_client",
    ]

dispatcher = None
generallogger = None
execute_worker = None


def osc_startup(**kwargs):
    global dispatcher, generallogger, execute_worker
    if dispatcher is not None:
        return

    if 'logger' in kwargs:
        generallogger = kwargs['logger']

    dispatcher = oscdispatching.Dispatcher("global", {
                    "logger": generallogger,
                    })
    oscdispatching.register_global_dispatcher(dispatcher)
    # This monitoring thread will look at sockets.
    oscscheduling.get_global_socket_monitor(generallogger)
    # This thread will get, decode and process received raw packets.
    oscdistributing.create_rawpackets_thread(generallogger)
    # This thread will encode and transmit packets to send.
    oscdistributing.create_sendingpackets_thread(generallogger)
    # This thread will process delayed bundles.
    oscdispatching.create_delayed_thread(generallogger)

    # To execute methods in the process context.
    execute_worker = osctoolspools.WorkQueue()


def osc_terminate():
    global dispatcher, manager, execute_worker
    if dispatcher is None:
        return

    execute_worker.terminate()
    execute_worker = None

    oscscheduling.terminate_global_socket_monitor()
    oscscheduling.terminate_global_polling_monitor()
    oscdistributing.terminate_sendingpackets_thread()
    oscdistributing.terminate_rawpackets_thread()
    oscdispatching.terminate_delayed_thread()
    oscdispatching.unregister_global_dispatcher()
    dispatcher = None


def osc_process():
    while True:
        job = execute_worker.wait_for_job(0)
        if job is osctoolspools.LAST_JOB or job is None:
            break
        try:
            job()
        except:
            generallogger.exception("Failure in method execution job")


def osc_method(addrpattern, function, argscheme=oscmethod.OSCARG_DATAUNPACK, extra=None):
    # Important: specify the workqueue to really process methods in the
    # context of osc_process() call.
    apf = oscmethod.MethodFilter(addrpattern, function, logger=generallogger,
                        workqueue=execute_worker, argscheme=argscheme,
                        extra=extra)
    oscdispatching.register_method(apf)


def osc_send(packet, names):
    oscdistributing.send_packet(packet, names)


def osc_udp_server(address, port, name):
    from . import oscudpmc   # Only import if necessary.

    chan = oscudpmc.UdpMcChannel(name, "r",
            {
            'udpread_host': address,
            'udpread_port': port,
            'monitor': oscchannel.SCHED_SELECTTHREAD,
            'auto_start': True,     # The channel will automaticaly register
                                    # with monitor..
            'logger': generallogger,
            })


def osc_udp_client(address, port, name):
    global channels

    from . import oscudpmc   # Only import if necessary.

    chan = oscudpmc.UdpMcChannel(name, "w",
            {
            'udpwrite_host': address,
            'udpwrite_port': port,
            "udpwrite_nonblocking": True,
            'monitor': oscchannel.SCHED_SELECTTHREAD,
            'auto_start': True,
            'logger': generallogger,
            })


def osc_multicast_server(address, port, name):
    from . import oscudpmc   # Only import if necessary.

    chan = oscudpmc.UdpMcChannel(name, "r",
            {
            'udpread_host': address,
            'udpread_port': port,
            'monitor': oscchannel.SCHED_SELECTTHREAD,
            'auto_start': True,
            'mcast_enabled': True,
            'logger': generallogger,
            })


def osc_multicast_client(address, port, name, ttl=1):
    from . import oscudpmc   # Only import if necessary.

    chan = oscudpmc.UdpMcChannel(name, "w",
            {
            'udpwrite_host': address,
            'udpwrite_port': port,
            'udpwrite_ttl': ttl,
            "udpwrite_nonblocking": True,
            "write_workqueue": write_worker,
            'monitor': oscchannel.SCHED_SELECTTHREAD,
            'auto_start': True,
            'mcast_enabled': True,
            'logger': generallogger,
            })


def osc_broadcast_server(address, port, name):
    global channels

    from . import oscudpmc   # Only import if necessary.

    chan = oscudpmc.UdpMcChannel(name, "r",
            {
            'udpread_host': address,
            'udpread_port': port,
            'monitor': oscchannel.SCHED_SELECTTHREAD,
            'auto_start': True,
            'bcast_enabled': True,
            'logger': generallogger,
            })


def osc_broadcast_client(address, port, name, ttl=1):
    from . import oscudpmc   # Only import if necessary.

    chan = oscudpmc.UdpMcChannel(name, "w",
            {
            'udpwrite_host': address,
            'udpwrite_port': port,
            'udpwrite_ttl': ttl,
            "udpwrite_nonblocking": True,
            "write_workqueue": write_worker,
            'monitor': oscchannel.SCHED_SELECTTHREAD,
            'auto_start': True,
            'bcast_enabled': True,
            'logger': generallogger,
            })


as__common.apply_docs(globals())
