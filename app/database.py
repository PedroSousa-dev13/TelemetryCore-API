from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

def get_db():
    db=session_Local()
    try:
        yield db 
    finally:
        db.close()

DATABASE_URL = (
    "postgresql+psycopg2://postgres:postgres"
    "@localhost:5432/telemetrycore"
)


engine = create_engine(DATABASE_URL, echo=True)

session_Local=sessionmaker(autocommit=False,autoflush=False,bind=engine)

class Base(DeclarativeBase):
    pass