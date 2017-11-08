### What did Evan do to setup the experimental environment

This project is based on AWS EC2 instances. I originally tried to run swarm on mininet hosts, but it turns out that all the mininet hosts share the same network name space. That's why I chose EC2 to isolate each machine with individual network name space.

### Setup EC2 instance

#### Add EC2 instance
- Go to [EC2 homepage](https://console.aws.amazon.com/ec2/). Open Instances tab on the left hand side
- Click "Launch Instance", and choose Linux 16.04 image. Then follow the default setup.
- When it prompts needs for keypair, choose demo keypair (I haven't done experiments without keypair).
- Then go to "Security Groups" on the left hand side, click the security group for the newly created instance, and choose "Inbound" tab on the bottom.
- Click "Edit", and add "Add Rule". Custom TCP / TCP / 2377 / Anywhere. Then click save. This step is critical because by default, Swarm uses 2377 port. Without this step, the nodes cannot reach out to each other.


#### Login to EC2 instance
- Check the aws.sh script in script folder. I already added ssh commands for different nodes. If you need to add instances, simply get another entry and replace the IPV4 address.
- Before you use the script, make sure you copy the demo.pem key file to the script folder.
- Then do "./aws.sh aws1". Add the footprint, and you are now in the machine.

#### Set up Docker on EC2 instance
- Git clone this repo.
- Run "docker_install.sh" script in script folder. This should install all the tools that are needed to use Docker.
- Type "docker version" to make sure you already installed docker correctly. 
- If you intend to run the EC2 instance as manager, run "docker swarm init". This will give you a token to join the swarm.
- If you intend to run the EC2 instance as worker, you need to setup a swarm with manager first. Then in the terminal of worker, run whatever command that is returned by swarm init. 


