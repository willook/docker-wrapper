import os
import pickle

import zmq
import docker
from multiprocessing import Queue
from threading import Thread


class DockerExecutor(Thread):
    def __init__(self, volume_path:str, node_path:str, queue:Queue):
        '''
        args
            volume_path : Volume you want to share
            node_path   : Path of node starting after volume_path
            ex) /home/user/workspace/project1/env_node.py
                volume_path = /home/user/workspace
                node_path = project1/env_node.py
        '''
        super(DockerExecutor, self).__init__()
        self.volume_path = volume_path
        
        self.node_basename = os.path.basename(node_path)
        container_path = "/workspace"
        node_dirpath = os.path.dirname(node_path)
        self.node_dirpath = os.path.join(container_path, node_dirpath)
        self.queue = queue
        
    def run(self):
        client = docker.from_env()
        command = f"sh -c 'cd {self.node_dirpath}; python {self.node_basename}'"
        self.container = client.containers.run("realbx:latest",
                                    command= command,
                                    tty = True,
                                    auto_remove=True,
                                    network ="keai",
                                    user = "user",
                                    volumes = {self.volume_path: {'bind': '/workspace'}},
                                    detach = True)
        try:
            self.queue.put(self.container.id[:12])
            output_streams = self.container.attach(stream=True)
            for line in output_streams:
                print(f"[container]", line.decode().strip())
        except Exception as err:
            print(err)
        finally:
            print("kill container...")
            self.container.kill()
    
    def __del__(self):
        self.container.kill()


class Coordinator():
    def __init__(self, ip:str, port:int = 5555):
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect(f"tcp://{ip}:{port}")
        
    def send_command_get_returns(self, command:str, args:tuple = ()):
        send_packet = pickle.dumps((command, args))
        self.socket.send(send_packet)
        
        recv_packet = self.socket.recv()
        returns = pickle.loads(recv_packet)
        return returns
        

class DockerizedEnv():
    def __init__(self, volume_path:str, node_path:str):
        # initialize docker container
        
        queue = Queue(maxsize=1)
        process = DockerExecutor(volume_path, node_path, queue)
        process.daemon = True
        process.start()
        
        # establish communication
        ip = queue.get(block=True)
        self.coord = Coordinator(ip)

    def reset(self):
        return self.coord.send_command_get_returns(command="reset")

    def step(self, action):
        return self.coord.send_command_get_returns(command="step", args = (action,))