from fastapi import FastAPI,Path,Query,HTTPException
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Literal,Optional
import json
from fastapi.responses import JSONResponse

def load_data():
    with open("patients.json") as f:
        data = json.load(f)
        return data
    
app = FastAPI()


# first route or endpoint
@app.get('/')
def welcome():
    return "welcome to the world of fastapi"


#we wanna get the whole data from the server
@app.get('/view')
def patients():
    data = load_data()
    return data


"""
we want some specific data.      : Path Parameter

@app.get("/patient/{patients_id}")
def patient(patients_id):
    data = load_data()
    if patients_id in data:
        return data[patients_id]"""

# path() function. 
"""Path() function provide meta data:[title,description,example], 
    validation rule:[gt,lt,ge,le,max_length,min_length]: documentation for path"""

@app.get("/patient/{patients_id}")
def patient(patients_id : str= Path(...,description="Provide Patient's ID",example="P001")):
    data = load_data()
    if patients_id in data:
        return data[patients_id]
    raise HTTPException(status_code=401,detail="Patient not found")


# Query Parameter
"""Query Parameter are optional key-value parameters, passed through url after ? symbol.
                    used for sorting,searching,filtering | optional key this is why we don't pass it in the route, pass it in the function"""



@app.get('/sort')
def sorted_data(sort_by:str=Query(...,description="By which key you wanna sort?",example="bmi/height/weight"),
                order:str=Query(default="asc",description="In which order you wanna sort?",example="asc,desc")):
    valid_fields = ["bmi",'height','weight']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,detail=f"Bad request select from {valid_fields}")
    if order not in ["asc","desc"]:
        raise HTTPException(status_code=400,detail="Bad request select")

    data = load_data()

    sorted_data = sorted(data.values(),key=lambda x : x.get(sort_by,0),reverse=True if order=="desc" else False)   # key is a function which shows all values ,which it will sort, and based on the sorted numbers ,sort the dict
    return sorted_data





#Post


class Patient(BaseModel):
    id:Annotated[str,Field(..., description="ID of the Patient",examples=["P002"])]
    name:Annotated[str,Field(...,description="Name of the Patient")]
    city:Annotated[str,Field(...,description="Patients city")]
    age: Annotated[int,Field(...,gt=0,le=100)]
    gender:Annotated[Literal["male","female"],Field(...,description="Gender of the patients")]
    height:Annotated[float,Field(...,gt=0,description="Height of the patients(Miters)")]
    weight:Annotated[float,Field(...,gt=0,description="Weight of the patients(KG)")] 


    @computed_field
    @property
    def bmi(self)->float:
        bmi = round(self.weight/(self.height*self.height),2)
        return bmi

    @computed_field
    @property
    def verdict(self)->str:
        if self.bmi<18.5:
            return "Underweight"
        elif self.bmi<25: 
            return "Normal"
        elif self.bmi<30:
            return "fat"
        else:
            return "Obese"


class Patient_update(BaseModel):
    name: Annotated[Optional[str],Field(default=None)]
    city: Annotated[Optional[str],Field(default=None)]
    age : Annotated[Optional[int],Field(default=None,gt=0)]
    gender :Annotated[Optional[Literal["Male","Female"]],Field(default=None)]
    height: Annotated[Optional[float],Field(default=None,gt=0)]
    weight: Annotated[Optional[float],Field(default=None,gt=0)]



def save_data(data):
    with open ("patients.json","w") as f:
        json.dump(data,f)



@app.post("/create")
def create_patient(patient:Patient):

    # load data,and check this data already exists?
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code=400,detail="patient is already in database")

    # new patient so,add it with existing data
    data[patient.id]=patient.model_dump(exclude=["id"])

    #data is added to the loaded data, but we have to save into the json
    save_data(data)

    return JSONResponse(status_code=201,content={"message":"Patient created Successfully"})


# PUT

##########################
@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: Patient_update):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    existing_patient_info = data[patient_id]

    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value

# # bmi and verdict is not calculated,so convert existing patient info into pydantic obj,then computed_fields will be computed automatically
# # then convert into a dict then into data and put it into that json file

    #existing_patient_info -> pydantic object -> updated bmi + verdict
    existing_patient_info['id'] = patient_id
    patient_pydandic_obj = Patient(**existing_patient_info)
    #-> pydantic object -> dict
    existing_patient_info = patient_pydandic_obj.model_dump(exclude='id')

    # add this dict to data
    data[patient_id] = existing_patient_info

    # save data
    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient updated'})

###########################
# delete


@app.delete("/delete/{patient_id}")
def delete_patient(patient_id:str):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404,detail="patient not found")
    del data[patient_id]
    save_data(data)

    return JSONResponse(status_code=200,content="Patient Deleted")
