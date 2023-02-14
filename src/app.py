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
# - This project is under active development
#
# @section todo_main TODO
# - Implement game logic
#
# @section author_main Authors
# - Justin Stahl
# - Niklas Klemens
# - Felicitas Fuhrmann

##
# @file app.py
#    
# @brief Main file for the entire programm
#    
# @section description_app Description
# The pillar of the entire programm, containing the main-method, all Intent-Handler and the entire game logic.
#    
# @section libraries_app Libraries/Modules
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
# - game_api
#   - Local import; manages api call and contains game logic and utility functions

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name, get_supported_interfaces
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_webservice_support.webservice_handler import WebserviceSkillHandler
from ask_sdk_model.interfaces.alexa.presentation.apl.render_document_directive import RenderDocumentDirective
import azure.functions as func
import json
import os
import logging
import sys

# Local import
from src import game_api

game = game_api.trivia()

logger = logging.getLogger("azure.mgmt.resource")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

logger = logging.getLogger("azure.mgmt.resource")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

class LaunchRequestHandler(AbstractRequestHandler):
    """! Handler for Skill Launch"""
    """! @param AbstractRequestHandler Extension of the class *AbstractRequestHandler*"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if the Request inside the Handler Input is from type *LaunchRequest*."""
        """! @param handler_input Contains the request type.
            @return Returns an Boolean value
        """

        return is_request_type("LaunchRequest")(handler_input) or is_request_type("LaunchIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        """! Adds the session attribute *state* and sets it to *introduced*. Also the Response gets built to greet the user and asks if the game should start."""
        """! @param handler_input Contains methods to manipulate the session attributes and build the Response.
            @return Returns an Response obj which includes the generated Response
        """
        
        _session_attr = handler_input.attributes_manager.session_attributes
        
        
        _speech_text = "Welcome to our Trivia Gameshow. Would you like to start a game?"
        _reprompt = "If you need help, just say so"

        _session_attr["state"] = "introduced"
        handler_input.response_builder.speak(_speech_text).ask(_reprompt)
        return handler_input.response_builder.response


class YesIntentHandler(AbstractRequestHandler):
    """! Handler for Yes Intent"""
    """! @param AbstractRequestHandler Extension of the class *AbstractRequestHandler*"""
    
    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if he Request inside the Handler Input has the intent name *AMAZON.YesIntent*."""
        """! @param handler_input Contains the intent name.
            @return Returns an Boolean value
        """
        
        return is_intent_name("AMAZON.YesIntent")(handler_input)
    
    def handle(self, handler_input: HandlerInput) -> Response:
        """! Sets the session attribute *state* to *waitingForPlayerCount* and the Response gets built to asks the user how many players they are."""
        """! @param handler_input Contains methods to manipulate the session attributes and build the Response.
            @return Returns an Response obj which includes the generated Response
        """
        
        _session_attr = handler_input.attributes_manager.session_attributes
        if ("state" in _session_attr) and (_session_attr["state"] == "introduced"):

            _session_attr["playerCount"] = 0
            
            _speech_text = "Thats cool! How many players are you?"
            _reprompt = "How many players are you?"
            
            _session_attr["state"] = "waitingForPlayerCount"
            handler_input.response_builder.speak(_speech_text).ask(_reprompt)
            return handler_input.response_builder.response

class NumberOfPlayersIntentHandler(AbstractRequestHandler):
    """! Handler for player count"""
    """! @param AbstractRequestHandler Extension of the class *AbstractRequestHandler*"""
    
    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if the Request inside the Handler Input has the session attribute *state* set to *waitingForPlayerCount* 
            and the intent name is *NumberOfPlayersIntent*. 
        """
        """! @param handler_input Contains the session attribute and intent name.
            @return Returns an Boolean value
        """
        
        _session_attr = handler_input.attributes_manager.session_attributes
        
        return ("state" in _session_attr) and (_session_attr["state"] == "waitingForPlayerCount") and is_intent_name("NumberOfPlayersIntent")(handler_input)
    
    def handle(self, handler_input: HandlerInput) -> Response:
        """! Sets the session attribute *state* to *waitingForPlayerNames*, adds the session attribute *playerCount* 
            and sets it to the value stated in the request. Also the Response gets built to asks the first user which color he wants.
        """
        """! @param handler_input Contains methods to manipulate the session attributes and build the Response.
            @return Returns an Response obj which includes the generated Response
        """
        
        _session_attr = handler_input.attributes_manager.session_attributes
        playerCount = int(handler_input.request_envelope.request.intent.slots["count"].value)
        _session_attr["playerCount"] = playerCount
        
        if playerCount > 1:
            _speech_text = "Okay. Player one, which color do you want?"
        else:
            _speech_text = "Okay. Which color do you want?"
        _reprompt = "Which color do you want?"
        
        _session_attr["state"] = "waitingForPlayerColor"
        handler_input.response_builder.speak(_speech_text).ask(_reprompt)
        return handler_input.response_builder.response

class AddPlayerIntentHandler(AbstractRequestHandler):
    """! Handler for adding player(s) with a color"""
    """! @param AbstractRequestHandler Extension of the class *AbstractRequestHandler*"""
    
    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if the Request inside the Handler Input has the session attribute *state* set to *waitingForPlayerColor* 
            and the intent name is *AddPlayerIntent*. 
        """
        """! @param handler_input Contains the session attribute and intent name.
            @return Returns an Boolean value
        """
        
        _session_attr = handler_input.attributes_manager.session_attributes
        
        return ("state" in _session_attr) and (_session_attr["state"] == "waitingForPlayerColor") and is_intent_name("AddPlayerIntent")(handler_input)
    
    def handle(self, handler_input: HandlerInput) -> Response:
        """! Appends a new player with his stated color from the request to the session attribute *player*, which is a dictionary. 
            If it does not exist yet, it gets added. If all players are added (session attribute *playerCount* == keys in *player*), the session attribute *state*
            gets set to *waitingForDifficulty* and the Response gets built to asks the user, on which difficulty he want to play. 
            If not, the built Response asks the next player for his color.
        """
        """! @param handler_input Contains methods to manipulate the session attributes and build the Response.
            @return Returns an Response obj which includes the generated Response
        """
        
        _session_attr = handler_input.attributes_manager.session_attributes
        playerColor = handler_input.request_envelope.request.intent.slots["color"].resolutions.resolutions_per_authority[0].values[0].value.name
        
        if not ("player" in _session_attr):                      # If no players are added yet, the first one gets added
            _i = 0
            _session_attr["player"] = {
                "0": {
                    "color": playerColor,
                    "score": 0,
                },
            }
        else:
            _i = len(_session_attr["player"])                    # if at least one player is added yet, the next one gets added
            _session_attr["player"][str(_i)] = {
                "color": playerColor,
                "score": 0,
            }
        if _i == (_session_attr["playerCount"] - 1):             # If all players are added now
            _session_attr["state"] = "waitingForDifficulty"
            
            _speech_text = "Okay! Now that we are ready, on which difficulty do you want to play? You can choose between easy, medium and hard."
            _reprompt = "On which difficulty do you want to play? You can select either easy,medium or hard."
        else:
            _speech_text = ("Okay! Player "+ str(_i+2) +" which color do you want?")
            _reprompt = ("Player "+ str(_i+2) +" which color do you want?")
            
        handler_input.response_builder.speak(_speech_text).ask(_reprompt)
        return handler_input.response_builder.response

class SetDifficultyIntentHandler(AbstractRequestHandler):
    """! Handler for setting the difficulty"""
    """! @param AbstractRequestHandler Extension of the class *AbstractRequestHandler*"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if the Request inside the Handler Input has the session attribute *state* set to *waitingForDifficulty* 
            and the intent name is *SetDifficultyIntent*. 
        """
        """! @param handler_input Contains the session attribute and intent name.
            @return Returns an Boolean value
        """
        
        _session_attr = handler_input.attributes_manager.session_attributes
        
        return ("state" in _session_attr) and (_session_attr["state"] == "waitingForDifficulty") and is_intent_name("SetDifficultyIntent")(handler_input)
        
    def handle(self, handler_input: HandlerInput) -> Response:
        """! Sets the session attribute *state* to *waitingForCategory*, adds the session attribute *difficulty* 
            and sets it to the value stated in the request. Also builds the Response to repeat the difficulty set.
        """
        """! @param handler_input Contains methods to manipulate the session attributes and build the Response.
            @return Returns an Response obj which includes the generated Response
        """

        _session_attr = handler_input.attributes_manager.session_attributes
        print(handler_input.request_envelope.request.intent.slots["difficulty"].resolutions.resolutions_per_authority[0])
        _difficulty = handler_input.request_envelope.request.intent.slots["difficulty"].resolutions.resolutions_per_authority[0].values[0].value.name
        _session_attr["difficulty"] = _difficulty
        

        _speech_text = f"The difficulty has been set to {_difficulty}. Which categories do you want to use? You can choose between Geography, History, Sports and Hobbies, Art, Entertainment and Science."
        _reprompt = "Which categories do you want to use? You can pick between Geography, History, Sports and Hobbies, Art, Entertainment and Science."

        _session_attr["state"] = "waitingForCategory"
        handler_input.response_builder.speak(_speech_text).ask(_reprompt)
        self.launch_screen(handler_input)
        return handler_input.response_builder.response

    def supports_apl(self, handler_input):
        supported_ifaces = get_supported_interfaces(handler_input)
        return supported_ifaces.alexa_presentation_apl != None

    def launch_screen(self,handler_input):
        if self.supports_apl(handler_input):
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="documentToken",
                    document={

                        "type": "Link",
                        "src": "doc://alexa/apl/documents/Categories"
                    }
                )
            )


class SelectCategoryIntentHandler(AbstractRequestHandler):
    """! Handler for setting the categorys and starting the game"""
    """! @param AbstractRequestHandler Extension of the class *AbstractRequestHandler*"""
    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if the Request inside the Handler Input has the session attribute *state* set to *waitingForCategory* 
            and the intent name is *SelectCategoryIntent*. 
        """
        """! @param handler_input Contains the session attribute and intent name.
            @return Returns an Boolean value
        """
        _session_attr = handler_input.attributes_manager.session_attributes
        
        return ("state" in _session_attr) and is_intent_name("SelectCategoryIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        """! \todo Sets the session attributes *state* to "question1", *categories* to the value got from handler_input, 
            builds the Response to announce that the game will start now and asks the first question.
        """
        """! @param handler_input Contains methods to manipulate the session attributes and build the Response."""
        _alexa = handler_input.response_builder

        _session_attr = handler_input.attributes_manager.session_attributes
        _categories = handler_input.request_envelope.request.intent.slots["categoryname"].resolutions.resolutions_per_authority[0].values[0].value.name
        
        _session_attr["categories"] = _categories

        game.getQuestions(categories=_categories, difficulty=_session_attr["difficulty"])
        _firstPlayer = _session_attr["player"]["0"]["color"]

        _speech_text = "pep"
        _alexa.speak(_speech_text)
        return _alexa.response

        game.selectQuestion()
        _question = {}
        with open("aplquestion.json", "r") as out_file:
            _question = out_file.json()


        _speech_text = "Okay. The Game starts in 3 .. 2 .. 1 ... Please answer each question with A, B, C or D."
        _alexa.speak(_speech_text)
        _speech_text = f"Here is your first question {_firstPlayer}: {_question['question']}"
        _alexa.speak(_speech_text)
        _speech_text = f"The possible answers are {_question['answ'][0]}"
        _alexa.speak(_speech_text)
        self.launch_screen(handler_input)
        _session_attr["questions"] = _question
        _session_attr["state"] = "question2"

        return _alexa.response

    def supports_apl(self, handler_input):
        # Checks whether APL is supported by the User's device
        supported_interfaces = get_supported_interfaces(
            handler_input)
        return supported_interfaces.alexa_presentation_apl != None

    def launch_screen(self, handler_input):
        # Only add APL directive if User's device supports APL
        if self.supports_apl(handler_input):
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="documentToken",
                    document={
                        "type": "Link",
                        "src": "doc://alexa/apl/documents/TP-Interface"
                    },
                    datasources="aplquestion.json"
                )
            )


class QuestionAnswerIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if the Request inside the Handler Input has the intent name *Answer*."""
        """! @param handler_input Contains the intent name.
            @return Returns an Boolean value
        """
            
        return is_intent_name("AnswerIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        _alexa = handler_input.response_builder

        _session_attr = handler_input.attributes_manager.session_attributes
        _answerHandle = handler_input.request_envelope.request.intent.slots["answerSlot"].resolutions.resolutions_per_authority[0].values[0].value.name
        _question = {}
        with open("aplquestion.json", "r") as out_file:
            _question = out_file.json()

        if _answerHandle == "A":
            _answer = _question.answ[0]
        if _answerHandle == "B":
            _answer = _question.answ[1]
        if _answerHandle == "C":
            _answer = _question.answ[2]
        if _answerHandle == "D":
            _answer = _question.answ[3]

        
        cor = game.checkcorrect(_answer, _question.question)
        if cor == True:
            return(
                handler_input.response_builder
                    .add_directive(
                        RenderDocumentDirective(
                            token="soundToken",
                            document={
                                "type": "Link",
                                "src": "doc://alexa/apla/documents/correct"
                            },
                            datasources={}
                        )
                )
                .response
            )
        elif cor == False:
            return(
                handler_input.response_builder
                    .add_directive(
                        RenderDocumentDirective(
                            token="soundToken",
                            document={
                                "type": "Link",
                                "src": "doc://alexa/apla/documents/wrong"
                            },
                            datasources={}
                        )
                )
                .response
            )
        

class HelpIntentHandler(AbstractRequestHandler):
    """! Handler for Help Intent"""
    """! @param AbstractRequestHandler Extension of the class *AbstractRequestHandler*"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if the Request inside the Handler Input has the intent name *AMAZON.HelpIntent*."""
        """! @param handler_input Contains the intent name.
            @return Returns an Boolean value
        """
            
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        """! \todo Builds Response that helps the user use the Skill correctly"""
        """! @param handler_input Contains the methods to build the Response
            @return Returns an Response obj which includes the generated Response
        """
        
        return handler_input.response_builder.response

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """! Single handler for Cancel and Stop Intent"""
    """! @param AbstractRequestHandler Extension of the class *AbstractRequestHandler*"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if the Request inside the Handler Input has the intent name *AMAZON.CancelIntent* or *AMAZON.StopIntent*."""
        """! @param handler_input Contains the intent name.
            @return Returns an Boolean value
        """
        
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input: HandlerInput) -> Response:
        """! Builds the Response that says goodbye to the user."""
        """! @param handler_input Contains the methods to build the Response
            @return Returns an Response obj which includes the generated Response
        """
        
        _speech_text = "Thanks for playing our Trivial Pursuit game. See you soon!"
        _session_attr = handler_input.attributes_manager.session_attributes
        _session_attr["state"] = "None"

        handler_input.response_builder.speak(_speech_text)
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """! This handler will not be triggered except in supported locales, so it is safe to deploy on any locale"""
    """! @param AbstractRequestHandler Extension of the class *AbstractRequestHandler*"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if the Request inside the Handler Input has the intent name *AMAZON.FallbackIntent*."""
        """! @param handler_input Contains the intent name.
            @return Returns an Boolean value
        """
        
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        """! Builds the Response that the Skill dont know what to do"""
        """! @param handler_input Contains the methods to build the Response
            @return Returns an Response obj which includes the generated Response
        """
        
        _speech_text = (
            "The Trivial Pursuit skill can't help you with that. "
            "You can say help")
        _reprompt = "If you need help just say so"
        handler_input.response_builder.speak(_speech_text).ask(_reprompt)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """! Handler for Session End"""
    """! @param AbstractRequestHandler Extension of the class *AbstractRequestHandler*"""

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if the Request inside the Handler Input is from type *SessionEndedRequest*."""
        """! @param handler_input Contains the request type.
            @return Returns an Boolean value
        """
        
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        """! \todo Handler for clean up tasks after stop of the programm"""
        """! @param handler_input Contains the methods to build the Response
            @return Returns an Response obj which includes the generated Response
        """
        
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """! Catch all exception handler and respond with custom message"""
    """! @param AbstractRequestHandler Extension of the class *AbstractRequestHandler*"""

    def can_handle(self, handler_input: HandlerInput, exception) -> bool:
        """! Always returns true because it only gets called if an exception occurs"""
        """! @param handler_input    Contains the request type.
            @param exception        Contains the thrown exception.
            @return Returns the Boolean value *true*
        """
        
        return True

    def handle(self, handler_input: HandlerInput, exception) -> Response:
        """! Builds the Response that a problem has occured"""
        """! @param handler_input    Contains the methods to build the Response
            @param exception        Contains the thrown exception
            @return Returns an Response obj which includes the generated Response
        """
        
        _speech_text = "Sorry, there was some problem. Please try again!!"
        handler_input.response_builder.speak(_speech_text).ask(_speech_text)

        return handler_input.response_builder.response

def main(req: func.HttpRequest) -> func.HttpResponse:
    """! The main function initialises the Skill with all avaible handlers and validates that the request was meant for this specific skill. 
        It also converts incomming HTTP headers and bodys into native format of dict and str and vice versa
    """
    """! @param req Contains the incomming request in an azure.functions.HttpRequest obj
        @return Returns an azure.functions.HttpResponse obj which includes the http response
    """
    
    _sb = SkillBuilder()
    _sb.skill_id = os.environ["SKILL_ID"]
    
    _sb.add_request_handler(LaunchRequestHandler())
    _sb.add_request_handler(YesIntentHandler())
    _sb.add_request_handler(NumberOfPlayersIntentHandler())
    _sb.add_request_handler(AddPlayerIntentHandler()) 
    _sb.add_request_handler(SetDifficultyIntentHandler())
    _sb.add_request_handler(SelectCategoryIntentHandler())
    _sb.add_request_handler(HelpIntentHandler())
    _sb.add_request_handler(CancelOrStopIntentHandler())
    _sb.add_request_handler(FallbackIntentHandler())
    _sb.add_request_handler(SessionEndedRequestHandler())

    _sb.add_exception_handler(CatchAllExceptionHandler())
    
    _webservice_handler = WebserviceSkillHandler(skill=_sb.create())
    response = _webservice_handler.verify_request_and_dispatch(req.headers, req.get_body().decode("utf-8"))
    
    return func.HttpResponse(json.dumps(response),mimetype="application/json")