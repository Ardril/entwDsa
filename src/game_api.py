
from argparse import ArgumentError
from copy import deepcopy
import time
from typing import Iterable
import requests
import json 
from googletrans import Translator


class game():
    players = []    #player = ("name",points)
    questions = []  #question = (question,correct answer,incorrect_answers)
    settings = {
                'amount': 0,
                'typ': 'n',
                'categories':[],
                'difficulty':'n'
                } 
    # category is a list and could be selected from with a random function or via asking the players 
    # == > buildURL must be called once for each category
    activePlayer = None

    def addPlayer(self, player: str):
        if(self.playing):
            return False
        else:
            self.players.append({player, 0})
            return True

    def setAmount(self,amount:int):
        if amount <= 0:
            raise ArgumentError(message="amount must not be lower than 0 or bigger than 50")
        self.settings["amount"] = amount

    def setTyp(self,typ: str):
        if typ == "mc":
            self.settings["typ"] = "mc"
        elif typ == "tf":
            self.settings["typ"] = "tf"
        else:
            raise ArgumentError.message("typ must be either 'mc' or 'tf' ")

    def setCategory(self,category:int,islist = False):
        if islist:
            for cate in category:
                if category > 32 or category < 9:
                    raise ArgumentError(message="category must be a number between 9 and 32")
            for cate in category:
                self.settings["categories"].append(category)
        else:
            if category > 32 or category < 9:
                raise ArgumentError(message="category must be a number between 9 and 32")
            self.settings["categories"].append(category)

    def setDifficulty(self,difficulty:int):
        if difficulty > 3 or difficulty < 1:
            raise ArgumentError(message="Difficulty must be a number between 1-3")
        self.settings["difficulty"] = difficulty
        
class trivia():
    translation = Translator()
    _TOKEN = None
    _categories = {}
    #{"response_code":0,
    # "results":
    # [ 
    #       {
    #           "category":"Entertainment: Film",
    #           "type":"boolean",
    #           "difficulty":"easy",
    #           "question":"The film &quot;2001: A Space Odyssey&quot; was released on December 31st, 2000.",
    #           "correct_answer":"False",
    #           "incorrect_answers":["True"]
    # }
    

    def __init__(self):
        resp = requests.get("https://opentdb.com/api_token.php?command=request").json()
        self._TOKEN = resp['token']
        self.buildCategories()
        self._game = game()
        print(self.returnHumanReadableCategories())

    def setupNewGame(self,game : game):
        
        return True

    

    def buildCategories(self):
        categoryResponse = requests.get("https://opentdb.com/api_category.php").json()
        self._categories = deepcopy(categoryResponse['trivia_categories'])
        return self._categories
        
    def returnHumanReadableCategories(self):
        hrc = deepcopy(self._categories)
        i = 1
        for cat in hrc:
            if(":" in cat["name"]):
                cat["name"] = cat["name"].split(":")[1]
            cat["number"] = i
            i += 1
        return hrc

    def getQuestions(self,url):
        resp = requests.get(url).json()
        quest = []
        if resp["response_code"] != 0:
            return
        for question in resp['results']:
            print("ENG:  "+question['question'])
            quest.append(question['question'])
            #print("GER:  "+self.translation.translate(str(question['question'])))

          


    def buidlUrl(self,amount: int,typ: str,category: int,difficulty: str or int):
        if difficulty > 3 or difficulty < 1:
            raise ArgumentError(message="Difficulty must be a number between 1-3")
        if amount <= 0:
            raise ArgumentError(message="amount must not be lower than 0 or bigger than 50")
        if category > 32 or category < 9:
            raise ArgumentError(message="category must be a number between 9 and 32")
        comp = []

        # Amount 
        amount = str(amount)
        comp.append("amount="+amount)

        #Typ
        if typ == "mc":
            comp.append("type=multiple")
        elif typ == "tf":
            comp.append("type=boolean")
        else:
            raise ArgumentError.message("typ must be either mc or tf")

        # Categories
        comp.append("category="+str(category))
        
        # Difficulty
        if "str" in str(type(difficulty)):
            difficulty = "difficulty="+difficulty
        else:
            if difficulty == 1:
                difficulty = "difficulty=easy" 
            elif difficulty == 2:
                difficulty = "difficulty=medium"
            elif difficulty == 3:
                difficulty == "difficulty=hard"
        comp.append(difficulty)


        url = "https://opentdb.com/api.php?"+( "&".join(comp))
        tokenstring = "&token="+str(self._TOKEN)
        url = url + tokenstring
        return url

    #difficulty = "" # easy,medium,hard or mixed or 1,2,3
    def initGame(url,players):
        resp = requests.get(url)
        if resp.status_code != 200:
            return 
        result = json.loads(resp.json)
        questions = result["results"]





g = trivia()
