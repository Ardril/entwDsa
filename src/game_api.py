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
        pass


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
        resp = requests.get(url).json()

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
        # Amount
        string = "total_"+difficulty.split("=")[1]+"_question_count"
        if amount > c_resp["category_question_count"][string]:
            amount = c_resp["category_question_count"][string]-2
        amount = str(amount)
        comp.append("amount="+amount)


        url = "https://opentdb.com/api.php?"+( "&".join(comp))
        return url

    #difficulty = "" # easy,medium,hard or mixed or 1,2,3

if __name__ == "__main__":
    g = trivia()
    #g.buildUrl(5,"mc","Science",2)
    g.getQuestions(category="Science", difficulty="easy")
    g.selectQuestion()