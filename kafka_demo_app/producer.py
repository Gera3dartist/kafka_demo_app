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
