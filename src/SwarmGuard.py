import subprocess

LEADER = 0
MANAGER = 1
WORKER = 2

class SwarmGuardian:

    def __init__(self, _desired_manager = 3):
        self.dead_managers = list()
        self.live_managers_center = set()
        self.data_centers = dict()
        self.live_managers = 0
        self.leaderID = None
        self.selfID = None
        self.desired_manager = _desired_manager
        self.self_identity= None

    ###

    def run(self):
        self.reset()
        self.update_datacenter_info()

        if self.iAmLeader():
            return
        else:
            self.leaderWork()

    ###

    def reset(self):
        self.dead_managers.clear()
        self.live_managers_center.clear()
        self.live_managers = 0
        self.leaderID = None
        self.selfID = None
        self.self_identity= None

    ###

    def update_datacenter_info(self):
        nodes_info = self.getNodeInfo()

        for node in nodes_status:
            self.update_node_info(node)

    ###

    def update_node_info(self, node):
        parsedInfo = parseNodeInfo(node)

        if self.isSelf(parsedInfo):
            self.selfID = getNodeID(parsedInfo)
            self.self_identity = getIdentity(parsedInfo)

        if self.isDeadWorker(parsedInfo):
            continue
        if self.isDeadManagerOrLeader(parsedInfo):
            self.dead_managers.append(getNodeID(parsedInfo))
            continue

        if self.getDataCenter(parsedInfo) not in self.data_centers:
            self.data_centers[self.getDataCenter(parsedInfo)] = dict()
        self.data_centers[self.getDataCenter(parsedInfo)][self.getNodeID(parsedInfo)] = self.getIdentity(parsedInfo)
        if not self.isWorker(parsedInfo):
            self.live_managers += 1
            self.live_managers_center.add(self.getDataCenter(parsedInfo))
        if self.isLeader(parsedInfo):
            self.leaderID = self.getNodeID(parsedInfo)

    ###

    def getNodeInfo(self):
        proc = subprocess.Popen(["sudo", "docker", "node", "ls"], stdout=subprocess.PIPE)
        nodes_info = proc.stdout.read().split('\n')    
        return nodes_info[1:]

    ###

    def parseNodeInfo(self, node_info):
        if len(node_info) == 0:
            return None

        status = node_info.split()
        print status
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

    ###

    def stable(self):
        return self.live_managers >= self.desired_manager

    ###

    def iAmLeader(self):
        return self.leaderID == self.selfID

    ###

    def leaderWork(self):
        self.demoteDeadManagers()
        if self.stable():
            return
        self.defaultPromotePolicy()

    ###

    def defaultPromotePolicy():
        for key, value in self.data_centers.iteritems():
            if key in self.live_managers_center.keys():
                continue
            for node, identity in value.iteritems():
                if self.isWorker(self.self_identity):
                    self.promoteNode(node)
                    return

        for key, value in self.data_centers.iteritems():
            for node, identity in value.iteritems():
                if self.isWorker(self.self_identity):
                    self.promoteNode(node)
                    return

    ###

    def demoteDeadManagers(self):
        for dead_manager in self.dead_managers:
            proc = subprocess.Popen(["sudo", "docker", "node", "demote", dead_manager], stdout=subprocess.PIPE)

    ###

    def promoteNode(self, node):
        proc = subprocess.Popen(["sudo", "docker", "node", "promote", node], stdout=subprocess.PIPE)

    ###

    def isWorker(self, identity):
        return identity == WORKER

    ###

    def isManager(self, identity):
        return identity == MANAGER

    ###

    def isLeader(self, identity):
        return identity == LEADER

    ###

    def isDead(self, info):
        return info['alive']

    ###

    def isSelf(self, info):
        return True if info['self_id'] is not None else False

    ###

    def isDeadWorker(self, info):
        return isDead(info) and isWorker(getIdentity(info))

    ###

    def isDeadManagerOrLeader(self, info):
        return isDead(info) and (isManager(getIdentity(info)) or isLeader(getIdentity(info)))

    ###

    def getNodeID(self, info):
        return info['nodeID']

    ###

    def getIdentity(self, info):
        return info['identity']

    ###

    def getDataCenter(self, info):
        return info['datacenter']

