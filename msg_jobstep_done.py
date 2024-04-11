import pika 
import sys

#! add return checks on procedure calls.
#! establish a connection to the RabbitMQ server
#! mq_server = 'localhost'
mq_server = 'localhost'
connection = pika.BlockingConnection(pika.ConnectionParameters(mq_server))
channel = connection.channel()

#! create the "task" queue to which messages will be delivered and consumeed
channel.queue_declare(queue='task_queue', durable=True)

#! TODO - validate argv input
task = ' '.join(sys.argv[1:])
message = task + '_done' 
#! publish test message
channel.basic_publish(exchange='',
                      routing_key='task_queue',
                      body=message,
                      properties=pika.BasicProperties(
                        delivery_mode=pika.DeliveryMode.Persistent))

print("[msg_jobstep_done] Enqueue message = " + message)

#! TODO check return to make sure call successed

#! make sure network buffers are flushed and message was delivered
connection.close()




