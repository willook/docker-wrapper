import zmq
import gym
import pickle

''' Define your environment '''
env = gym.make('Breakout-v0')



context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    recv_packet = socket.recv()
    command, args = pickle.loads(recv_packet)
    print(command, args)
    assert type(command) is str, "command should be str"
    assert type(args) is tuple, "args should be tuple"
    
    returns = None
    if command == 'reset':
        returns = env.reset(*args) if args else env.reset()
    elif command == 'step':
        returns = env.step(*args) if args else env.step()
    else:
        returns = None
    
    send_packet = pickle.dumps(returns)
    
    socket.send(send_packet)