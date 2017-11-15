import time
import subprocess
import json
import os

SLEEP_SECS = 5
DESIRED_MANAGER = 3
data_centers = dict()
CONFIG_PATH = 'config.json'
POLICY = 0 # 0 is Fault-tolerant(By default) 1 is Performance

LEADER = 0
MANAGER = 1
WORKER = 2

def main():
    init()
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

def getNodeInfo():
    proc = subprocess.Popen(["sudo", "docker", "node", "ls"], stdout=subprocess.PIPE)
    nodes_info = proc.stdout.read().split('\n')    
    return nodes_info[1:]

def parseNodeInfo(node_info):
    if len(node_info) == 0:
        return None

    status = node_info.split()
    info = dict()
    if status[1] == '*':
        del status[1]
        info['self_id'] = status[0]
    else:
        info['self_id'] = None

    info['nodeID'] = status[0]
    info['identity'] = WORKER
    if len(status) == 5:
            info['identity'] = LEADER if status[-1] == 'Leader' else MANAGER
    info['hostname'] = status[1]
    info['datacenter'] = status[1].split('-')[0]
    info['alive'] = True
    if info['identity'] == WORKER and status[2] == 'Down':
        info['alive'] = False
    if info['identity'] != WORKER and status[-1] == 'Unreachable':
        info['alive'] = False

    return info

def isWorker(info):
    return info['identity'] == WORKER

def isManager(info):
    return info['identity'] == MANAGER

def isLeader(info):
    return info['identity'] == LEADER

def isDead(info):
    return info['alive']

def isSelf(info):
    return True if info['self_id'] is not None else False

def isDeadWorker(info):
    return isDead(info) and isWorker(info)

def isDeadManagerOrLeader(info):
    return isDead(info) and (isManager(info) or isLeader(info))

def getNodeID(info):
    return info['nodeID']

def getIdentity(info):
    return info['identity']

def getDataCenter(info):
    return info['datacenter']

def demoteDeadManagers(dead_managers):
    for dead_manager in dead_managers:
    	proc = subprocess.Popen(["sudo", "docker", "node", "demote", dead_manager], stdout=subprocess.PIPE)

def swarmGuardian():
    global data_centers
    print nodes_status

    # split to different nodes
    nodes_info = getNodeInfo()

    # update datacenter dict
    dead_managers = []
    live_managers = 0
    live_managers_center = set()
    leaderID = ""
    selfID = ""
    for node in nodes_status:
        parsedInfo = parseNodeInfo(node)

        if isSelf(parsedInfo):
            selfID = getNodeID(parsedInfo)

        if isDeadWorker(parsedInfo):
            continue
        if isDeadManagerOrLeader(parsedInfo):
            dead_managers.append(getNodeID(parsedInfo))
            continue

    	if datacenter_name not in data_centers:
            data_centers[datacenter_name] = dict()
    	data_centers[datacenter_name][getNodeID(parsedInfo)] = getIdentity(parsedInfo)
    	if not isWorker(parsedInfo):
            live_managers += 1
            live_managers_center.add(getDataCenter(parsedInfo))
    	if isLeader(parsedInfo):
            leaderID = getNodeID(parsedInfo)
    # if the number of managers < DESIRED_MANAGER or the leader is unreachable, return
    # if itself is not leader, return
    if leaderID != selfID :
    	return

    demoteDeadManagers(dead_managers)

    if live_managers >= DESIRED_MANAGER:
    	return

    # find best candidate, and run promotion
    for key, value in data_centers.iteritems():
    	if key in live_managers_center.keys():
            continue
    	for node, identity in value.iteritems():
            if identity == 2:
                proc = subprocess.Popen(["sudo", "docker", "node", "promote", node], stdout=subprocess.PIPE)
                return

    for key, value in data_centers.iteritems():
    	for node, identity in value.iteritems():
            if identity == 2:
                proc = subprocess.Popen(["sudo", "docker", "node", "promote", node], stdout=subprocess.PIPE)
                return
    
if __name__ == '__main__':
    main()
