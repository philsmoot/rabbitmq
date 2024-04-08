import pika
import sys
import os
import time
import json
import subprocess

def launch_shell_job(command):
    # Launch the command in a shell
    shell_command = "./" + command
    process = subprocess.Popen(shell_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for the command to complete and capture output
    stdout, stderr = process.communicate()
    
    print("launch_shell_job" + shell_command)
    # Print the output
    print("Standard Output:")
    print(stdout.decode())
    print("Standard Error:")
    print(stderr.decode())

def queue_msg(mq_server, message):
    
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

    print(" [x] Enqueue message = " + message)

    #! TODO check return to make sure call successed

    #! make sure network buffers are flushed and message was delivered
    connection.close()

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
        
        # Extract job steps
        job_steps = json_data.get("job_steps")
        
        # Extract number of job steps
        num_job_steps = json_data.get("num_job_steps")
        
        return server_ip, environment, job_steps, num_job_steps
    else:
        return None, None, None, None
    
def act_on_message(message, current_step, next_step):
    #! messages can look like:
    #! msg_taskname_queued
    #! msg_taskname_started
    #! msg_taskname_done

    if message == "msg_" + current_step + "_queued":
        launch_shell_job(current_step)
        return 1
    elif message == "msg_" + current_step + "_done":
        queue_msg("msg_" + next_step + "_queued")
        return 0
    else:
        print ("message not handled" + message)
        return 0

def main():

    if len(sys.argv) != 2:
        print("Usage: python3 dojob.py <path_to_json_file>")
        #! hack for now, we should exit...
        file_path = "./job_steps.json"
    else:
        file_path = sys.argv[1]
    
    # Read JSON file
    server_config = read_server_config(file_path)
    
    # Parse JSON data
    server_ip, environment, job_steps, num_job_steps = parse_json(server_config)
    current_job_index = 0
    
    if server_ip is not None:
        print(f"Server IP Address: {server_ip}")
        print(f"Environment: {environment}")
        print("Job Steps:")
        for step in job_steps:
            print(step)
        print(f"Number of Job Steps: {num_job_steps}")
    else:
        print("No server configuration extracted.")

    connection = pika.BlockingConnection(pika.ConnectionParameters(server_ip))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)

    def callback(ch, method, properties, body):
        print(f" [x] Dequeue message = {body.decode()}")
        message = str(f"{body.decode()}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
        if current_job_index < num_job_steps:
            current_step = job_steps[current_job_index]
            if current_job_index < num_job_steps - 1:
                next_step = job_steps[current_job_index + 1]
            else:
                next_step = ""
        if (act_on_message(message, current_step, next_step) == 1):
            current_job_index = current_job_index + 1
        return
    
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue', on_message_callback=callback)

    current_step = job_steps[current_job_index]
    queue_msg(server_ip, "msg_" + current_step + "_queued")

    print(' [*] Waiting for messages. To exit press CTRL+C')
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

