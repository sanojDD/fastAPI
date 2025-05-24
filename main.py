from fastapi import FastAPI, Path ,HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal
import json

app = FastAPI()


class Patient(BaseModel):

  id:Annotated[str, Field(...,description='ID of the patient', example='P001')]
  name:Annotated[str, Field(...,description='Name of the patient')]
  city:Annotated[str, Field(...,description='City where the patient is living')]
  age:Annotated[int, Field(..., gt=0, lt=120, description='Age of the patient')]
  gender:Annotated[Literal['Male','Female','Others'], Field(...,description='Gender of the patient')]
  height:Annotated[float, Field(...,gt=0, description='Height of the patient in meters')]
  weight:Annotated[float, Field(...,gt=0, description='Weight of the patient in kgs')]

  @computed_field
  @property
  def bmi(self) -> float:
    bmi = round(self.weight/(self.height ** 2),2)
    return bmi
  


  @computed_field
  @property
  def verdict(self) -> str:
    if self.bmi < 18.5:
      return 'Underweight'
    elif self.bmi <25 :
      return 'Normal'
    else:
      return 'Obese'



# helper function
def load_data():
  with open('patients.json','r') as f:
    data = json.load(f)
  return data

def save_data(data):
  with open('patients.json','w') as f:
    json.dump(data, f) #convert the dict into the json file


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

@app.get('/patient/{patient_id}')
def view_patient(patient_id:str = Path(...,description='ID of the patient in the DB', example='P001')):
  # load all the patient
  data = load_data()

  if patient_id in data:
    return data[patient_id]
  # return {'error: patient not found'}
  raise HTTPException(status_code=404, detail='patient not found...')


@app.get('/sort')
def sort_patients(sort_by:str = Query(..., description='sort on the basis of height, weight or the bmi'), order:str =Query('asc',description='sort in ascending and the descending order')):

  valid_fields = ['height', 'weight', 'bmi']

  if sort_by not in  valid_fields:
    raise HTTPException(status_code=400,detail= f'Invalid field select from {valid_fields}')
  
  if order not in ['asc', 'desc']:
    raise HTTPException(status_code=400, detail = 'invalid order select between asc and desc')
  

  data = load_data()


  sort_order = True if order =='desc' else False
  sorted_data = sorted(data.values(), key = lambda x:x.get(sort_by,0), reverse=sort_order)

  return sorted_data


@app.post('/create')
def create_patient(patient: Patient):


  # load the existing data
  data = load_data()

  # check if the patient already exist
  if patient.id in data:
    raise HTTPException(status_code=400, detail='patient already exist')

  # new patient add to the database
  data[patient.id] = patient.model_dump(exclude=['id'])
  
  # save into the json file
  save_data(data)

  return JSONResponse(status_code=201, content={'patient created successfully'})
