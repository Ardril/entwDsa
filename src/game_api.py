"""! @brief API-managing file"""

##
# @file game_api.py
#    
# @brief API-managing file
#    
# @section description_game_api Description
# Code in this file manages the API call to get the requested questions, contains the game logic and utility functions
#
# @section notes_game_api Notes
# For code in this file, theres only a automaticly created doxygen documentation for now
#
# @section libraries_main Libraries/Modules
# - requests
#   - Needed to send HTTP-requests to the API
# - json
#   - Needed to parse the HTTP-response from the API into json format
#  
# @section todo_game_api TODO
# - Implement game logics
# - Add doxygen comments
#    
# @section author_game_api Authors
# - Niklas Klemens
# - Justin Stahl
# - Felicitas Fuhrmann

from argparse import ArgumentError
from copy import deepcopy
import random
import requests
import json

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

    def setDifficulty(self,difficulty:str):
        if difficulty > 3 or difficulty < 1:
            raise ArgumentError(message="Difficulty must be a number between 1-3")
        self.settings["difficulty"] = difficulty
        
class trivia():
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
        print(self.listCategoriesByName())

    def setupNewGame(self,game : game):
        
        return True

    

    def buildCategories(self):
        categoryResponse = requests.get("https://opentdb.com/api_category.php").json()
        self._categories = deepcopy(categoryResponse['trivia_categories'])
        print(str(type(self._categories)))
        return self._categories
    
    def listCategoriesByName(self):
        cs = []
        for entry in self._categories:
            if(":" in entry['name']):
                entry["name"] = entry['name'].split(":")[1]
            cs.append(entry['name'])
        return cs


    def returnHumanReadableCategories(self, mode):
        if(mode != "numbers" and mode != "names"):
            raise ArgumentError().message("mode must be one of ['numbers','names']")
        hrc = deepcopy(self._categories)
        i = 1
        for cat in hrc:
            if(":" in cat["name"]):
                cat["name"] = cat["name"].split(":")[1]
            cat["number"] = i
            i += 1
            print("cat == %s",str(cat))
        return hrc
        if(mode=="numbers"):
            li = []
            for cat in hrc:
                li.append(hrc['number'])
            return li
        elif(mode=="names"):
            li = []
            for cat in hrc:
                li.append(hrc["name"])
            return li
        else:
            return hrc    

    def getQuestions(self,categories,difficulty):
        """Returns a list of questions that were requeste from the api. The amount of questions is split evenly
         based on the number of categories and the type (multiple-choice/true-false) is based on a random boolean.
         Before it is returned, the list gets shuffled once"""
        """! @param categories a list of categories selected by the player(s) """
        """! @param difficulty """ 
    	

        questions = []
        amm = int(50/len(categories))
        if(difficulty not in ["1","2","3"]) and (difficulty not in ["easy","medium","hard"]) :
            raise ArgumentError().message("difficulty must either be one of ['1','2','3'] or ['easy','medium','hard']")

        for i in range(len(categories)):
            typ = bool(random.getrandbits(1))
            url = self.buidlUrl(amm,typ,categories[i],difficulty)
            resp = requests.get(url).json()

            if resp["response_code"] != 0:
                return

            for entry in resp['results']:

                question = entry['question']
                questions.append(question)
        random.shuffle(questions)

        return questions

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

if __name__ == "__main__":
    g = trivia()