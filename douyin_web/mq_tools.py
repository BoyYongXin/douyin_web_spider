import time
import logging
import pika
import _thread


class MqConfig(object):

    def __init__(self, ip, user, password, port='5672', virtual='/'):
        self.server = ip
        self.user = user
        self.password = password
        self.port = port
        self.virtual = virtual


class MqClient(object):

    def __init__(self, config: MqConfig):
        self.connection: pika.adapters.BlockingConnection = None
        self.channel: pika.adapters.blocking_connection.BlockingChannel = None

        self.bind_connection: pika.adapters.BlockingConnection = None

        self.config = config

        self.set_connection()

    def send_message(self, queue_name, content, tries=2):
        if not tries:
            logging.error(str(f'[mq]-[消息发送异常]-[{queue_name}]-[{content}]'))
            return
        tries -= 1

        try:
            if self.connection.is_closed:
                self.set_connection()
            elif self.channel.is_closed:
                logging.error('[mq-channel]-[异常断链]-[尝试恢复]')
                self.channel = self.connection.channel()

            self.channel.basic_publish(
                exchange='', routing_key=queue_name, body=content)
        except pika.exceptions.AMQPError as exceptions:
            logging.exception(exceptions)
            self.set_connection()
            self.send_message(queue_name, content, tries)

    def bind_queue(self, queue_name, callback, new_thread=True):
        # if not self.bind_connection or self.bind_connection.is_closed:
        #     print('=========================')
        #     self.bind_connection = self.get_connection()

        # channel = self.bind_connection.channel()
        channel = self.get_connection().channel()
        channel.basic_qos(prefetch_count=1)  # 只接受一条消息

        def on_message_callback(channel, method, properties, body):
            callback(body.decode('utf-8'))
            channel.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(on_message_callback=on_message_callback,
                              queue=queue_name, auto_ack=False)

        if new_thread:
            _thread.start_new_thread(channel.start_consuming, ())
        else:
            channel.start_consuming()

    def get_message(self, queue_name):
        channel = self.channel
        data = channel.basic_get(queue_name, auto_ack=False)
        if data[0]:
            channel.basic_ack(data[0].delivery_tag)
        if data[2]:

            return data[2].decode('utf-8')
        else:
            return []


    def set_connection(self):
        retry_time = 0
        while True:
            retry_time += 1
            try:
                logging.info('[mq]-[建立新链接]')
                self.close()

                self.connection = self.get_connection()
                self.channel = self.connection.channel()
                return
            except pika.exceptions.AMQPError as err:
                logging.error(str(f'[mq]-[建立链接异常，重试({retry_time})]'))
                logging.exception(err)
                time.sleep(retry_time * 10 * 60)

    def get_connection(self) -> pika.adapters.BlockingConnection:
        config = self.config
        return pika.BlockingConnection(pika.ConnectionParameters(
            config.server, config.port, config.virtual,
            pika.PlainCredentials(config.user, config.password), socket_timeout=600000, blocked_connection_timeout=600000, stack_timeout=600000))

    def close(self):
        try:
            if self.channel and self.channel.is_open:
                logging.info('[mq]-[关闭]-[channel]')
                self.channel.close()
            if self.connection and self.connection.is_open:
                logging.info('[mq]-[关闭]-[connection]')
                self.connection.close()
        except pika.exceptions.AMQPError as exceptions:
            logging.exception(exceptions)
    # def __repr__(self):
    #     try:
    #         if self.channel and self.channel.is_open:
    #             logging.info('[mq]-[关闭]-[channel]')
    #             self.channel.close()
    #         if self.connection and self.connection.is_open:
    #             logging.info('[mq]-[关闭]-[connection]')
    #             self.connection.close()
    #     except pika.exceptions.AMQPError as exceptions:
    #         logging.exception(exceptions)
