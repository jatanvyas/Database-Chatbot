from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from rasa_core.channels import HttpInputChannel
from rasa_core import utils
from rasa_core.agent import Agent
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.channels.channel import UserMessage
from rasa_core.channels.direct import CollectingOutputChannel
from rasa_core.channels.rest import HttpInputComponent
from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)

class SimpleWebBot(HttpInputComponent):
    """A simple web bot that listens on a url and responds."""

    def blueprint(self, on_new_message):
        custom_webhook = Blueprint('custom_webhook', __name__)

        @custom_webhook.route("/status", methods=['GET'])
        def health():
            return jsonify({"status": "ok"})

        @custom_webhook.route("/", methods=['POST'])
        def receive():
            opjson = {}
            payload = request.json
            sender_id = 'jv'                                       # static for testing, otherwise payload.get()
            text = payload.get("message", None)
            out = CollectingOutputChannel()
            on_new_message(UserMessage(text, out, sender_id))
            opjson["text"] = out.messages[0]["text"]
            try:
                opjson["option"] = out.messages[1]["text"]          #Pass other data as response.
            except:
                pass
            return jsonify(opjson)
    
        return custom_webhook

def run(serve_forever=True):
    interpreter = RasaNLUInterpreter("models/nlu/default/nlu_mod")
    agent = Agent.load('models/current/dialogue', interpreter=interpreter)

    input_channel = SimpleWebBot()
    if serve_forever:
        agent.handle_channel(HttpInputChannel(5004, "/chat", input_channel))
    return agent

if __name__ == '__main__':
    utils.configure_colored_logging(loglevel="INFO")
    run()

#curl -XPOST -H "Content-Type: application/json" http://localhost:5004/chat/ -d '{"message":"Hello"}'

#file:///home/jatan/test/index.html

#file:///home/jatan/PycharmProjects/MBbot/venv/index.html