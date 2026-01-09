from hmac import new
import random
from telnetlib import STATUS
from typing import Optional
from fastapi import FastAPI,Response,status,HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
from time import sleep

#making schema
class post(BaseModel):
    title:str
    content:str
    published:bool=False
    rating:Optional[int]=None
    #no need of geberating id here as it will be generated in the create post function
#name your app

app=FastAPI()

#connecting our database
while True:
    try:
        conn=psycopg2.connect(host='localhost',database='social_media_fastapi'
                              ,user='postgres',password='kshu086',
                              cursor_factory=RealDictCursor)
        cursor=conn.cursor()
        print("database connection was successful")
        break
    except Exception as error:
        print("connection to database failed")
        print("error:",error)
        sleep(3)

@app.get('/')# need for routing 
             #.get is the get method of http request 
            # / refers to website path
def root():
    return {'message':'Hello, this is my first fastAPI project'}#fastapi converts dict to json

my_post=[{"title":"title of post 1","content":"content of post 1","id":1},
         {"title":"title of post 2","content":"content of post 2","id":2}]

@app.get("/post")
def get_post():
    cursor.execute("""SELECT *from posts """)
    posts=cursor.fetchall()
    return {"data":posts}

#integrate postman body with fastapi
#estract data from the body of the postman raw section
'''

@app.post("/createpost")
def create_post(new_post:dict=Body(...)):
    print(new_post)
    return{"data":f"name is {new_post['name']}"}
'''

@app.post("/create_post",status_code=status.HTTP_201_CREATED)
def create_post(post:post):
    cursor.execute(""" INSERT INTO posts (title,content,published)
                    VALUES(%s,%s,%s) RETURNING * """,(post.title,
                                                      post.content
                                                      ,post.published))
    created_post=cursor.fetchone()
    conn.commit()
    return{"data":created_post}# will get a value error if  atleast oen part ios missing

#brutforce method for getting sp[ecific post

def find_post(id):
    for p in my_post:
        if p["id"]==id:
            return p
        


@app.get("/post/{id}")
def get_post_specific(id:int,response:Response):#validation check for id to be an integer

    cursor.execute(""" SELECT id from posts""")
    all_id=cursor.fetchall()
    id_list=[]
    for ids in all_id:
        id_list.append(ids['id'])

    if id in id_list:
        cursor.execute(""" SELECT * from posts WHERE id=%s """,(str(id),))
        post=cursor.fetchone()
        return{"post details":post}
    
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found")

    # print(id)
    # post = find_post(id)#alternate method=> in basemodel id type is int and here in request id type is str so we need to convert
    # print(post)
    # if not post:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail=f"invalid id  try again later")#it is of fastapi
    #     '''
    #     alternate method
    #     response.status_code=status.HTTP_404_NOT_FOUND
    #     return {"alert!":f"post with id {id} not found"}

#get latest post
@app.get("/latest_post")
def get_latest_post():
    latest_post=my_post[len(my_post)-1]
    return{"latest post":latest_post}

def find_indes(id):
    for i,p in enumerate(my_post):
        if p['id']==id:
            return i

#delete a post
@app.delete("/delete_post/{id}")
def delete_post(id:int):
    #logic for deleting post
    #step1=> find teh ides in the list having required id:
    #step=?my_post.pop(indes)
    cursor.execute(""" DELETE FROM posts WHERE id=%s RETURNING * """,(str(id),))
    deleted_post=cursor.fetchone()
    conn.commit()
    if deleted_post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found") 
    return {"message":f"post with id {id} deleted successfully"}

    
@app.put("/update_post/{id}")#user sends request to update a post
def update(id: int,post:post):
    #indes=find_indes(id)#indes of the post will be checked in my_post
    cursor.execute(""" UPDATE posts SET title=%s, content=%s,
                    published=%s WHERE id=%s RETURNING * """,
                   (post.title,post.content,post.published,str(id)))
    updated_post=cursor.fetchone()
    conn.commit()
    if updated_post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found")

    # post_dict=post.dict()#store the updated data in the form of dictionary
    # post_dict['id']=id
    # my_post[indes]=post_dict

    return {"data":updated_post}
