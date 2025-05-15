from fastapi import FastAPI

app = FastAPI()
import json

def load_data():
  with open('patients.json','r') as f:
    data = json.load(f)
  return data


@app.get('/')
def hello():
  return {'message':'patient management system'}

@app.get('/about')
def about():
  return{'message':'fully functional api to manage your patient records'}

@app.get('/view')
def view():
  data = load_data()

  return data