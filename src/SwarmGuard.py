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
	print 'run'
        self.reset()
        self.update_datacenter_info()

        if self.iAmLeader():
            self.leaderWork()
        else:
            return

    ###

    def reset(self):
        del self.dead_managers[:]
        self.live_managers_center.clear()
        self.live_managers = 0
        self.leaderID = None
        self.selfID = None
        self.self_identity= None

    ###

    def update_datacenter_info(self):
        nodes_info = self.getNodeInfo()

        for node in nodes_info:
            self.update_node_info(node)

    ###

    def update_node_info(self, node):
        parsedInfo = self.parseNodeInfo(node)

	if parsedInfo is None:
	    return

        if self.isSelf(parsedInfo):
            self.selfID = self.getNodeID(parsedInfo)
            self.self_identity = self.getIdentity(parsedInfo)

        if self.isDeadWorker(parsedInfo):
            return 
        if self.isDeadManagerOrLeader(parsedInfo):
            self.dead_managers.append(self.getNodeID(parsedInfo))
            return 

        if self.getDataCenter(parsedInfo) not in self.data_centers:
            self.data_centers[self.getDataCenter(parsedInfo)] = dict()
        self.data_centers[self.getDataCenter(parsedInfo)][self.getNodeID(parsedInfo)] = self.getIdentity(parsedInfo)
        if not self.isWorker(self.getIdentity(parsedInfo)):
            self.live_managers += 1
            self.live_managers_center.add(self.getDataCenter(parsedInfo))
        if self.isLeader(self.getIdentity(parsedInfo)):
            self.leaderID = self.getNodeID(parsedInfo)

    ###

    def getNodeInfo(self):
        proc = subprocess.Popen(["sudo", "docker", "node", "ls"], stdout=subprocess.PIPE)
        nodes_info = proc.stdout.read().split('\n')    
        return nodes_info[1:-1]

    ###

    def parseNodeInfo(self, node_info):
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

    ###

    def stable(self):
	print 'live managers: '
	print self.live_managers
	print 'desired managers: '
	print self.desired_manager
        return self.live_managers >= self.desired_manager

    ###

    def iAmLeader(self):
        return self.leaderID == self.selfID

    ###

    def leaderWork(self):
	print 'process leader work'
        self.demoteDeadManagers()
        if self.stable():
	    print 'it is stable'
            return
        self.defaultPromotePolicy()

    ###

    def defaultPromotePolicy(self):
	print 'default promote policy'
        for key, value in self.data_centers.iteritems():
            if key in self.live_managers_center:
                continue
            for node, identity in value.iteritems():
                if self.isWorker(identity):
                    self.promoteNode(node)
                    return

        for key, value in self.data_centers.iteritems():
            for node, identity in value.iteritems():
                if self.isWorker(identity):
                    self.promoteNode(node)
                    return

    ###

    def demoteDeadManagers(self):
        for dead_manager in self.dead_managers:
	    print 'demoting ' + dead_manager 
	    self.demoteNode(dead_manager)

    ###

    def demoteNode(self, node):
        proc = subprocess.Popen(["sudo", "docker", "node", "demote", node], stdout=subprocess.PIPE)
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
        return not info['alive']

    ###

    def isSelf(self, info):
        return True if info['self_id'] is not None else False

    ###

    def isDeadWorker(self, info):
        return self.isDead(info) and self.isWorker(self.getIdentity(info))

    ###

    def isDeadManagerOrLeader(self, info):
        return self.isDead(info) and (self.isManager(self.getIdentity(info)) or self.isLeader(self.getIdentity(info)))

    ###

    def getNodeID(self, info):
        return info['nodeID']

    ###

    def getIdentity(self, info):
        return info['identity']

    ###

    def getDataCenter(self, info):
        return info['datacenter']

