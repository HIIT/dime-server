import zmq
from random import choice
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://127.0.0.1:5000")
 
countries = ['netherlands','brazil','germany','portugal']
events = ['yellow card', 'red card', 'goal', 'corner', 'foul']
 
while True:
    msg = choice( countries ) +" "+ choice( events )
    print "->",msg
    socket.send( msg )
