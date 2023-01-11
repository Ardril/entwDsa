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
from ask_sdk_core.utils import is_request_type, is_intent_name, get_supported_interfaces
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_webservice_support.webservice_handler import WebserviceSkillHandler
from ask_sdk_model.interfaces.alexa.presentation.apl.render_document_directive import RenderDocumentDirective
import azure.functions as func
import json
import os
import game_api

global game 
game = game_api.trivia()

CAT_DATASOURCE = {
    "trivia_categories": [
            {
                "id": 9,
                "name": "General Knowledge"
            },
            {
                "id": 10,
                "name": "Entertainment: Books"
            },
            {
                "id": 11,
                "name": "Entertainment: Film"
            },
            {
                "id": 12,
                "name": "Entertainment: Music"
            },
            {
                "id": 13,
                "name": "Entertainment: Musicals & Theatres"
            },
            {
                "id": 14,
                "name": "Entertainment: Television"
            },
            {
                "id": 15,
                "name": "Entertainment: Video Games"
            },
            {
                "id": 16,
                "name": "Entertainment: Board Games"
            },
            {
                "id": 17,
                "name": "Science & Nature"
            },
            {
                "id": 18,
                "name": "Science: Computers"
            },
            {
                "id": 19,
                "name": "Science: Mathematics"
            },
            {
                "id": 20,
                "name": "Mythology"
            },
            {
                "id": 21,
                "name": "Sports"
            },
            {
                "id": 22,
                "name": "Geography"
            },
            {
                "id": 23,
                "name": "History"
            },
            {
                "id": 24,
                "name": "Politics"
            },
            {
                "id": 25,
                "name": "Art"
            },
            {
                "id": 26,
                "name": "Celebrities"
            },
            {
                "id": 27,
                "name": "Animals"
            },
            {
                "id": 28,
                "name": "Vehicles"
            },
            {
                "id": 29,
                "name": "Entertainment: Comics"
            },
            {
                "id": 30,
                "name": "Science: Gadgets"
            },
            {
                "id": 31,
                "name": "Entertainment: Japanese Anime & Manga"
            },
            {
                "id": 32,
                "name": "Entertainment: Cartoon & Animations"
            }
        ]
        }
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
        
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["state"] = "introduced"
        
        speech_text = "Welcome to our Trivial Pursuit Game. Would you like to start a game?"
        reprompt = "If you need help, just say so"

        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return (handler_input.response_builder.response)


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
    """! @param AbstractRequestHandler Extension of the class *AbstractRequestHandler*"""
    
    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if the Request inside the Handler Input has the session attribute *state* set to *waitingForPlayerCount* 
            and the intent name is *NumberOfPlayersIntent*. 
        """
        """! @param handler_input Contains the session attribute and intent name.
            @return Returns an Boolean value
        """
        
        session_attr = handler_input.attributes_manager.session_attributes
        
        return ("state" in session_attr) and (session_attr["state"] == "waitingForPlayerCount") and is_intent_name("NumberOfPlayersIntent")(handler_input)
    
    def handle(self, handler_input: HandlerInput) -> Response:
        """! Sets the session attribute *state* to *waitingForPlayerNames*, adds the session attribute *playerCount* 
            and sets it to the value stated in the request. Also the Response gets built to asks the first user which color he wants.
        """
        """! @param handler_input Contains methods to manipulate the session attributes and build the Response.
            @return Returns an Response obj which includes the generated Response
        """
        
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["state"] = "waitingForPlayerColor"
        playerCount = int(handler_input.request_envelope.request.intent.slots["count"].value)
        session_attr["playerCount"] = playerCount
        
        if playerCount > 1:
            speech_text = "Okay. Player one, which color do you want?"
        else:
            speech_text = "Okay. Which color do you want?"
        reprompt = "Which color do you want?"
        
        handler_input.response_builder.speak(speech_text).ask(reprompt)
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
        
        session_attr = handler_input.attributes_manager.session_attributes
        
        return ("state" in session_attr) and (session_attr["state"] == "waitingForPlayerColor") and is_intent_name("AddPlayerIntent")(handler_input)
    
    def handle(self, handler_input: HandlerInput) -> Response:
        """! Appends a new player with his stated color from the request to the session attribute *player*, which is a dictionary. 
            If it does not exist yet, it gets added. If all players are added (session attribute *playerCount* == keys in *player*), the session attribute *state*
            gets set to *waitingForDifficulty* and the Response gets built to asks the user, on which difficulty he want to play. 
            If not, the built Response asks the next player for his color.
        """
        """! @param handler_input Contains methods to manipulate the session attributes and build the Response.
            @return Returns an Response obj which includes the generated Response
        """
        
        session_attr = handler_input.attributes_manager.session_attributes
        playerColor = handler_input.request_envelope.request.intent.slots["color"].value
        
        if not ("player" in session_attr):                      # If no players are added yet, the first one gets added
            _i = 0
            session_attr["player"] = {
                "0": {
                    "color": playerColor,
                    "score": 0,
                },
            }
        else:
            _i = len(session_attr["player"])                    # if at least one player is added yet, the next one gets added
            session_attr["player"][str(_i)] = {
                "color": playerColor,
                "score": 0,
            }
        if _i == (session_attr["playerCount"] - 1):             # If all players are added now
            session_attr["state"] = "waitingForDifficulty"
            
            speech_text = "Okay! Now that we are all present, on which difficulty do you want to play?"
            reprompt = "On which difficulty do you want to play?"
        else:
            speech_text = ("Okay! Player "+ str(_i+2) +" which color do you want?")
            reprompt = ("Player "+ str(_i+2) +" which color do you want?")
            
        handler_input.response_builder.speak(speech_text).ask(reprompt)
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
        
        session_attr = handler_input.attributes_manager.session_attributes
        
        return ("state" in session_attr) and (session_attr["state"] == "waitingForDifficulty") and is_intent_name("SetDifficultyIntent")(handler_input)
        
    def handle(self, handler_input: HandlerInput) -> Response:
        """! Sets the session attribute *state* to *waitingForCategory*, adds the session attribute *difficulty* 
            and sets it to the value stated in the request. Also builds the Response to repeat the difficulty set.
        """
        """! @param handler_input Contains methods to manipulate the session attributes and build the Response.
            @return Returns an Response obj which includes the generated Response
        """
        
        session_attr = handler_input.attributes_manager.session_attributes
        difficulty = handler_input.request_envelope.request.intent.slots["difficulty"].value
        session_attr["difficulty"] = difficulty
        session_attr["state"] = "waitingForCategory"

        speech_text = f"The difficulty has been set to {difficulty}. Which categories do you want to use? Just say 'categories' and i will list them for you."
        reprompt = "Which categories do you want to use? "

        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response

class ListCategoriesHandler(AbstractRequestHandler):

    def can_handle(self, handler_input: HandlerInput) -> bool:
        """! Returns true if the Request inside the Handler Input has the session attribute *state* set to *waitingForCategory* 
            and the intent name is *SelectCategoryIntent*. 
        """
        """! @param handler_input Contains the session attribute and intent name.
            @return Returns an Boolean value
        """
        
        session_attr = handler_input.attributes_manager.session_attributes
        return ("state" in session_attr) and (session_attr["state"] == "waitingForCategory") and is_intent_name("listCategoriesIntent")(handler_input)

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
                    },
                    datasources=CAT_DATASOURCE
                )
            )

    def handle(self, handler_input: HandlerInput) -> Response:

        alexa = handler_input.response_builder
        session_attr = handler_input.attributes_manager.session_attributes
        self.launch_screen(handler_input)
        


        return handler_input.response_builder.response

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
        
        session_attr = handler_input.attributes_manager.session_attributes
        
        return ("state" in session_attr) and (session_attr["state"] == "waitingForCategory") and is_intent_name("selectCategoryIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        """! \todo Sets the session attributes *state* to "question1", *categories* to the value got from handler_input, 
            builds the Response to announce that the game will start now and asks the first question.
        """
        """! @param handler_input Contains methods to manipulate the session attributes and build the Response."""
        alexa = handler_input.response_builder
        session_attr = handler_input.attributes_manager.session_attributes
        #speech_text = "Which categories do you want to use?"
        categories = handler_input.request_envelope.request.intent.slot["category"].values
        hucat = game.listCategoriesByName()
        selected_cats = []
        missing_cats = ""
        for cat in categories:
            if cat not in hucat:
                missing_cats += cat
            else:
                selected_cats.append(cat)
        if missing_cats != "":
            speech_text = "Sorry,the categories"+missing_cats+"are not available at the moment"
            alexa.speak(speech_text)
        session_attr["category"] = selected_cats
        session_attr["state"] = "readyToLaunch"
        
        speech_text = "Your selected categories "+str(selected_cats)+"have been added."
        alexa.speak(speech_text).ask("Please")
        return alexa.response

class TellCategoriesIntentHandler(AbstractRequestHandler):
    """! Handler to tell which categories are avaible to choose"""
    """! @param AbstractRequestHandler Extension of the class *AbstractRequestHandler*"""
    def can_handle(self, handler_input: HandlerInput):
        """! Returns true if the Request inside the Handler Input has the session attribute *state* set to *waitingForCategory* 
            and the intent name is *tellCategories*. 
        """
        """! @param handler_input Contains the session attribute and intent name.
            @return Returns an Boolean value
        """
        session_attr = handler_input.attributes_manager.session_attributes
        
        return ("state" in session_attr) and (session_attr["state"] == "waitingForCategory") and is_intent_name("tellCategories")(handler_input)

    def handle(self, handler_input: HandlerInput):
        """! \todo TODO"""
        """! @param handler_input Contains the methods to build the Response
            @return Returns an Response obj which includes the generated Response
        """
        session_attr = handler_input.attributes_manager.session_attributes
        #speech_text = "Which categories do you want to use?"
        categories = handler_input.request_envelope.request.intent.slot["category"].values
        hucat = game.listCategoriesByName()
        speech_text = "The following categories are available"
        for cat in hucat:
            speech_text += cat['id'] + cat['name'] + ","
        handler_input.response_builder.speak(speech_text)
        return handler_input.response_builder.response

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
        
        speech_text = "Goodbye!"

        handler_input.response_builder.speak(speech_text)
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
        
        speech_text = (
            "The Trivial Pursuit skill can't help you with that. "
            "You can say help")
        reprompt = "If you need help just say so"
        handler_input.response_builder.speak(speech_text).ask(reprompt)
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
        
        speech = "Sorry, there was some problem. Please try again!!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response

def main(req: func.HttpRequest) -> func.HttpResponse:
    """! The main function initialises the Skill with all avaible handlers and validates that the request was meant for this specific skill. 
        It also converts incomming HTTP headers and bodys into native format of dict and str and vice versa
    """
    """! @param req Contains the incomming request in an azure.functions.HttpRequest obj
        @return Returns an azure.functions.HttpResponse obj which includes the http response
    """
    
    sb = SkillBuilder()
    sb.skill_id = os.environ["skill_id"]
    
    sb.add_request_handler(LaunchRequestHandler())
    sb.add_request_handler(YesIntentHandler())
    sb.add_request_handler(NumberOfPlayersIntentHandler())
    sb.add_request_handler(AddPlayerIntentHandler()) 
    sb.add_request_handler(SetDifficultyIntentHandler())
    sb.add_request_handler(SelectCategoryIntentHandler())
    sb.add_request_handler(TellCategoriesIntentHandler())
    sb.add_request_handler(ListCategoriesHandler())
    sb.add_request_handler(HelpIntentHandler())
    sb.add_request_handler(CancelOrStopIntentHandler())
    sb.add_request_handler(FallbackIntentHandler())
    sb.add_request_handler(SessionEndedRequestHandler())

    sb.add_exception_handler(CatchAllExceptionHandler())
    
    _webservice_handler = WebserviceSkillHandler(skill=sb.create())
    response = _webservice_handler.verify_request_and_dispatch(req.headers, req.get_body().decode("utf-8"))
    
    return func.HttpResponse(json.dumps(response),mimetype="application/json")