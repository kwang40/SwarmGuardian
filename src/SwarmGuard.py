import time
import subprocess
import json
import os

SLEEP_SECS = 5
DESIRED_MANAGER = 3
data_centers = dict()
CONFIG_PATH = 'config.json'
POLICY = 0 # 0 is Fault-tolerant(By default) 1 is Performance


# parser.add_argument(
#     '--k', type = int, default = 5,
#     help = '',
# )

def main():
    #init()
    run()
    
def init():
    with open(CONFIG_PATH, 'r') as f:
        data = json.load(f)
    
    global SLEEP_SECS
    SLEEP_SECS = data['SLEEP_SECS']
    global DESIRED_MANAGER
    DESIRED_MANAGER = data['DESIRED_MANAGER']
    global POLICY
    POLICY = data['POLICY']
    pass

def run():
    while True:
        swarmGuardian()
        time.sleep(SLEEP_SECS)

def isDead(status):


def swarmGuardian():
    global data_centers
    # run swarm node ls to show all nodes status
    proc = subprocess.Popen(["sudo", "docker", "node", "ls"], stdout=subprocess.PIPE)
    # split to different nodes
    nodes_status = proc.stdout.read().split('\n')    
    # update datacenter dict
    dead_managers = []
    live_managers = 0
    live_managers_center = dict()
    leaderID = ""
    selfID = ""
    for node in nodes_status[1:]:
    	status = node.split()

    	if status[1] == '*':
    		del status[1]
    		selfID = status[0]
    	# 0 for leader, 1 for manager, 2 for worker
    	identity = 2

    	if len(status) == 5:
    		identity = 0 if status[-1] == 'Leader' else 1
    	hostname = stauts[1]
    	datacenter_name = stauts[1].split('-')[0]
    	# if dead, continue, if is mangaer
    	if identity == 2 and stauts[2] == 'Down':
    		continue
    	if identity != 2 and stauts[-1] == 'Unreachable':
    		dead_managers.append(stauts[0])
    		continue
    	if datacenter_name not in data_centers:
    		data_centers[datacenter_name] = dict()
    	data_centers[datacenter_name][status[0]] = identity
    	if identity != 2:
    		live_managers += 1
    		live_managers_center[datacenter_name] = 0
    	if identity == 0:
    		leaderID = status[0]
    # if the number of managers < DESIRED_MANAGER or the leader is unreachable, return
    # if itself is not leader, return
    if leaderID != selfID :
    	return

    for dead_manager in dead_managers:
    	proc = subprocess.Popen(["sudo", "docker", "node", "demote", dead_manager], stdout=subprocess.PIPE)

    if live_managers == DESIRED_MANAGER:
    	return

    # find best candidate, and run promotion
    for (key, value) in data_centers:
    	if key in live_managers_center.keys():
    		continue
    	for (node, identity) in value:
    		if identity == 2:
    			proc = subprocess.Popen(["sudo", "docker", "node", "promote", node], stdout=subprocess.PIPE)
    			return

    for (key, value) in data_centers:
    	for (node, identity) in value:
    		if identity == 2:
    			proc = subprocess.Popen(["sudo", "docker", "node", "promote", node], stdout=subprocess.PIPE)
    			return
    
if __name__ == '__main__':
    main()