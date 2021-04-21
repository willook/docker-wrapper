import numpy as np
from docker_wrapper import DockerizedEnv

# option 1, if you use several projects in workspace
volume_path = "/home/willook/workspace"
node_path = "docker-wrapper/atari_node.py"

# option 2
volume_path = "/home/willook/workspace/docker-wrapper"
node_path = "atari_node.py"
        
env = DockerizedEnv(volume_path, node_path)
observation = env.reset()

print(observation.shape)

for i in range(5):
    action = 0
    observation, reward, done, info = env.step(action)

    print("action", action)
    print("observation", np.array(observation).shape)
    print("reward", reward)
    print("done", done)
    print("info", info)
    print()
    
    
