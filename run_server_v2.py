from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sqlite3
from fastapi.responses import JSONResponse

import requests

from utils.preocess_json_v3 import precess_json_v3

app = FastAPI(
    title="FastAPI",
)

# Enable CORS (important if you're using a frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DATABASE_NAME = 'data/hh_aiest.db'
MAPPING_DB_NAME = "data/mapping.db"
SAVING_PATH = "demo1/"  # Directory to save attachments


def getdbData(target: str):
    try:
        db = sqlite3.connect(DATABASE_NAME)
        cur = db.cursor()

        sql = "SELECT * FROM data_management_app_datajson WHERE target = ?"
        cur.execute(sql, (target,))

        data = [
            dict((cur.description[i][0], value) for i, value in enumerate(row))
            for row in cur.fetchall()
        ]
        # assuming the data is only 1 row
        if data:
            data[0].pop("id", None)
            data[0].pop("timestamp", None)
            data[0]["attachment"] = eval(data[0]["attachment"])
            if "est_part" in data[0]:
                data[0].pop("est_part")
            return data[0]
        else:
            return None

    except Exception as e:
        print(str(e))
    finally:
        cur.close()
        db.close()


@app.get("/items/{target}")
def get_item(target: str):
    data = getdbData(target)
    if data:
        return JSONResponse(content=data)
    raise HTTPException(status_code=404, detail="Item not found")


def download_attachment(saving_path, i, url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()

        # Create a filename based on the index
        filename = f"./data/{saving_path}/attachment_{i}.bin"

        # Write the response content to a file
        with open(filename, 'wb') as file:
            file.write(response.content)
        return filename
    except Exception as e:
        print(f"An error occurred: {e}")




@app.get("/items")
def get_db_json(target: str, saving_path: str = SAVING_PATH):
    try:
        response = get_item(target)
    except HTTPException as e:
        raise e

    data = response.body
    import json
    content = json.loads(data)
    attachment = content.get("attachment")
    if not attachment:
        raise HTTPException(status_code=404, detail="No attachments found in JSON response")
    email_array = []

    for i, url in enumerate(attachment):
        file_path = download_attachment(saving_path, i, url)
        email_array.append(file_path)

    # Assuming you have a function to process the JSON data
    precessed = precess_json_v3(content, email_array)

    postData = {"params": {"data": [precessed]}}

    # request to the server if needded
    # url = "https://uat16c.hunghingprinting.com/est_hd/for_ai_insert"
    # x = requests.post(url, json=postData)

    # Assuming the JSON response contains a "result" like this
    x = {
     "jsonrpc": "2.0",
     "id": 1,
     "result": {
         "data": {
             "create_data": [
                 {"est_hd_id": 12345}  # Example response
            ]
        }
    }

    }
    url = "http://localhost:8000/en/api/target_id_mapping/"
    x = requests.post(
        url,
        json={
            "id": x["result"]["data"]["create_data"][0]["est_hd_id"],
            "key": target,
        },
    )
    print(x.text)
    return {
        "status": "success",
        "message": "Data processed and sent successfully.",
        "response": x.json()
    }


class TargetIDMappingRequest(BaseModel):
    id: int  # or str, depending on your data type
    key: int

@app.post("/en/api/target_id_mapping/")
async def target_id_mapping(data: TargetIDMappingRequest):
    received_id = data.id
    received_key = data.key

    # Store in SQLite database
    conn = sqlite3.connect(MAPPING_DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO mappings (id, key) VALUES (?, ?)", (received_id, received_key))
    conn.commit()
    conn.close()

    return {
        "status": "success",
        "received_id": received_id,
        "received_key": received_key
    }
