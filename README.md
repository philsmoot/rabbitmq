dojob.py is a job scheduler that can run in multiple environments

on macbook
1) edit job_steps.json
2) start the RabbitMQ server
   a) on macbook - start_server.sh
   b) on bruno - start_bruno_rabbit.sh
3) start the dojob.py
   a) on macbook - python3 dojob.py
   b) on bruno
     i) module load anaconda
     ii) python3 -m pip install pika --upgrade
     iii) python3 dojob.py

   
