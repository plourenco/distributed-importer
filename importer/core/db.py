from sqlalchemy import create_engine

from importer.models import Base

engine = create_engine('sqlite:///test.db')
Base.metadata.create_all(engine)
