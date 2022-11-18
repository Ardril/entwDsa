from flask import Flask
from pymongo import MongoClient
from ask_sdk_core.skill_builder import SkillBuilder
from flask_ask_sdk.skill_adapter import SkillAdapter
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response
import game_api
app = Flask(__name__)

client = MongoClient(port=27017)
db=client.local

sb = SkillBuilder()

gameapi = game_api()

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["state"] = "introduced"
        
        speech_text = "Welcome to our Trivial Pursuit Game"
        ask_text = "Would you like to start a game?"

        handler_input.response_builder.speak(speech_text).ask(ask_text)
        return handler_input.response_builder.response


class YesIntentHandler(AbstractRequestHandler):
    """Handler for Yes Intent"""
    
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AMAZON.YesIntent")(handler_input)
    
    def handle(self, handler_input: HandlerInput):
        session_attr = handler_input.attributes_manager.session_attributes
        if "state" in session_attr and session_attr["state"] == "introduced":
            session_attr["state"] = "waitingForPlayerCount"
            session_attr["player"] = {{}}
            session_attr["playerCount"] = 0
            
            speech_text = "Thats cool!"
            ask_text = "How many players are you?"
            
            handler_input.response_builder.speak(speech_text).ask(ask_text)
            return handler_input.response_builder.response
        else:
            pass

class NumberOfPlayersIntentHandler(AbstractRequestHandler):
    """Handler for player count"""
    
    def can_handle(self, handler_input: HandlerInput) -> bool:
        session_attr = handler_input.attributes_manager.session_attributes
        
        return "state" in session_attr and session_attr["state"] == "waitingForPlayerCount" and is_intent_name("NumberOfPlayersIntent")(handler_input)
    
    def handle(self, handler_input: HandlerInput):
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["state"] = "waitingForPlayerNames"
        playerCount = handler_input.request_envelope.request.intent.slots["count"].value
        session_attr["playerCount"] = playerCount
        
        speech_text = "Okay."
        if playerCount > 1:
            ask_text = "Player 1, what is your name?"
        else:
            ask_text = "What is your name?"
        
        handler_input.response_builder.speak(speech_text).ask(ask_text)
        return handler_input.response_builder.response

class AddPlayerIntentHandler(AbstractRequestHandler):
    """Handler for adding player with name"""
    
    def can_handle(self, handler_input: HandlerInput) -> bool:
        session_attr = handler_input.attributes_manager.session_attributes
        
        return "state" in session_attr and session_attr["state"] == "waitingForPlayerNames" and is_intent_name("AddPlayerIntent")(handler_input)
    
    def handle(self, handler_input: HandlerInput):
        session_attr = handler_input.attributes_manager.session_attributes
        playerName = handler_input.request_envelope.request.intent.slots["name"].value
        
        for i in session_attr["player"]:    # Counts the amount of players already added
            i += 1
        if i == 0:
            session_attr["player"][0]["name"] = playerName
            session_attr["player"][0]["score"] = 0
        else:
            session_attr["player"][i+1]["name"] = playerName
            session_attr["player"][i+1]["score"] = 0
        if i == (session_attr["playerCount"] - 1):          # If all players are added now
            session_attr["state"] = "waitingForDifficulty"
            
            speech_text = "Okay!"
            ask_text = "Now that we are all present, on which difficulty do you wanna play?"
            
            handler_input.response_builder.speak(speech_text).ask(ask_text)
            return handler_input.response_builder.response
        else:
            speech_text = "Okay!"
            ask_text = "Player "+(i+1)+" what is your name?"
            
            handler_input.response_builder.speak(speech_text).ask(ask_text)
            return handler_input.response_builder.response

class StoreNameRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("StoreName")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        slots = handler_input.request_envelope.request.intent.slots
        name = slots["name"].value

        nameDoc = {
            'name': name
        }

        db.names.insert(nameDoc)

        speech_text = "Der Name wurde gespeichert."

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Name gespeichert", speech_text)).set_should_end_session(
            False)
        return handler_input.response_builder.response

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "You can say hello to me!"

        handler_input.response_builder.speak(speech_text).ask(
            speech_text).set_card(SimpleCard("Hello World", speech_text))
        return handler_input.response_builder.response

class NewGameIntentHandler(AbstractRequestHandler):
    """Handler for creating a new game"""
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return super().can_handle(handler_input)

    def handle(self, handler_input: HandlerInput):
        game_api.trivia.initGame()
        return super().handle(handler_input)

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = "Goodbye!"

        handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard("Hello World", speech_text))
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """
    This handler will not be triggered except in supported locales,
    so it is safe to deploy on any locale.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech_text = (
            "The Hello World skill can't help you with that.  "
            "You can say hello!!")
        reprompt = "You can say hello!!"
        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        app.logger.error(exception, exc_info=True)

        speech = "Sorry, there was some problem. Please try again!!"
        handler_input.response_builder.speak(speech).ask(speech)

        return handler_input.response_builder.response


sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(StoreNameRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

skill_adapter = SkillAdapter(
    skill=sb.create(), skill_id=1, app=app)


@app.route('/', methods=['GET', 'POST'])
def invoke_skill():
    return skill_adapter.dispatch_request()


if __name__ == '__main__':
    app.run()
