from functools import lru_cache
from fastapi import Depends, FastAPI
from pydantic import BaseModel, BaseSettings
from pymongo import MongoClient
from typing import List


class Settings(BaseSettings):
    DB_USERNAME: str = ''
    DB_PASSWORD: str = ''
    DB_DATABASE: str = ''
    class Config:
        env_file = '.env'
        env_nested_delimiter = "__"

class Product(BaseModel):
    _id: str
    title: str
    description: str
    imagePath: str
    unitPrice: float


settings = Settings()

client = MongoClient('mongodb://%s:%s@mongo' % (settings.DB_USERNAME, settings.DB_PASSWORD))
db = client[settings.DB_DATABASE]

app = FastAPI()

@app.get('/', response_model=List[Product])
def index():
    products = []
    for product in db.products.find():
        products.append(Product(**product))
    return products