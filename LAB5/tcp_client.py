# -*- coding: utf-8 -*-
"""
Created on Wed May 02 16:46:27 2018

@author: Sezer
"""
import socket
target_host=input('Enter the target host')
target_port=input('Enter the target port')
client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((target_host,target_port))
message=input('Enter your message')
client.send(message)
response=client.recv(4096)
print response