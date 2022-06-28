from typing import Union
from fastapi import FastAPI, Request
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import subprocess, os
import configparser
CONFIG_FILE = 'config.ini'
config = configparser.ConfigParser()
config.read(CONFIG_FILE)
main = config['main']
host, looker = main['HOST'],main['LOOKER']
frontend_port = main['FRONTENDPORT']
backend_port = main['BACKENDPORT']

app = FastAPI()
from auth import generateUrlLocally, urlFromLookerAPI

origins = [
    "*",
   f"{host}:{frontend_port}",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/auth")
def auth_from_local_url(request: Request,src:str=""):
    userToken = request.headers.get('usertoken')
    return {"url":generateUrlLocally(src, userToken)}


@app.get('/auth2')
def auth_from_api(request: Request,src:str=""):
    userToken = request.headers.get('usertoken')
    return urlFromLookerAPI(src, userToken)


if __name__ == '__main__':
    #checks if npm install has been run, runs if not
    if not os.path.exists('frontend/node_modules'):
        subprocess.run('cd frontend; npm install',shell=True)
    my_env = os.environ.copy()
    my_env["HOST"], my_env["LOOKER"], my_env["BACKENDPORT"], my_env["PORT"]  = host, looker, backend_port, frontend_port
    #start the frontend server with environment variables
    subprocess.Popen("cd frontend; npm start", env=my_env, shell=True)
    #start the backend server
    uvicorn.run(
        'main:app', port=int(backend_port), host='0.0.0.0',
        reload=True,
        ssl_keyfile='ssl/cert.key',
        ssl_certfile='ssl/cert.pem')