from hmac import new
import random
from telnetlib import STATUS
from typing import Optional
from fastapi import FastAPI,Response,status,HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange

#making schema
class post(BaseModel):
    title:str
    content:str
    published:bool=False
    rating:Optional[int]=None
    #no need of geberating id here as it will be generated in the create post function
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

@app.post("/create_post",status_code=status.HTTP_201_CREATED)
def create_post(new_post:post):
    post_dict=new_post.dict()
    post_dict['id']=randrange(0,1000000)
    my_post.append(post_dict)
    return{"data":post_dict}# will get a value error if  atleast oen part ios missing

#brutforce method for getting sp[ecific post

def find_post(id):
    for p in my_post:
        if p["id"]==id:
            return p
        


@app.get("/post/{id}")
def get_post_specific(id:int,response:Response):#validation check for id to be an integer
    print(id)
    post = find_post(id)#alternate method=> in basemodel id type is int and here in request id type is str so we need to convert
    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"invalid id  try again later")#it is of fastapi
        '''
        alternate method
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"alert!":f"post with id {id} not found"}
        '''
    return {"post detail": post}


#get latest post
@app.get("/latest_post")
def get_latest_post():
    latest_post=my_post[len(my_post)-1]
    return{"latest post":latest_post}