from fastapi import FastAPI
from typing import List
from pydantic import BaseModel

class Product(BaseModel):
    title: str
    description: str
    imagePath: str
    unitPrice: float

app = FastAPI()

fake_product_db = [
    {
        "title": "macbook pro 16\"",
        "description": "Cutting edge technology with solid performance.",
        "imagePath": "somewhere/on/this/server/or/s3",
        "unitPrice": 3000.5,
    }
]


@app.get('/', response_model=List[Product])
async def index():
    return fake_product_db