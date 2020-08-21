import logging
from pymongo import MongoClient
import azure.functions as func
import json
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    uri = os.getenv("MONGODB")
    mongodb = MongoClient(uri)
    apidb = mongodb["API"] 
    final_res = {}
    users = apidb.current.find({},{'_id':0,'name':1,'entry':1, 'discord-id' : 1, 'username' : 1})
    for user in users:
        tem = {
            'name' : user['name'],
            'discord-id' : user['discord-id'],
            'username' : user['username']
        }
        final_res[user['entry']] = tem
    return func.HttpResponse(json.dumps(final_res, sort_keys=True), mimetype="application/json")
