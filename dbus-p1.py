#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import sys, os
import signal
from dbus.mainloop.glib import DBusGMainLoop
import dbus
import gobject
from threading import Thread
import traceback

import logging
logging.basicConfig(level=logging.INFO)

# Victron packages
sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'ext', 'velib_python'))
from vedbus import VeDbusService

# SmartMeter package
sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'ext', 'smeterd', 'smeterd'))
from meter import SmartMeter, P1PacketError

VERSION = '0.1'
TTY = '/dev/ttyUSB0'

def main():
    DBusGMainLoop(set_as_default=True)

    m = SmartMeter(TTY, baudrate=115200)

    service = VeDbusService("com.victronenergy.gasmeter")

    # Add objects required by ve-api
    service.add_path('/Management/ProcessName', __file__)
    service.add_path('/Management/ProcessVersion', VERSION)
    service.add_path('/Management/Connection', TTY)
    service.add_path('/DeviceInstance', 0)
    service.add_path('/ProductId', 0)
    service.add_path('/ProductName', 'gasmeter')
    service.add_path('/Connected', 1)

    # Add readings
    service.add_path('/Meter', value=None)

    def poll(mainloop):
        try:
            # Hide the endless output of logs
            logging.getLogger('meter').setLevel(logging.WARNING)

            while True:
                try:
                    p = m.read_one_packet()
                except P1PacketError:
                    # ignore the (hopefully occassional) crc error
                    continue

                service['/Meter'] = p['gas']['total']

        except:
            traceback.print_exc()
            mainloop.quit()

    # Need to run the serial port in separate thread. Pass in the mainloop so
    # the thread can kill us if there is an exception.
    gobject.threads_init()
    mainloop = gobject.MainLoop()

    poller = Thread(target=lambda: poll(mainloop))
    poller.daemon = True
    poller.start()

    # Save counter on shutdown
    signal.signal(signal.SIGTERM, lambda *args: sys.exit(0))

    try:
        mainloop.run()
    except KeyboardInterrupt:
        pass
    finally:
        pass
        # save_counters()


if __name__ == "__main__":
    main()
