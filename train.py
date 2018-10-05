from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import rasa_core
from rasa_nlu.training_data import load_data
from rasa_nlu import config
from rasa_nlu.model import Trainer
from rasa_nlu.model import Metadata, Interpreter
from rasa_core.agent import Agent
from rasa_core.policies.fallback import FallbackPolicy
from rasa_core.policies.keras_policy import KerasPolicy
from rasa_core.policies.memoization import MemoizationPolicy
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core import run

import warnings
warnings.simplefilter('ignore')

logger = logging.getLogger(__name__)

def train_nlu(data, configs, model_dir):
    training_data = load_data(data)
    trainer = Trainer(config.load(configs))
    trainer.train(training_data)
    model_directory = trainer.persist(model_dir, fixed_model_name='nlu_mod')


def run_nlu(text):
    interpreter = Interpreter.load('models/nlu/default/nlu_mod')
    print(interpreter.parse(text))

def train_dialogue(domain_file='data/core/domain.yml',
                   model_path='models/current/dialogue',
                   training_data_file='data/core/stories.md'):
    fallback = FallbackPolicy(fallback_action_name="utter_default",
                              core_threshold=0.3,
                              nlu_threshold=0.3)

    agent = Agent(domain_file, policies=[KerasPolicy(), fallback])
    data = agent.load_data(training_data_file)
    agent.train(
        data,
        epochs=300,
        batch_size=50,
        validation_split=0.2)
    agent.persist(model_path)
    return agent

def run_bot():
    run.main('models/current/dialogue','models/nlu/default/nlu_mod')
    print('ran bot...')
    return None

'''

run nlu:
python3 -m rasa_nlu.run -m models/nlu/default/nlu_mod
 
run bot:
python3 -m rasa_core.run -d models/current/dialogue -u models/nlu/default/nlu_mod

'''

train_nlu('./data/nlu/training_dataset.json', './data/nlu/config.yml', './models/nlu')

#train_dialogue()

#run_bot()