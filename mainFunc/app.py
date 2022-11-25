from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_webservice_support.webservice_handler import WebserviceSkillHandler
import azure.functions as func
import json
import os

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["state"] = "introduced"
        
        speech_text = "Welcome to our Trivial Pursuit Game. Would you like to start a game?"
        reprompt = "If you need help, just say so"

        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response


class YesIntentHandler(AbstractRequestHandler):
    """Handler for Yes Intent"""
    
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AMAZON.YesIntent")(handler_input)
    
    def handle(self, handler_input: HandlerInput) -> Response:
        session_attr = handler_input.attributes_manager.session_attributes
        if ("state" in session_attr) and (session_attr["state"] == "introduced"):
            session_attr["state"] = "waitingForPlayerCount"
            session_attr["playerCount"] = 0
            
            speech_text = "Thats cool! How many players are you?"
            reprompt = "How many players are you?"
            
            handler_input.response_builder.speak(speech_text).ask(reprompt)
            return handler_input.response_builder.response
        else:
            pass

class NumberOfPlayersIntentHandler(AbstractRequestHandler):
    """Handler for player count"""
    
    def can_handle(self, handler_input: HandlerInput) -> bool:
        session_attr = handler_input.attributes_manager.session_attributes
        
        return ("state" in session_attr) and (session_attr["state"] == "waitingForPlayerCount") and is_intent_name("NumberOfPlayersIntent")(handler_input)
    
    def handle(self, handler_input: HandlerInput) -> Response:
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["state"] = "waitingForPlayerNames"
        playerCount = int(handler_input.request_envelope.request.intent.slots["count"].value)
        session_attr["playerCount"] = playerCount
        
        if playerCount > 1:
            speech_text = "Okay. Player one, what is your name?"
        else:
            speech_text = "Okay. What is your name?"
        reprompt = "What is your name?"
        
        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response

class AddPlayerIntentHandler(AbstractRequestHandler):
    """Handler for adding player with name"""
    
    def can_handle(self, handler_input: HandlerInput) -> bool:
        session_attr = handler_input.attributes_manager.session_attributes
        
        return ("state" in session_attr) and (session_attr["state"] == "waitingForPlayerNames") and is_intent_name("AddPlayerIntent")(handler_input)
    
    def handle(self, handler_input: HandlerInput) -> Response:
        session_attr = handler_input.attributes_manager.session_attributes
        playerName = handler_input.request_envelope.request.intent.slots["name"].value
        
        if not ("player" in session_attr):                      # If no players are added yet, the first one gets added
            i = 0
            session_attr["player"] = {
                "0": {
                    "name": playerName,
                    "score": 0,
                },
            }
        else:
            i = len(session_attr["player"])                     # if at least one player is added yet, the next one gets added
            session_attr["player"][str(i)] = {
                "name": playerName,
                "score": 0,
            }
        if i == (session_attr["playerCount"] - 1):              # If all players are added now
            session_attr["state"] = "waitingForDifficulty"
            
            speech_text = "Okay! Now that we are all present, on which difficulty do you wanna play?"
            reprompt = "On which difficulty do you wanna play?"
        else:
            speech_text = ("Okay! Player "+ str(i+2) +" what is your name?")
            reprompt = ("Player "+ str(i+2) +" what is your name?")
            
        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        speech_text = "You can say hello to me!"

        handler_input.response_builder.speak(speech_text).ask(speech_text)
        return handler_input.response_builder.response

class setDifficultyIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input: HandlerInput) -> bool:
        session_attr = handler_input.attributes_manager.session_attributes
        
        return "state" in session_attr and session_attr["state"] == "waitingForDifficulty" and is_intent_name("setDifficulty")(handler_input)
    def handle(self, handler_input: HandlerInput):
        session_attr = handler_input.attributes_manager.session_attributes
        difficulty = handler_input.request_envelope.request.intent.slots["requestedDifficulty"].value
        session_attr["difficulty"] = str(difficulty)

        response_text = "The difficulty has been set to "+difficulty
        handler_input.response_builder.speak(response_text)

        return handler_input.response_builder.response
class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input: HandlerInput) -> Response:
        speech_text = "Goodbye!"

        handler_input.response_builder.speak(speech_text)
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """
    This handler will not be triggered except in supported locales,
    so it is safe to deploy on any locale.
    """

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        speech_text = (
            "The Trivial Pursuit skill can't help you with that. "
            "You can say help")
        reprompt = "If you need help just say so"
        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """

    def can_handle(self, handler_input: HandlerInput, exception) -> bool:
        return True

    def handle(self, handler_input: HandlerInput, exception) -> Response:
        speech = "Sorry, there was some problem. Please try again!!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response

def main(req: func.HttpRequest) -> func.HttpResponse:
    sb = SkillBuilder()
    sb.skill_id = os.environ["skill_id"]
    
    sb.add_request_handler(LaunchRequestHandler())
    sb.add_request_handler(YesIntentHandler())
    sb.add_request_handler(NumberOfPlayersIntentHandler())
    sb.add_request_handler(AddPlayerIntentHandler()) 
    sb.add_request_handler(setDifficultyIntentHandler())
    sb.add_request_handler(HelpIntentHandler())
    sb.add_request_handler(CancelOrStopIntentHandler())
    sb.add_request_handler(FallbackIntentHandler())
    sb.add_request_handler(SessionEndedRequestHandler())

    sb.add_exception_handler(CatchAllExceptionHandler())
    
    webservice_handler = WebserviceSkillHandler(skill=sb.create())
    response = webservice_handler.verify_request_and_dispatch(req.headers, req.get_body().decode("utf-8"))
    
    return func.HttpResponse(json.dumps(response),mimetype="application/json")