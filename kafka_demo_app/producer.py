#!/usr/bin/env python

from functools import partial
import json


from configparser import ConfigParser
from confluent_kafka import Producer

config_parser = ConfigParser()
config_parser.read("/Users/andriigerasymchuk/private-repositories/3PI-03/kafka_demo_app/kafka_demo_app/getting_started.ini")
topic = config_parser.get("metadata", "topic")
config = dict(config_parser['default'])

producer = Producer(config)


def delivery_callback(err, msg):
        if err:
            print('ERROR: Message failed delivery: {}'.format(err))
        else:
            print("Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
                topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))


async def produce_kafka_event(event: dict, topic: str):
    producer.produce(topic, json.dumps(event).encode('utf-8'))

produce_animal_vote = partial(produce_kafka_event, topic=topic)
   

# if __name__ == '__main__':
#     # Parse the command line.
#     parser = ArgumentParser()
#     parser.add_argument('config_file', type=FileType('r'))
#     args = parser.parse_args()

#     # Parse the configuration.
#     # See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
#     config_parser = ConfigParser()
#     config_parser.read_file(args.config_file)
#     config = dict(config_parser['default'])

#     # Create Producer instance
#     producer = Producer(config)

#     # Optional per-message delivery callback (triggered by poll() or flush())
#     # when a message has been successfully delivered or permanently
#     # failed delivery (after retries).
#     def delivery_callback(err, msg):
#         if err:
#             print('ERROR: Message failed delivery: {}'.format(err))
#         else:
#             print("Produced event to topic {topic}: key = {key:12} value = {value:12}".format(
#                 topic=msg.topic(), key=msg.key().decode('utf-8'), value=msg.value().decode('utf-8')))

#     # Produce data by selecting random values from these lists.
#     topic = "vottings"
#     user_ids = ['eabara', 'jsmith', 'sgarcia', 'jbernard', 'htanaka', 'awalther']
#     pets = ['cat', 'dog']

#     count = 0
#     for _ in range(10):

#         user_id = choice(user_ids)
#         product = choice(pets)
#         producer.produce(topic, product, user_id, callback=delivery_callback)
#         count += 1

#     # Block until the messages are sent.
#     producer.poll(10000)
#     producer.flush()