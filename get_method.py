from fastapi import FastAPI,HTTPException,Path,Query
import json


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
                    used for sorting,searching,filtering """

@app.get("/sort")
@app.get('/sort')
def sorted_data(sort_by:str=Query(...,description="By which key you wanna sort?",example="bmi/height/weight"),
                order:str=Query(default="asc",description="In which order you wanna sort?",example="asc,desc")):
    valid_fields = ["bmi",'height','weight']
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,detail=f"Bad request select from {valid_fields}")
    if order not in ["asc","desc"]:
        raise HTTPException(status_code=400,detail="Bad request select")

    data = load_data()

    sorted_data = sorted(data.values(),key=lambda x : x.get(sort_by,0),reverse=True if order=="desc" else False)
    return sorted_data

