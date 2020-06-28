import logging
import azure.functions as func
import requests
import time
from collections import deque 

def check(tk, tch):
    if(tk[:len(tch)] == tch):
        return True
    return False

def specifictxt(prob, ser):
    url = "https://brilliant.org/daily-problems/"
    url = url + prob
    x = requests.get(url)
    tex = ""
    res = x.text
    fin = res.find(ser)
    res = res[fin:].strip()
    return res

def parse(txt):
    synt = False
    syntaxes = []
    tex = ""
    for i in txt:
        if(i == "\n"):
            continue
        if(i == "<"):
            synt = True
            if(len(tex.strip()) > 0):
                tem = ('text',tex)
                syntaxes.append(tem)
            tex = "<"
        elif( i == ">"):
            synt = False
            if(tex[1] == '/'):
                type_syn = tex.split(" ")[0][2:]
                op_t = "syn_cl"
            else:
                type_syn = tex.split(" ")[0][1:]
                op_t = "syn_op"
            tex = tex + ">"
            tem = (op_t,type_syn,tex)
            syntaxes.append(tem)
            tex = ""
        else:
            tex = tex + i
    return syntaxes
def finques(syntaxes):
    ques = ""
    ignore = False
    con = False
    inmid = 0
    for i in syntaxes:
        if(ignore):
            if(i[:11] == "<annotation"):
                con = True
            elif(con):
                if(i == "</annotation>" ):
                    con = False
                else:
                    ques = ques + i 
                con = False
            elif(i[:5] == "<span"):
                inmid += 1
            elif(i == "</span>"):
                inmid -= 1
                if(inmid == -1):
                    ignore = False
        elif(i[:5] == "<span"):
            if(check(i)):
                ignore = True
                inmid = 0
        elif(i[0] != "<"):
            ques = ques + i 
        elif(i == "</p>"):
            ques = ques + "\n"
    return ques
def updat(syntaxes):
    inmid = 0
    stack = deque()
    le = 0
    for i in syntaxes:
        le += 1
        if(i[0] == 'text'):
            continue
        if(i[0] == 'syn_op'):
            tem = (i[0], i[1])
            stack.append(tem)
        elif(i[0] == 'syn_cl'):
            while(stack.pop()[1] != i[1]):
                continue
        if(len(stack) == 0):
            break
    syntaxes = syntaxes[:le]
    return syntaxes

def extract(syntaxes):
    infos = []
    ignore = False
    start = False
    con = False
    tem_stack = deque()
    tex = ""
    for i in syntaxes:
        if(ignore):
            if(i[0] == 'syn_op'):
                if(i[1] == "annotation"):
                    con = True
                tem_stack.append(i[1])
            elif(con and i[0] == 'text'):
                tex = tex + i[1]
            elif(i[0] == 'syn_cl'):
                if(i[1] == "annotation"):
                    con = False
                while(tem_stack.pop() != i[1]):
                    continue  
                if(len(tem_stack) == 0):
                    ignore = False
        elif(i[0] == 'syn_op' and i[1] == 'p'):
            tex = ''
        elif(i[0] == 'syn_op' and i[1] == 'input'):
            tex = tex.strip()
            if(len(tex) > 0):
                infos.append(tex)
            tex = ""
        elif(i[0] == 'syn_cl' and i[1] == 'p'):
            tex = tex.strip()
            if(len(tex) > 0):
                infos.append(tex)
            tex = ""
        elif(i[0] == 'syn_op' and i[1] == 'span' and i[2] == '<span class="katex">' ):
            tem_stack.append('span')
            ignore = True
        elif(i[0] == 'syn_op' and (i[1] == 'ol' or i[1] == 'ul')):
            start = True
        elif(i[0] == 'syn_cl' and (i[1] == 'ol' or i[1] == 'ul')):
            tex = tex.strip()
            if(len(tex) > 0):
                infos.append(tex)
            start = False
        elif(i[0] == 'syn_op' and i[1] == 'li'):
            tex = tex + "\n" + "# "
        elif(i[0] == 'syn_op'):
            media = ""
            if(check(i[2] , '<div class="video-container"')):
                fin = i[2].find('data-assets=')
                temu = i[2][fin:].strip()[:-1]
                temu = temu.split(',')
                for i in temu:
                    tk = i.strip()
                    if(tk[:8] == '"url": "'):
                        media = tk[8:-2]
                        break
            elif(i[1] == 'img'):
                temu = i[2].split()
                media = temu[1][5:-1]
            if(len(media) > 0):
                tex = tex.strip()
                if(len(tex) > 0):
                    infos.append(tex)
                tex = ""
                infos.append(media)
        elif(i[0] == 'text'):
            tex = tex + i[1]
    if(len(tex.strip()) > 0):
        infos.append(tex.strip())
    return infos

def findques():
    url = "https://brilliant.org/daily-problems/"
    x = requests.get(url)
    res = x.text
    ser = '<div class="nf-feed-item">'
    fin = res.find(ser)
    res = res[fin:]
    ser = 'href="/daily-problems/'
    fin = res.find(ser)
    start = fin + len(ser)
    i = start
    while(res[i] != '"'):
        i += 1
    ques = res[start:i]
    return ques

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    req_body = req.get_json()
    try:
        webhook = req_body['webhook']
    except:
        return func.HttpResponse(
             "Invalid Call",
             status_code=400
        )
    try:
        ques = req_body['ques']
    except:
        ques = findques()
    res = specifictxt(ques, '<div class="question-text latex">')
    if(res.strip() == ""):
        return func.HttpResponse(
            "Invalid Question",
            status_code=404
        )
    syntaxes = parse(res)
    syntaxes = updat(syntaxes)
    information = extract(syntaxes)
    headers = {'Content-type': 'application/json'}
    values = {'content' : "Today`s Challenge"}
    r = requests.post(url = webhook, json=values, headers = headers)
    for i in range(len(information)-1):
        values = {'content' : information[i]}
        r = requests.post(url = webhook, json=values, headers = headers)
        logging.info(r.status_code)
        time.sleep(0.25)
        
    options_txt = specifictxt(ques, '<div class="dp-solv-details solv-details clearfix mcq logged-out">')
    op_syn = parse(options_txt)
    op_syn = updat(op_syn)
    options = extract(op_syn)
    out = "Options Are - \n"
    for i in range(len(options) - 1):
        out = out +"\t# " +options[i] + "\n"
    values = {'content' : out}
    r = requests.post(url = webhook, json=values, headers = headers)
    return func.HttpResponse(f"{out}")
