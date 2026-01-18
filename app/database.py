#NOTE: better option over sqlAlchemy is sqlModel

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

database_url='postgresql://postgres:kshu086@localhost/social_media_fastapi'
#disadvantage:harcode values can be seen by others on github while seeing you code

#cretaing engine
engine=create_engine(database_url)

sessionlocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

#create base
base=declarative_base()

#get connection or session for database(getting dependencies)
def get_db():
    db=sessionlocal()
    try:
        yield db
    finally:
        db.close()

