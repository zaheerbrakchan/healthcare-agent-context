from sqlalchemy import create_engine, text

from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()  # by default, it looks for .env in the same folder


USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Construct the SQLAlchemy connection string
DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

print("DATABASE_URL : ",DATABASE_URL)
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT NOW();"))
        print("DB Connected! Current time:", result.fetchone()[0])
except Exception as e:
    print("DB connection failed:", e)
