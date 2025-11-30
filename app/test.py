from sentence_transformers import SentenceTransformer
import llama_index
from dotenv import load_dotenv
import psycopg2

load_dotenv()

model = SentenceTransformer("all-MiniLM-L6-v2")
print("sentence transformer loaded")

try:
    conn = psycopg2.connect(
        dbname="vectordb",
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
        
    )
    print("Connected suffessfully")
    conn.close()
except Exception as e:
    print(f"Error connecting to database : {e}")