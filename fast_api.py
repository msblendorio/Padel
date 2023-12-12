from fastapi import FastAPI
from pydantic import BaseModel

class User_input(BaseModel):
    giorni: str
    ora: str
    callback: str

app = FastAPI()

@app.post("/disponibilita")
def operate(input:User_input):

    return 'Registrazione avvenuta con successo.'
