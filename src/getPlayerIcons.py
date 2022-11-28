import azure.functions as func
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    """! \todo Not functional yet"""
    card = req.params.get('card')
    
    if not card:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            card = req_body.get('card')

    if card:
        file_dir = os.path.dirname(os.path.realpath('__file__'))
        file_name = os.path.join(file_dir, f'../res/player_card_{card}.png')
        file_name = os.path.abspath(os.path.realpath(file_name))                # Absolut path to png

        return func.HttpResponse(mimetype="image/png")
    else:
        return func.HttpResponse(
             "Pass a card (color, entity) in the query string or in the request body to get the wished png",
             status_code=400
        )
