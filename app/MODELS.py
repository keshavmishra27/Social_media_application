from .database import base
from sqlalchemy import Column,Integer,String,Boolean
from sqlalchemy.sql.expression import null,text
from sqlalchemy.sql.sqltypes import TIMESTAMP

class post(base):
    #specify table name
    __tablename__="posts"

    #cretae collumns
    id=Column(Integer,primary_key=True,nullable=False)
    title=Column(String,nullable=False)#by default primary key=false
    content=Column(String,nullable=False)
    published=Column(Boolean,server_default='TRUE')#by default nullable=True
                                                   #serber_default will set constraint=true by default
    #will add time span collumn later
    created_at=Column(TIMESTAMP(timezone=True),nullable=False,server_default=text('now()'))

#uusing this  will create a new table if not esists,it will not modify table, 
# for modifying u need alembic sqlalchemy 






