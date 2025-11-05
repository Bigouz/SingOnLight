import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio
import sqlite3

templates = Jinja2Templates(directory="templates/")
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get('/index.html')
def test(request:Request):
    #user = {'username': 'Cécile'}
    return templates.TemplateResponse("index.html",{"request":request})

@app.get("/play.html")
def hello(request:Request) -> str:
    return templates.TemplateResponse('play.html',{'request': request})

@app.get("/data.html")
def hello(request:Request) -> str:
    return templates.TemplateResponse('data.html',{'request': request})

@app.get("/about")
def hello(request:Request) -> str: 
    user = {'username': 'Cécile'}
    return templates.TemplateResponse('hello.html',{'request': request,'title':'First page', 'user':user})

if __name__ == "__main__":
    uvicorn.run(app) # lancement du serveur HTTP + WSGI avec les options de debug
