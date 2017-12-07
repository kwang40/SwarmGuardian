import time
import json
from SwarmGuard import SwarmGuardian 

SLEEP_SECS = 5
DESIRED_MANAGER = 3
CONFIG_PATH = 'config.json'
POLICY = 0 # 0 is Fault-tolerant(By default) 1 is Performance
EMAIL = "user@example.com"

def main():
    init()
    run()

def init():
    with open(CONFIG_PATH, 'r') as f:
        data = json.load(f)

    global SLEEP_SECS
    global DESIRED_MANAGER
    global POLICY
    global EMAIL

    SLEEP_SECS = data['SLEEP_SECS']
    DESIRED_MANAGER = data['DESIRED_MANAGER']
    POLICY = data['POLICY']
    EMAIL = data['EMAIL']

def run():
    s = SwarmGuardian(DESIRED_MANAGER, POLICY, EMAIL)
    while True:
        s.run()
        time.sleep(SLEEP_SECS)

if __name__ == '__main__':
    main()
