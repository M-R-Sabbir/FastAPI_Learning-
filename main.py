from fastapi import FastAPI,Path,HTTPException,Query
import json

app = FastAPI()           # fastapi object

def data_loader():
    with open ('patients.json','r') as f:
        data = json.load(f)
    return data


@app.get("/")             # creates a route using decorator (/ : home route)
                        # this is an endpoint
def hello():               
    return {"message":"Patients management system api"}

@app.get('/about')          # 2nd end point
def about():
    return {"message":"API to manage patient records"}

@app.get('/patients')
def view():
    data = data_loader()
    return data


# Path Parameter
@app.get('/patients/{patients_id}')
def view_patient(patients_id: str = Path(...,description="ID of the patient in the DB", example="P002",max_length=4)):
    data = data_loader()

    if patients_id in data:
        return data[patients_id]
    # return {"error":"patient not found"}        # but if user do it he should get 404
                                                # cause data don't exist
    raise HTTPException(status_code=404,detail="Patient not found")



# Query Parameter
@app.get('/sort')
def sort_patients(sort_by:str = Query(..., description="Sort on the basis of hight/weight/BMI"),
                  order:str= Query('asc',description='sort in asc/desc order')):
    valid_fields = ["heights","weights","bmi"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,detail=f'Invalid field choose from {valid_fields}')

    if order not in ['asc',"desc"]:
        raise HTTPException(status_code=400, detail="Invalid order select asc or desc")

    data = data_loader()
    sort_order = True if order=='desc' else False
    sorted_data = sorted(data.values(),key=lambda x : x.get(sort_by,0),reverse=sort_order)
    return sorted_data

