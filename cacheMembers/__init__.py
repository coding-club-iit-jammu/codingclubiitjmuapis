import logging
from pymongo import MongoClient
import azure.functions as func
import json
import requests
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContentSettings, ContainerClient, __version__

connect_str = os.getenv('STORAGE')
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_name = "codingclub"

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    uri = os.getenv("MONGODB")
    mongodb = MongoClient(uri)
    db = mongodb["CodingClub"] 
    final_res = {}
    users = db.member.find({},{'_id':0,'name':1,'entry':1, 'discordid' : 1, 'rating':1})
    dbMap = {}
    for user in users:
        dbMap[user['discordid']] = {
            'name' : user['name'],
            'entry' : user['entry'],
            'rating' : user['rating']
        }
    Token = os.getenv("BOT_TOKEN")
    headers = {"Authorization" : f"Bot {Token}"}
    guildMember = requests.get('https://discordapp.com/api/guilds/664156473944834079/members?limit=500', headers = headers)
    dic = []
    Verified = '740429875046776953'
    Alumni = '779048768145457173'
    for i in guildMember.json():
        if('bot' in i['user'] and i['user']['bot']):
            continue
        if(Verified in i['roles'] and Alumni not in i['roles']):
            did = i['user']['id']
            if(i['user']['avatar'] == None):
                vk = int(i['user']['discriminator'])%5
                img_link = f"https://cdn.discordapp.com/embed/avatars/{vk}.png"
            else:
                img_link = f"https://cdn.discordapp.com/avatars/{did}/{i['user']['avatar']}.png"
            tem = {
                'name' : dbMap[did]['name'],
                'entry': dbMap[did]['entry'],
                'discordid' : did,
                'image': img_link,
                'username' : f"{i['user']['username']}#{i['user']['discriminator']}",
                'rating' : dbMap[did].get('rating',0)
            }
            dic.append(tem)
    dic.sort(key = lambda x: x['entry'])
    out = {}
    ind = 1
    for i in dic:
        out[ind] = i
        ind += 1
    out_tex = json.dumps(out, sort_keys=True)
    my_content_settings = ContentSettings(content_type='application/json')
    blob_client = blob_service_client.get_blob_client(container=container_name, blob="memberlist.json")
    blob_client.upload_blob(out_tex, overwrite=True, content_settings=my_content_settings)
    return func.HttpResponse('{"message" : "refreshed successfully "}', mimetype="application/json")