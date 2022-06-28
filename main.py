from typing import Union
from fastapi import FastAPI, Request
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
from auth import generateUrlLocally, urlFromLookerAPI

origins = [
    "*",
    "embed.demo.com:8000",
    "embed.demo.com:3000",
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
    uvicorn.run(
        'main:app', port=8000, host='0.0.0.0',
        reload=True,
        ssl_keyfile='ssl/cert.key',
        ssl_certfile='ssl/cert.pem')