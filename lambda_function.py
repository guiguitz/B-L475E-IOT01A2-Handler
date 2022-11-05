# -*- coding: utf-8 -*-

import random
import logging
import os
import time
import json

from ask_sdk_core.utils import is_intent_name, is_request_type, viewport
from ask_sdk_model.ui import SimpleCard
from ask_sdk_core.skill_builder import SkillBuilder

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective, ExecuteCommandsDirective, SpeakItemCommand,
    AutoPageCommand, HighlightMode)

createMQTTClient = AWSIoTMQTTClient("B-L475E-IOT01A2")

"""
Change this endpoint to suit yours
"""
createMQTTClient.configureEndpoint('a2mxctj6in6ukh-ats.iot.us-east-1.amazonaws.com', 443)
#createMQTTClient.configureEndpoint(os.environ['AWS_IOT_ENDPOINT'], 443)

"""
# Check these certificate names if necessary
"""
createMQTTClient.configureCredentials("./certs/AmazonRootCA1.pem", "./certs/39e9497f17e0cba128e2af9ce6b48e0ab4127a294821b6152753c0a88b4ed9ca-private.pem.key", "./certs/39e9497f17e0cba128e2af9ce6b48e0ab4127a294821b6152753c0a88b4ed9ca-certificate.pem.crt")

createMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
createMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
createMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
createMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
createMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

createMQTTClient.connect()

SKILL_NAME = "My display controller"
HELP_MESSAGE = "You can say hello, turn the display red, or sparkle."
HELP_REPROMPT = "What do you want to do? Try saying hello?"
STOP_MESSAGE = "Goodbye!"
FALLBACK_MESSAGE = "Oops! I didn't understand. Say hello."
FALLBACK_REPROMPT = 'How can I help you?'
EXCEPTION_MESSAGE = "Sorry. I can't do that"

sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def _load_apl_document(file_path):
    """Load the apl json document at the path into a dict object."""
    with open(file_path) as f:
        return json.load(f)

def format_mqtt_message(directive, data):
    payload = {}
    payload['directive'] = directive
    payload['data'] = data

    print("Payload")
    print(json.dumps(payload))

    return json.dumps(payload)

"""
Note the use of dictionary type for data, so we can pass anything. e.g:
send_mqtt_directive("/myPi", "take a picture", data={"session_id":session_id})
"""
def send_mqtt_directive(topic, directive, data = {}):
    payload = format_mqtt_message(directive, data)
    createMQTTClient.publish(topic, payload, 1)

@sb.request_handler(can_handle_func = is_intent_name("SparkleIntent"))
def spin_around_intent_handler(handler_input):
    speech = "Ok, sparkling"
    send_mqtt_directive("/myPi", "sparkle")
# send_mqtt_directive("/myPi", "spin", data= {"data", 10))
# replace 10 with passed sparkle time

    handler_input.response_builder.speak(speech).set_card(SimpleCard(SKILL_NAME, speech)).set_should_end_session(False)
    return handler_input.response_builder.response

@sb.request_handler(can_handle_func = is_intent_name("RedIntent"))
def spin_around_intent_handler(handler_input):
    speech = "Ok, turning red"
    send_mqtt_directive("/myPi", "red")

    handler_input.response_builder.speak(speech).set_card(SimpleCard(SKILL_NAME, speech)).set_should_end_session(False)
    return handler_input.response_builder.response

@sb.request_handler(can_handle_func = is_intent_name("StopIntent"))
def stop_moving_intent_handler(handler_input):
    speech = "Ok, stopping"
    send_mqtt_directive("/myPi", "stop")

    handler_input.response_builder.speak(speech).set_card(SimpleCard(SKILL_NAME, speech)).set_should_end_session(False)
    return handler_input.response_builder.response

@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    speech = "Hi! You can control the display, say hello, or give me a command like sparkle or turn red"

    handler_input.response_builder.speak(speech).set_card(SimpleCard(SKILL_NAME, speech)).set_should_end_session(False)
    return handler_input.response_builder.response

@sb.request_handler(can_handle_func = is_intent_name("HelloWorldIntent"))
def hello_world_intent_handler(handler_input):

    speech = "Hello. Look at the display!"
    send_mqtt_directive("/myPi", "hello")
    print("Send hello to MQTT")

    handler_input.response_builder.speak(speech).set_card(SimpleCard(SKILL_NAME, speech)).set_should_end_session(False)
    return handler_input.response_builder.response

@sb.request_handler(can_handle_func = is_intent_name("AMAZON.StopIntent"))
def help_intent_hanlder(handler_input):
    speech = "Ok, stopping"
    send_mqtt_directive("/myPi", "stop")
    return handler_input.response_builder.speak(HELP_MESSAGE).ask(HELP_REPROMPT).set_card(SimpleCard(SKILL_NAME, HELP_MESSAGE)).response

@sb.request_handler(can_handle_func = is_intent_name("AMAZON.HelpIntent"))
def help_intent_hanlder(handler_input):
    return handler_input.response_builder.speak(HELP_MESSAGE).ask(HELP_REPROMPT).set_card(SimpleCard(SKILL_NAME, HELP_MESSAGE)).response

@sb.request_handler(can_handle_func = (is_intent_name("AMAZON.CancelIntent") or is_intent_name("AMAZON.StopIntent")))
def cancel_or_stop_intent_handler(handler_input):
    return handler_input.response_builder.speak(STOP_MESSAGE).response

@sb.request_handler(can_handle_func = is_intent_name("AMAZON.FallbackIntent"))
def fallback_intent_handler(handler_input):
    return handler_input.response_builder.speak(FALLBACK_MESSAGE).ask(FALLBACK_REPROMPT).set_card(SimpleCard(SKILL_NAME, FALLBACK_MESSAGE)).response

@sb.request_handler(can_handle_func = is_request_type("SessionEndedRequest"))
def session_ended_request(handler_input):
    logger.info("In SessionEndedRequestHandler")
    logger.info("Session ended reason: {}".format(handler_input.request_envelope.request.reason))
    return handler_input.response_builder.response

@sb.exception_handler(can_handle_func = lambda i, e: 'AskSdk' in e.__class__.__name__)
def ask_exception_intent_handler(handler_input, exception):
    return handler_input.response_builder.speak(EXCEPTION_MESSAGE).ask(HELP_REPROMPT).response

@sb.global_request_interceptor()
def request_logger(handler_input):
    print("Request received: {}".format(handler_input.request_envelope.request))

# Handler name that is used on AWS lambda
lambda_handler = sb.lambda_handler()
