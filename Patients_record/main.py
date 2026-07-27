import json
import os
from pathlib import Path
from threading import RLock
from typing import Annotated, Literal, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field

app = FastAPI()
DATA_FILE = Path(os.getenv("PATIENTS_FILE", Path(__file__).with_name("patients.json")))
DATA_LOCK = RLock()

class Patient(BaseModel):
    
    id: Annotated[str, Field(...,description ='Id of patient',example='P001')]
    name: Annotated[str, Field(...,description ='Name of patient',example='Shraddhan')]
    city: Annotated[str, Field(...,description ='City of patient',example='Ahmedabad')]
    age: Annotated[int, Field(...,description ='Age of patient, greater than 0', gt=0, lt=120)]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='Gender of the patient')]
    height: Annotated[float, Field(..., gt=0, description='Height of the patient in mtrs')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the patient in kgs')]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)
    
    @computed_field
    @property
    def verdict(self) -> str:

        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'


class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0, lt=120)]
    gender: Annotated[Optional[Literal['male', 'female', 'others']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]

def load_data():
    with DATA_LOCK:
        with DATA_FILE.open('r', encoding='utf-8') as file:
            return json.load(file)

def save_data(data):
    temporary_file = DATA_FILE.with_suffix(f'{DATA_FILE.suffix}.tmp')

    with DATA_LOCK:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with temporary_file.open('w', encoding='utf-8') as file:
            json.dump(data, file, indent=2)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary_file, DATA_FILE)

@app.get("/")
def hello():
    return{'message': 'Patient Management API'}  

@app.get("/about")
def about():
    return{'about me' : 'You can view patients using /view'}

@app.get("/view")
def views():
    data = load_data()
    return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id : str):
    data = load_data()
    if patient_id in data :
        return data[patient_id]
    raise HTTPException(status_code = 404 , detail = "Patient not found")

@app.get("/sort")
def sort_patients(sort_by: str = Query(..., description="Sort by height weight & bmi"), order :str = Query('asc', description ="sort in order" )):
    valid_fields = ['height','weight','bmi']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort. Select from {valid_fields}")
    
    if order not in ["asc","desc"]:
        raise HTTPException(status_code=400 , detail = "Invalid Order")

    data = load_data()

    sort_order = True if order == 'desc' else False

    sort_data = sorted(data.values(), key = lambda x: x.get(sort_by, 0), reverse = sort_order)
    return sort_data

@app.post("/create", status_code=201)
def create_patient(patient: Patient):
    with DATA_LOCK:
        data = load_data()

        if patient.id in data:
            raise HTTPException(
                status_code=409,
                detail="Patient already exists"
            )

        data[patient.id] = patient.model_dump(exclude={"id"})
        save_data(data)

    return {
        "message": "Patient created successfully",
        "patient_id": patient.id
    }


@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):
    with DATA_LOCK:
        data = load_data()

        if patient_id not in data:
            raise HTTPException(status_code=404, detail='Patient not found')

        existing_patient_info = data[patient_id]
        updated_patient_info = patient_update.model_dump(exclude_unset=True)
        existing_patient_info.update(updated_patient_info)
        existing_patient_info['id'] = patient_id

        patient_pydantic_obj = Patient(**existing_patient_info)
        data[patient_id] = patient_pydantic_obj.model_dump(exclude={'id'})
        save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient updated'})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):
    with DATA_LOCK:
        data = load_data()

        if patient_id not in data:
            raise HTTPException(status_code=404, detail='Patient not found')

        del data[patient_id]
        save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient deleted'})
