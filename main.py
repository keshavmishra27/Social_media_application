from hmac import new
import random
from typing import Optional
from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange

#making schema
class post(BaseModel):
    title:str
    content:str
    published:bool=False
    rating:Optional[int]=None
#name your app

app=FastAPI()

@app.get('/')# need for routing 
             #.get is the get method of http request 
            # / refers to website path
def root():
    return {'message':'Hello, this is my first fastAPI project'}#fastapi converts dict to json

my_post=[{"title":"title of post 1","content":"content of post 1","id":1},
         {"title":"title of post 2","content":"content of post 2","id":2}]

@app.get("/post")
def get_post():
    return {"data":my_post}

#integrate postman body with fastapi
#estract data from the body of the postman raw section
'''

@app.post("/createpost")
def create_post(new_post:dict=Body(...)):
    print(new_post)
    return{"data":f"name is {new_post['name']}"}
'''

@app.post("/post")
def create_post(new_post:post):
    post_dict=new_post.dict()
    post_dict['id']=randrange(0,1000000)
    my_post.append(post_dict)
    return{"data":post_dict}# will get a value error if  atleast oen part ios missing



