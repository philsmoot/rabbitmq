dojob.py is a job scheduler that can run in multiple environments
a job has a set of steps which is define in job_steps.json
rabbitmq is used as the message queue for enqueuing and dequeuing step tasks.

to use:

0) get the server ip address that the rabbitmq instance will be running on.
   a) on macbook - ifconfig - look for the ip6 address
   b) on bruno - ifconfig - look for ip6 address under vlan300 entry
1) edit job_steps.json
2) start the RabbitMQ server
   a) on macbook - start_server.sh
   b) on bruno - start_bruno_rabbit.sh
3) start the dojob.py
   a) on macbook - python3 dojob.py
   b) on bruno
     i) module load anaconda
     ii) python3 -m pip install pika --upgrade (look to add this to global env)
     iii) python3 dojob.py

   
