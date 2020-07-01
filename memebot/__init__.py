import logging
import azure.functions as func
import requests
import praw
import random
import os
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        req_body  =req.get_json()
        webhook = req_body['webhook']
        con = True
    except:
        con = False
    reddit = praw.Reddit(client_id='xUYUZsnXrX-npw',
        client_secret=os.environ['reddit'],
        user_agent='disocrd-meme-bot')
    memes_submissions = reddit.subreddit('ProgrammerHumor').new(limit = 10)
    post_to_pick = random.randint(0, 9)
    for i in range(0, 10):
        submission = next(x for x in memes_submissions if not x.stickied)
        if(i == post_to_pick):
            break
    img = submission.url
    title = submission.title
    if(con):
        headers = {'Content-type': 'application/json'}
        values = {'content' : img}
        r = requests.post(url = webhook, json=values, headers = headers)
        out = title + "\n"
        values = {'content' : out}
        r = requests.post(url = webhook, json=values, headers = headers)
    resp = {
        "image" : img,
        "title" : title
    }
    return func.HttpResponse(json.dumps(resp), mimetype="application/json")
