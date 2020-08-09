import logging
import os
import pytz
import requests
import azure.functions as func
from datetime import datetime


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        res_obj = req.get_json()
        answers = res_obj["form_response"]["answers"]
        name = answers[0]["text"]
        email = answers[1]["email"]
        text = answers[2]["text"]
        time_got = res_obj["form_response"]["submitted_at"]
        DISCORD_CONTACT = os.environ["DISCORD_CONTACT"]
    except:
        return func.HttpResponse(
             "Not Valid Json Or Key",
             status_code=400
        )
    else:
        time_obj = datetime.strptime(time_got, '%Y-%m-%dT%H:%M:%SZ')
        time_zone = pytz.timezone('Asia/Kolkata')
        time_fin = time_obj.replace(tzinfo=pytz.utc).astimezone(time_zone)
        time_show = str(time_fin)
        values = {
            "embeds": [
                {
                "title": "Contact Us Response",
                "description": f"Name : {name}\nEmail : {email}\nMessage : {text}",
                "footer": {
                    "text": f"Time : {time_show}"
                    }
                }, 
            ]
        }
        headers = {'Content-type': 'application/json'}
        r = requests.post(url = DISCORD_CONTACT, json=values, headers = headers)
        return func.HttpResponse(f"{r.status_code}")
    
