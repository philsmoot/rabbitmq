import pika
import sys
import os
import json
import subprocess

def launch_shell_job(filepath, command):
    shell_command = filepath + '/' + command
    print("[launch_shell_job() command = " + shell_command)
    try:
        process = subprocess.Popen(shell_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("launch_shell_job failed")
        stdout, stderr = process.communicate()
        print("[launch_shell_job] Standard Output:" + stdout.decode())
        print("[launch_shell_job] Standard Error:" + stderr.decode())
   
def queue_msg(mq_server, message):    
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(mq_server))
        channel = connection.channel()

        #! create or ensure the "task" queue exists
        channel.queue_declare(queue='task_queue', durable=True)

        #! publish message
        channel.basic_publish(exchange='',
                        routing_key='task_queue',
                        body=message,
                        properties=pika.BasicProperties(
                        delivery_mode=pika.DeliveryMode.Persistent))

        #! make sure network buffers are flushed and message was delivered
        connection.close()
        print("[queue_msg()] Enqueue message = " + message)

    except pika.exceptions.AMQPError as e:
        print(f"Failed to deliver message: {e}")

def read_server_config(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Unable to parse JSON from file '{file_path}'.")
        return None

def parse_json(json_data):
    if json_data:
        # Extract server IP address
        server_ip = json_data.get("server_ip")
        
        # Extract environment
        environment = json_data.get("environment")

        # Extract pathname
        filepath = json_data.get("filepath")
        
        # Extract job steps
        job_steps = json_data.get("job_steps")
        
        # Extract number of job steps
        num_job_steps = json_data.get("num_job_steps")
        
        return server_ip, environment, filepath, job_steps, num_job_steps
    else:
        return None, None, None, None, None
    
def act_on_message(mq_server, message, job_steps, num_job_steps, filepath):
    #!
    #! messages can look like:
    #! task_queued
    #! task_started
    #! task_done
    #!
    #! launch a the job step if the task is "queued"
    #! if a task is "done" and there is another task to be completed, queue the next task
    #! else no operation for the message 

    index =  0
    for entry in job_steps:
        index +=1
        if message == entry + "_queued":
            launch_shell_job(filepath, entry)
        if message == entry + "_done":
            if index < num_job_steps:
               queue_msg(mq_server, job_steps[index] + "_queued") 
     
 
def main():

    if len(sys.argv) != 2:
        print("Usage: python3 dojob.py <path_to_json_file>")
        print("Default config file is ./job_steps.json")
        config_file = "./job_steps.json"
    else:
        config_file = sys.argv[1]
    
    # Read JSON file
    server_config = read_server_config(config_file)
    
    # Parse JSON data
    mq_server, environment, filepath, job_steps, num_job_steps = parse_json(server_config)
    
    if mq_server is not None:
        print("dojob.py configuration")
        print(f"Server IP Address: {mq_server}")
        print(f"Environment: {environment}")
        print(f"Filepath: {filepath}")
        print("Job Steps:")
        for step in job_steps:
            print(step)
        print(f"Number of Job Steps: {num_job_steps}")
    else:
        print("No server configuration extracted.")

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(mq_server))
        channel = connection.channel()
        #! make sure the 'task_queue' exists
        channel.queue_declare(queue='task_queue', durable=True)
    except pika.exceptions.AMQPError as e:
        print(f"main() failed to connect to mq_server: {e}")

    #! the callback function is called when a message is queued
    def callback(ch, method, properties, body):
        print(f"[callback] Dequeue message = {body.decode()}")
        message = str(f"{body.decode()}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        act_on_message(mq_server, message, job_steps, num_job_steps, filepath)   
        return
    
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue', on_message_callback=callback)

    print('[*] Waiting for messages. To exit press CTRL+C')

    #! initialize queue with the first task
    first_step = job_steps[0]
    queue_msg(mq_server, first_step + "_queued")

    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

