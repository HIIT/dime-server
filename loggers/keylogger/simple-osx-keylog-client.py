import zmq
#import time
    
context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://127.0.0.1:5000")
socket.setsockopt(zmq.SUBSCRIBE, "")
 
while True:
    #time.sleep(1)
    r = socket.recv()
    print "[",r,"]", type(r), ord(r)
