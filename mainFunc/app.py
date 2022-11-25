"""! @brief Main file for the entire programm"""

##
# @mainpage Trivial Pursuit Amazon Alexa Skill
#  
# @section description_main Description
# An Amazon Alexa Skill in Style of the popular boardgame "Trivial Pursuit", which first asks a few configuration questions (e.g. how many players are playing) 
# and then continues asking question about a lot of different topics.
#
# @section notes_main Notes
# - Written in Python
# - Code hosted on a Microsoft Azure Functions server

##
# @file app.py
#    
# @brief Main file for the entire programm
#    
# @section description_app Description
# The pillar of the entire programm, containing the main-method, all Intent-Handler and the entire game logic.
#    
# @section libraries_main Libraries/Modules
# - ask_sdk_core (components)
#   - Needed for all handlers
# - ask_sdk_model (component)
#   - Acces to class Response
# - ask_sdk_webservice_support (component)
#   - Needed to convert request/Response <-> HTTP
# - azure.functions
#   - Needed for Azure Functions hosting
# - json
#   - Needed to convert Response -> HTTP
# - os
#   - Acces to environment variables on Azure Functions server
#  
# @section todo_app TODO
# - Implement game logic
#    
# @section author_app Authors
# - Justin Stahl
# - Niklas Klemens
# - Felicitas Fuhrmann

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
    """! Handler for Skill Launch"""
    """! @param AbstractRequestHandler Responsible for processing Request inside the Handler Input and generating Response."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if the Request inside the Handler Input is from type *LaunchRequest*."""
        """! @param handler_input Contains the request type."""
    
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        """! Adds the session attribute *state* and sets it to *introduced*. Also the Response gets built to greet the user and asks if the game should start."""
        """! @param handler_input Contains methods to manipulate the session attributes and build the Response."""
        
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["state"] = "introduced"
        
        speech_text = "Welcome to our Trivial Pursuit Game. Would you like to start a game?"
        reprompt = "If you need help, just say so"

        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response


class YesIntentHandler(AbstractRequestHandler):
    """! Handler for Yes Intent"""
    """! @param AbstractRequestHandler Responsible for processing Request inside the Handler Input and generating Response."""
    
    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if he Request inside the Handler Input has the intent name *AMAZON.YesIntent*."""
        """! @param handler_input Contains the intent name."""
        
        return is_intent_name("AMAZON.YesIntent")(handler_input)
    
    def handle(self, handler_input: HandlerInput) -> Response:
        """! Sets the session attribute *state* to *waitingForPlayerCount* and the Response gets built to asks the user how many players they are."""
        """! @param handler_input Contains methods to manipulate the session attributes and build the Response."""
        
        session_attr = handler_input.attributes_manager.session_attributes
        if ("state" in session_attr) and (session_attr["state"] == "introduced"):
            session_attr["state"] = "waitingForPlayerCount"
            session_attr["playerCount"] = 0
            
            speech_text = "Thats cool! How many players are you?"
            reprompt = "How many players are you?"
            
            handler_input.response_builder.speak(speech_text).ask(reprompt)
            return handler_input.response_builder.response

class NumberOfPlayersIntentHandler(AbstractRequestHandler):
    """! Handler for player count"""
    """! @param AbstractRequestHandler Responsible for processing Request inside the Handler Input and generating Response."""
    
    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if the Request inside the Handler Input has the session attribute *state* set to *waitingForPlayerCount* 
            and the intent name is *NumberOfPlayersIntent*. 
        """
        """! @param handler_input Contains the session attribute and intent name."""
        
        session_attr = handler_input.attributes_manager.session_attributes
        
        return ("state" in session_attr) and (session_attr["state"] == "waitingForPlayerCount") and is_intent_name("NumberOfPlayersIntent")(handler_input)
    
    def handle(self, handler_input: HandlerInput) -> Response:
        """! Sets the session attribute *state* to *waitingForPlayerNames*, adds the session attribute *playerCount* 
            and sets it to the value stated in the request. Also the Response gets built to asks the first user how his name is.
        """
        """! @param handler_input Contains methods to manipulate the session attributes and build the Response."""
        
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
    """! Handler for adding player(s) with name"""
    """! @param AbstractRequestHandler Responsible for processing Request inside the Handler Input and generating Response."""
    
    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if the Request inside the Handler Input has the session attribute *state* set to *waitingForPlayerNames* 
            and the intent name is *AddPlayerIntent*. 
        """
        """! @param handler_input Contains the session attribute and intent name."""
        
        session_attr = handler_input.attributes_manager.session_attributes
        
        return ("state" in session_attr) and (session_attr["state"] == "waitingForPlayerNames") and is_intent_name("AddPlayerIntent")(handler_input)
    
    def handle(self, handler_input: HandlerInput) -> Response:
        """! Appends a new player with his stated name from the request to the session attribute *player*, which is a dictionary. 
            If it does not exist yet, it gets added. If all players are added (session attribute *playerCount* == keys in *player*), the session attribute *state*
            gets set to *waitingForDifficulty* and the Response gets built to asks the user, on which difficulty he wanna play. 
            If not, the built Response asks the next player for his name.
        """
        """! @param handler_input Contains methods to manipulate the session attributes and build the Response."""
        
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

class SetDifficultyIntentHandler(AbstractRequestHandler):
    """! Handler for setting the difficulty"""
    """! @param AbstractRequestHandler Responsible for processing Request inside the Handler Input and generating Response."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if the Request inside the Handler Input has the session attribute *state* set to *waitingForDifficulty* 
            and the intent name is *SetDifficultyIntent*. 
        """
        """! @param handler_input Contains the session attribute and intent name."""
        
        session_attr = handler_input.attributes_manager.session_attributes
        
        return ("state" in session_attr) and (session_attr["state"] == "waitingForDifficulty") and is_intent_name("SetDifficultyIntent")(handler_input)
        
    def handle(self, handler_input: HandlerInput) -> Response:
        """! Sets the session attribute *state* to *waitingForCategory*, adds the session attribute *difficulty* 
            and sets it to the value stated in the request. Also builds the Response to repeat the difficulty set.
        """
        """! @param handler_input Contains methods to manipulate the session attributes and build the Response."""
        """! \todo Add building Response to ask for category settings"""
        
        session_attr = handler_input.attributes_manager.session_attributes
        difficulty = handler_input.request_envelope.request.intent.slots["difficulty"].value
        session_attr["difficulty"] = difficulty
        session_attr["state"] = "waitingForCategory"

        speech_text = ("The difficulty has been set to " + difficulty)  

        handler_input.response_builder.speak(speech_text)
        return handler_input.response_builder.response

class HelpIntentHandler(AbstractRequestHandler):
    """! Handler for Help Intent"""
    """! @param AbstractRequestHandler Responsible for processing Request inside the Handler Input and generating Response."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if the Request inside the Handler Input has the intent name *AMAZON.HelpIntent*."""
        """! @param handler_input Contains the intent name."""
        
        
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        """! \todo Builds Response that helps the user use the Skill correctly"""
        """! @param handler_input Contains the methods to build the Response"""
        
        return handler_input.response_builder.response

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """! Single handler for Cancel and Stop Intent"""
    """! @param AbstractRequestHandler Responsible for processing Request inside the Handler Input and generating Response."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if the Request inside the Handler Input has the intent name *AMAZON.CancelIntent* or *AMAZON.StopIntent*."""
        """! @param handler_input Contains the intent name."""
        
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input: HandlerInput) -> Response:
        """! Builds the Response that says goodbye to the user."""
        """! @param handler_input Contains the methods to build the Response"""
        
        speech_text = "Goodbye!"

        handler_input.response_builder.speak(speech_text)
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """! This handler will not be triggered except in supported locales, so it is safe to deploy on any locale"""
    """! @param AbstractRequestHandler Responsible for processing Request inside the Handler Input and generating Response."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if the Request inside the Handler Input has the intent name *AMAZON.FallbackIntent*."""
        """! @param handler_input Contains the intent name."""
        
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        """! Builds the Response that the Skill dont know what to do"""
        """! @param handler_input Contains the methods to build the Response"""
        
        speech_text = (
            "The Trivial Pursuit skill can't help you with that. "
            "You can say help")
        reprompt = "If you need help just say so"
        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """! Handler for Session End"""
    """! @param AbstractRequestHandler Responsible for processing Request inside the Handler Input and generating Response."""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if the Request inside the Handler Input is from type *SessionEndedRequest*."""
        """! @param handler_input Contains the request type."""
        
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        """! \todo Handler for clean up tasks after stop of the programm"""
        """! @param handler_input Contains the methods to build the Response"""
        
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """! Catch all exception handler and respond with custom message"""
    """! @param AbstractRequestHandler Responsible for processing Request inside the Handler Input and generating Response."""

    def can_handle(self, handler_input: HandlerInput, exception) -> bool:
        """! Returns true."""
        """! @param handler_input    Contains the request type.
            @param exception        Contains the thrown exception.
        """
        
        return True

    def handle(self, handler_input: HandlerInput, exception) -> Response:
        """! Builds the Response that a problem has occured"""
        """! @param handler_input    Contains the methods to build the Response
            @param exception        Contains the thrown exception
        """
        
        speech = "Sorry, there was some problem. Please try again!!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response

def main(req: func.HttpRequest) -> func.HttpResponse:
    """! The main function initialises the Skill with all avaible handlers and validates that the request was meant for this specific skill. 
        It also converts incomming HTTP headers and body into native format of dict and str and vice versa
    """
    """! @param req Contains the incomming request"""
    
    sb = SkillBuilder()
    sb.skill_id = os.environ["skill_id"]
    
    sb.add_request_handler(LaunchRequestHandler())
    sb.add_request_handler(YesIntentHandler())
    sb.add_request_handler(NumberOfPlayersIntentHandler())
    sb.add_request_handler(AddPlayerIntentHandler()) 
    sb.add_request_handler(SetDifficultyIntentHandler())
    sb.add_request_handler(HelpIntentHandler())
    sb.add_request_handler(CancelOrStopIntentHandler())
    sb.add_request_handler(FallbackIntentHandler())
    sb.add_request_handler(SessionEndedRequestHandler())

    sb.add_exception_handler(CatchAllExceptionHandler())
    
    webservice_handler = WebserviceSkillHandler(skill=sb.create())
    response = webservice_handler.verify_request_and_dispatch(req.headers, req.get_body().decode("utf-8"))
    
    return func.HttpResponse(json.dumps(response),mimetype="application/json")