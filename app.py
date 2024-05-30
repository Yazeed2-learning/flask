import os 
from dotenv import load_dotenv
from flask import Flask, request
import psycopg2
from datetime import datetime

app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)

CREATE_ROOMS_TABLE = ("CREATE TABLE IF NOT EXISTS rooms (id SERIAL PRIMARY KEY, name TEXT);")
INSERT_ROOM_RETURN_ID = "INSERT INTO rooms (name) VALUES (%s) RETURNING id;"
CREATE_TEMPS_TABLE = ("CREATE TABLE IF NOT EXISTS temps (room_id INTEGER, temperature REAL, date TIMESTAMP, FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE);")
INSERT_TEMP = "INSERT INTO temps (room_id, temperature, date ) VALUES (%s, %s, %s);"
GLOBAL_AVG = "SELECT AVG(temperature) as average FROM temps"
GLOBAL_NUMBER_DAYS =("SELECT COUNT (DISTINCT DATE(date)) AS days FROM temps;")


@app.post('/api/rooms')
def create_room(): 
    data = request.get_json()
    name = data["name"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_ROOMS_TABLE)
            cursor.execute(INSERT_ROOM_RETURN_ID, (name,))
            room_id = cursor.fetchone()[0]

    return {"id": room_id, "message":f"Room {name} created"}, 201

@app.post('/api/temp')
def add_temp(): 
    data = request.get_json()
    temp = data["temp"]
    room_id = data["room"]
    try:
        date = datetime.strptime(data["date"], "%m-%d-%Y %H:%M:%S")
    except KeyError: 
        date = datetime.now()
    with connection:
        with connection.cursor() as cursor: 
            cursor.execute(CREATE_TEMPS_TABLE)
            cursor.execute(INSERT_TEMP, (room_id, temp, date))
    return {"message": "temperature added ;) "}, 201 

@app.get('/api/avg')
def get_avg():
    with connection:
        with connection.cursor() as cursor: 
            cursor.execute(GLOBAL_AVG)
            average = cursor.fetchone()[0]
            cursor.execute(GLOBAL_NUMBER_DAYS)
            days = cursor.fetchone()[0]
    return {"average": round(average, 2), "days": days}
