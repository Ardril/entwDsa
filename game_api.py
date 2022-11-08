
import requests
import json 
class trivia():
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
    class game():
        players = []    #player = ("name",points)
        questions = []  #question = (question,correct answer,incorrect_answers)
    def __init__():
        pass

    def buidlUrl(amount,typ,categories,difficulty):
        comp = [typ,categories,difficulty]
        comp.append("https://opentdb.com/api.php?")
        url = "&".join(comp)
        return url

    #difficulty = "" # easy,medium,hard or mixed or 1,2,3
    def initGame(url,players):
        resp = requests.get(url)
        if resp.status_code != 200:
            return 
        result = json.loads(resp.json)
        questions = result["results"]
