# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created By  : Guilherme Amorim
# Created Date: 2022
# version ='v1'
# ---------------------------------------------------------------------------

# Intents:
# - SparkleIntent
# - RedIntent
# - StopIntent
# - AMAZON.HelloWorldIntent
# - AMAZON.StopIntent
# - AMAZON.HelpIntent
# - AMAZON.CancelIntent
# - AMAZON.FallbackIntent
# - SetLedStateIntent

# Requests:
# - LaunchRequest
# - SessionEndedRequest

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
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

from ask_sdk_core.utils.request_util import get_slot_value

# ---------------------------------------------------------------------------
# IoT Thing information

THING_NAME = "B-L475E-IOT01A2"
AMAZON_ROOT_CA_CERTIFICATE  = "./certs/AmazonRootCA1.pem"
THING_PRIVATE_KEY_CERTIFICATE = "./certs/39e9497f17e0cba128e2af9ce6b48e0ab4127a294821b6152753c0a88b4ed9ca-private.pem.key"
THING_CERTIFICATE = "./certs/39e9497f17e0cba128e2af9ce6b48e0ab4127a294821b6152753c0a88b4ed9ca-certificate.pem.crt"
MQTT_ENDPOINT = "a2mxctj6in6ukh-ats.iot.us-east-1.amazonaws.com"

# ---------------------------------------------------------------------------
# Configuring MQTT

createMQTTClient = AWSIoTMQTTClient(THING_NAME)
createMQTTClient.configureEndpoint(MQTT_ENDPOINT, 443)
createMQTTClient.configureCredentials(AMAZON_ROOT_CA_CERTIFICATE, THING_PRIVATE_KEY_CERTIFICATE, THING_CERTIFICATE)
createMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
createMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
createMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
createMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
createMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
createMQTTClient.connect()

# ---------------------------------------------------------------------------
# Logging setup

SKILL_NAME = "My display controller"
LAUNCH_MESSAGE = "This skill was developed as a final course work at UFMG by Guilherme Amorim, under the guidance of Prof. Ricardo de Oliveira Duarte. You can say \"Hello\" or \"set led on/off\"."
HELP_MESSAGE = "Hi, You can say \"Hello\" or \"set led on/off\"."
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

# ---------------------------------------------------------------------------
# Formatting MQTT message

def format_mqtt_state_message(state_variable, value):
    payload = {"state":{"reported":{state_variable:value}}}
    print("Payload")
    print(json.dumps(payload))
    return json.dumps(payload)

def send_mqtt_state_message(topic, state_variable, value):
    payload = format_mqtt_state_message(state_variable, value)
    print("Sending payload to" + topic)
    createMQTTClient.publish(topic, payload, 1)

def format_mqtt_message(directive, data):
    payload = {}
    payload['directive'] = directive
    payload['data'] = data
    print("Payload")
    print(json.dumps(payload))
    return json.dumps(payload)

def send_mqtt_directive(topic, directive, data = {}):
    payload = format_mqtt_message(directive, data)
    createMQTTClient.publish(topic, payload, 1)

# ---------------------------------------------------------------------------
# SparkleIntent

@sb.request_handler(can_handle_func = is_intent_name("SparkleIntent"))
def spin_around_intent_handler(handler_input):
    speech = "Ok, sparkling"
    send_mqtt_directive("/myPi", "sparkle")
    handler_input.response_builder.speak(speech).set_card(SimpleCard(SKILL_NAME, speech)).set_should_end_session(False)
    return handler_input.response_builder.response

# ---------------------------------------------------------------------------
# RedIntent

@sb.request_handler(can_handle_func = is_intent_name("RedIntent"))
def spin_around_intent_handler(handler_input):
    speech = "Ok, turning red"
    send_mqtt_directive("/myPi", "red")
    handler_input.response_builder.speak(speech).set_card(SimpleCard(SKILL_NAME, speech)).set_should_end_session(False)
    return handler_input.response_builder.response

# ---------------------------------------------------------------------------
# StopIntent

@sb.request_handler(can_handle_func = is_intent_name("StopIntent"))
def stop_moving_intent_handler(handler_input):
    speech = "Ok, stopping"
    send_mqtt_directive("/myPi", "stop")
    handler_input.response_builder.speak(speech).set_card(SimpleCard(SKILL_NAME, speech)).set_should_end_session(False)
    return handler_input.response_builder.response

# ---------------------------------------------------------------------------
# LaunchRequest

@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    speech = LAUNCH_MESSAGE
    handler_input.response_builder.speak(speech).set_card(SimpleCard(SKILL_NAME, speech)).set_should_end_session(False)
    return handler_input.response_builder.response

# ---------------------------------------------------------------------------
# AMAZON.HelloWorldIntent

@sb.request_handler(can_handle_func = is_intent_name("HelloWorldIntent"))
def hello_world_intent_handler(handler_input):
    speech = "Hello. Look at the display!"
    send_mqtt_directive("/myPi", "hello")
    print("Send hello to MQTT")
    handler_input.response_builder.speak(speech).set_card(SimpleCard(SKILL_NAME, speech)).set_should_end_session(False)
    return handler_input.response_builder.response

# ---------------------------------------------------------------------------
# AMAZON.StopIntent

@sb.request_handler(can_handle_func = is_intent_name("AMAZON.StopIntent"))
def help_intent_hanlder(handler_input):
    speech = "Ok, stopping"
    send_mqtt_directive("/myPi", "stop")
    return handler_input.response_builder.speak(HELP_MESSAGE).ask(HELP_REPROMPT).set_card(SimpleCard(SKILL_NAME, HELP_MESSAGE)).response

# ---------------------------------------------------------------------------
# AMAZON.HelpIntent

@sb.request_handler(can_handle_func = is_intent_name("AMAZON.HelpIntent"))
def help_intent_hanlder(handler_input):
    return handler_input.response_builder.speak(HELP_MESSAGE).ask(HELP_REPROMPT).set_card(SimpleCard(SKILL_NAME, HELP_MESSAGE)).response

# ---------------------------------------------------------------------------
# AMAZON.CancelIntent

@sb.request_handler(can_handle_func = (is_intent_name("AMAZON.CancelIntent") or is_intent_name("AMAZON.StopIntent")))
def cancel_or_stop_intent_handler(handler_input):
    return handler_input.response_builder.speak(STOP_MESSAGE).response

# ---------------------------------------------------------------------------
# AMAZON.FallbackIntent

@sb.request_handler(can_handle_func = is_intent_name("AMAZON.FallbackIntent"))
def fallback_intent_handler(handler_input):
    return handler_input.response_builder.speak(FALLBACK_MESSAGE).ask(FALLBACK_REPROMPT).set_card(SimpleCard(SKILL_NAME, FALLBACK_MESSAGE)).response

# ---------------------------------------------------------------------------
# SessionEndedRequest

@sb.request_handler(can_handle_func = is_request_type("SessionEndedRequest"))
def session_ended_request(handler_input):
    logger.info("In SessionEndedRequestHandler")
    logger.info("Session ended reason: {}".format(handler_input.request_envelope.request.reason))
    return handler_input.response_builder.response

# ---------------------------------------------------------------------------
# SetLedStateIntent

@sb.request_handler(can_handle_func = is_intent_name("SetLedStateIntent"))
def set_led_on_intent_handler(handler_input):
    value = get_slot_value(handler_input, "ON_OFF_SLOT")
    speech = "Set LED state = " + value
    print("Send 'LED_value: " + value + "' to MQTT")
    send_mqtt_state_message("$aws/things/B-L475E-IOT01A2/shadow/update", "LED_value", value)
    send_mqtt_state_message("$aws/things/B-L475E-IOT01A2/testing", "LED_value", value)
    handler_input.response_builder.speak(speech).set_card(SimpleCard(SKILL_NAME, speech)).set_should_end_session(False)
    return handler_input.response_builder.response

# ---------------------------------------------------------------------------

@sb.exception_handler(can_handle_func = lambda i, e: 'AskSdk' in e.__class__.__name__)
def ask_exception_intent_handler(handler_input, exception):
    return handler_input.response_builder.speak(EXCEPTION_MESSAGE).ask(HELP_REPROMPT).response

@sb.global_request_interceptor()
def request_logger(handler_input):
    print("Request received: {}".format(handler_input.request_envelope.request))

# Handler name that is used on AWS lambda
lambda_handler = sb.lambda_handler()
