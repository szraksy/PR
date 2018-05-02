# -*- coding: utf-8 -*-
"""
Created on Wed May 02 16:46:47 2018

@author: Sezer
"""

import socket
import threading

bind_ip="0.0.0.0"
bind_port=10002
server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((bind_ip,bind_port))
server.listen(5)
print " Server is listening on %s:%d" % (bind_ip,bind_port)

def handle_client(client_socket):
     request=client_socket.recv(1024)
     print "Received Message : %s" % request
     client_socket.send(" Your message has been delivered")
     client_socket.close()
while True:
     client,addr = server.accept()
     client_handler=threading.Thread(target=handle_client,args=(client,))
     client_handler.start()