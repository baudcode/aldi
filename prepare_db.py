from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from aldi import populate_categories
import tqdm
import models

engine = create_engine(f"sqlite:///database.sqlite")
session_maker = sessionmaker(bind=engine, autocommit=False, autoflush=True)
session = session_maker()

models.Base.metadata.create_all(bind=engine)
populate_categories(session)
