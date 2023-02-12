import logging
import requests
from flask import Flask
from flask_ask import Ask, statement, context, question

app = Flask(__name__)
ask = Ask(app, '/')
log = logging.getLogger('flask_ask').setLevel(logging.DEBUG)


@ask.launch
def launchGame():
    return question("Welcome to our Trivial Pursuit Game. Would you like to start a game?")

