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
# @section libraries_game_api Libraries/Modules
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


    def setupNewGame(self,game : game):
        
        return True

    

    def buildCategories(self):
        categoryResponse = requests.get("https://opentdb.com/api_category.php").json()
        self._categories = deepcopy(categoryResponse['trivia_categories'])
        #print(str(type(self._categories)))
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

    def getQuestions(self,category,difficulty):
        """Returns a list of questions that were requested from the api"""
        """! @param categories a list of categories selected by the player(s) """
        """! @param difficulty """ 
    	
        counter = 0
        questions = {}
        amm = 5
        #if(difficulty not in ["1","2","3"]) and (difficulty not in ["easy","medium","hard"]) :
        #   raise ArgumentError().message("difficulty must either be one of ['1','2','3'] or ['easy','medium','hard']")

        typ = bool(random.getrandbits(1))
        url = self.buildUrl(amm,typ,category,difficulty)
        print("url = "+url)
        resp = requests.get(url).json()
        print("resp="+str(resp))

        if resp["response_code"] != 0:
                return

        for entry in resp['results']:
                i_a = []
                q = entry['question']
                if "&quot;" in q:
                    q = q.replace("&quot;", "'")
                c_a = entry['correct_answer']
                if "&quot;" in c_a:
                    c_a = c_a.replace("&quot;", "'")
                for answ in entry['incorrect_answers']:
                    if "&quot;" in answ:
                        answ = answ.replace("&quot;", "'")
                    i_a.append(answ)
                qdict = dict(question = q, correct_answer = c_a, incorrect_answers = i_a)
                name = "question" +str(counter)
                questions[name]= qdict
                counter += 1
        
                out_file = open("checkanswer.json", "w")
                json.dump(questions, out_file, indent = 6)
                out_file.close()

        return questions


    def selectQuestion(self):
        answers = []
        questions = {}
        with open("checkanswer.json", "r") as out_file:
            questions = json.load(out_file)
        length = len(questions) - 1
        q = questions[f"question"+str(length)]["question"]
        answers.append(questions[f"question"+str(length)]["correct_answer"])
        for answ in  questions[f"question"+str(length)]["incorrect_answers"]:
            answers.append(answ)

        random.shuffle(answers)
        apldict = dict(question = q, answ = answers)

        with open("aplquestion.json", "w") as out_file:
            json.dump(apldict, out_file, indent = 6)
        return apldict




    def checkcorrect(self, selected, q):
        check_file = open("questions.json", "r+")
        check = check_file.json()
        if selected == check.q["correct_answer"]:
            check.popitem()
            json.dump(check, check_file, indent = 6)
            check_file.close()
            return True
        else:
            check.popitem()
            json.dump(check, check_file, indent = 6)
            check_file.close()
            return False







        # quest = []
        # if resp["response_code"] != 0:
        #     return
        # for question in resp['results']:
        #     print("ENG:  "+question['question'])
        #     quest.append(question['question'])
        #     #print("GER:  "+self.translation.translate(str(question['question'])))'

          


    def buildUrl(self,amount: int,typ: str,category: str,difficulty: str or int):
        comp = []
        category = category.lower()

        typ = "mc"
        #Typ
        comp.append("type=multiple")
        

        # Categories
        #comp.append("category="+str(category))
        categorylist = []
        if category == "science":
            categorylist.append("category=17")
            categorylist.append("category=18")
            categorylist.append("category=19")
            categorylist.append("category=30")

            
        if category == "art":
            categorylist.append("category=25")

        if category == "sport and hobbies":
            categorylist.append("category=28")
            categorylist.append("category=21")

        if category == "entertainment":
            categorylist.append("category=10")
            categorylist.append("category=11")
            categorylist.append("category=12")
            categorylist.append("category=13")
            categorylist.append("category=14")
            categorylist.append("category=15")
            categorylist.append("category=16")
            categorylist.append("category=29")
            categorylist.append("category=31")
            categorylist.append("category=32")

        if category == "history":
            categorylist.append("category=23")

        if category == "geography":
            categorylist.append("category=22")
        
        


        ri= random.randint(0,len(categorylist))
        print("ri ="+str(ri))
        print("len = "+str(len(categorylist)))
        cat = categorylist[ri-1]
        comp.append(cat)

        

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

        c_resp = requests.get("https://opentdb.com/api_count.php?"+str(cat)).json()
        print("c_resp ="+str(c_resp))
        # Amount
        string = "total_"+difficulty.split("=")[1]+"_question_count"
        print("test_string =="+string)
        if amount > c_resp["category_question_count"][string]:
            amount = c_resp["category_question_count"][string]-2
        amount = str(amount)
        comp.append("amount="+amount)


        url = "https://opentdb.com/api.php?"+( "&".join(comp))
        tokenstring = "&token="+str(self._TOKEN)
        url = url #+ tokenstring
        print(url)
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
    #g.buildUrl(5,"mc","Science",2)
    g.getQuestions(category="Science",difficulty="easy")
    g.selectQuestion()
