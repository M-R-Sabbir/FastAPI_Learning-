import json
with open ('patients.json','r') as f:
        data = json.load(f)
print(data.values())


# sorted_data = sorted(data.values(),key=lambda x : x.get(sort_by,0),reverse=sort_order)
