# Consumer example
import pika, sys, os
from pika.spec import Queue

queue = 'Tx.tec.performance.computer-elements.CPU'

def main():
    credentials = pika.PlainCredentials('guest', 'guest')
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, '/',credentials))
    channel = connection.channel()

    #Channel will consume data from the queue: Tx.tec.performance.protocols.NETWORK
    channel.queue_declare(queue=queue)
    

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)

    channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

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