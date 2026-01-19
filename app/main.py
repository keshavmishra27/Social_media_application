from http.client import responses
from multiprocessing.sharedctypes import synchronized
import random
from typing import Optional
from urllib import response
from fastapi import FastAPI,Response,status,HTTPException,Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
from time import sleep
# will be using session from sqlalchemey
from sqlalchemy.orm import Session
from .MODELS import post
from Social_media_application.app import database

#making schema
class post(BaseModel):
    title:str
    content:str
    published:bool=False
    #no need of geberating id here as it will be generated in the create post function


#connect your db model
from . import MODELS #. refers to current directory
from .database import engine,get_db

database.base.metadata.create_all(bind=engine)

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

# my_post=[{"title":"title of post 1","content":"content of post 1","id":1},
#          {"title":"title of post 2","content":"content of post 2","id":2}]

@app.get("/sqlalchemy")
def  test_posts(db:Session=Depends(get_db)):
    # queryofpost=db.query(MODELS.post)
    # print(queryofpost)
    posts=db.query(MODELS.post).all()
    return{"data":posts}



@app.get("/post")
def get_post(db:Session=Depends(get_db)):
    # cursor.execute("""SELECT *from posts """)
    # posts=cursor.fetchall()
    #optimized method by using orm below
    posts=db.query(MODELS.post).all()
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
def create_post(id:int,post:post,db:Session=Depends(get_db)):
    # cursor.execute(""" INSERT INTO posts (title,content,published)
    #                 VALUES(%s,%s,%s) RETURNING * """,(post.title,
    #                                                   post.content
    #                                                   ,post.published))
    # created_post=cursor.fetchone()
    # conn.commit()
    #long way
    #created_post=MODELS.post(title=post.title,content=post.content,published=post.published)
    #alternate short optimized way
    #print(**post.dict())
    created_post=MODELS.post(**post.dict())#unpacking dictionary using ** {used for pydantic classes}
    #add and commit to the database
    db.add(created_post)
    db.commit()
    db.refresh(created_post)#to get the created post back with id
    return{"data":created_post}# will get a value error if  atleast oen part ios missing

#brutforce method for getting sp[ecific post

# def find_post(id):
#     for p in my_post:
#         if p["id"]==id:
#             return p
        


@app.get("/post/{id}")
def get_post_specific(id:int,db:Session=Depends(get_db)):#validation check for id to be an integer
    """
    NOTE 
    FastAPI sees db: Session = get_db and assumes:

“Oh, Session is a request/response field that needs Pydantic validation.”

But sqlalchemy.orm.session.Session:

❌ is not a Pydantic type

❌ is not JSON serializable

❌ should NEVER be treated as request/response data
    """

    # cursor.execute(""" SELECT id from posts""")
    # all_id=cursor.fetchall()
    # id_list=[]
    # for ids in all_id:
    #     id_list.append(ids['id'])

    # if id in id_list:
    #     cursor.execute(""" SELECT * from posts WHERE id=%s """,(str(id),))
    #     post=cursor.fetchone()

    post=db.query(MODELS.post).filter(MODELS.post.id==id).first() #.first to get only one post
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found")
    
    return{"post details":post}

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
# @app.get("/latest_post")
# def get_latest_post():
    #latest_post=my_post[len(my_post)-1]
    #return{"latest post":latest_post}

# def find_indes(id):
#     for i,p in enumerate(my_post):
#         if p['id']==id:
#             return i

#delete a post
@app.delete("/delete_post/{id}")
def delete_post(id:int,post:post,db:Session=Depends(get_db)):
    #logic for deleting post
    #step1=> find teh ides in the list having required id:
    #step=?my_post.pop(indes)
    # cursor.execute(""" DELETE FROM posts WHERE id=%s RETURNING * """,(str(id),))
    # deleted_post=cursor.fetchone()
    # conn.commit()

    deleted_post=db.query(MODELS.post).filter(MODELS.post.id==id)
    if deleted_post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found") 
    else:
        deleted_post.delete(synchronize_session=False)

        db.commit()
    return {"message":f"post with id {id} deleted successfully"}

    
@app.put("/update_post/{id}")#user sends request to update a post
def update(id: int, post:post,db:Session=Depends(get_db)):
    #indes=find_indes(id)#indes of the post will be checked in my_post
    # cursor.execute(""" UPDATE posts SET title=%s, content=%s,
    #                 published=%s WHERE id=%s RETURNING * """,
    #                (post.title,post.content,post.published,str(id)))
    # updated_post=cursor.fetchone()
    # conn.commit()
    updated_post=db.query(MODELS.post).filter(MODELS.post.id==id)
    posted=updated_post.first()
    if posted==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found")
    
    else:
 
        updated_post.update(post.dict(),synchronize_session=False)
        db.commit()

    # post_dict=post.dict()#store the updated data in the form of dictionary
    # post_dict['id']=id
    # my_post[indes]=post_dict

    return {"data":updated_post.first()}# if written update_post reccursion errror will occur

