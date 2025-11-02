
from fastapi import FastAPI
# Will switch to APIRouter() before integrating into the main backend

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Welcome to Flight Crew sAPI"}


@app.get("/pilots")
def get_all_pilots():
    return pilots

@app.get("/pilots/{pilot_id}")
def get_pilot(pilot_id: int):
    for pilot in pilots:
        if pilot["id"] == pilot_id:
            return pilot
    return {"error": "Pilot not found"}

