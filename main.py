from pymongo import MongoClient
from bson.objectid import ObjectId
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, BaseSettings, Field
from typing import List


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class Settings(BaseSettings):
    DB_HOST: str = 'localhost'
    DB_USERNAME: str = ''
    DB_PASSWORD: str = ''
    DB_DATABASE: str = ''
    class Config:
        env_file = '.env'
        env_nested_delimiter = "__"

class Product(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    title: str
    description: str
    imagePath: str
    unitPrice: float

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


settings = Settings()

client = MongoClient('mongodb://%s:%s@%s' % (settings.DB_USERNAME, settings.DB_PASSWORD, settings.DB_HOST))
db = client[settings.DB_DATABASE]

app = FastAPI()

@app.get('/products', response_description="Get all products", response_model=List[Product], response_model_exclude_none=True)
def index(page: int = 1, per_page: int = 10):
    products = []
    for product in db.products.find().limit(per_page).skip((page - 1) * per_page):
        products.append(Product(**product))
    return products

@app.post('/products', response_description="Add new product", response_model=Product)
def create(product: Product):
    product_id = db.products.insert_one(product.dict()).inserted_id
    created_product = db.products.find_one({'_id': product_id})
    return Product(**created_product)

@app.get('/products/{id}', response_description="Get product by id", response_model=Product, response_model_exclude_none=True)
def get(id: PyObjectId):
    product = db.products.find_one({'_id': id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product)

@app.put('/products/{id}', response_description="Update product by id", response_model=Product)
def update(id: PyObjectId, product: Product):
    product_id = db.products.update_one({'_id': id}, {"$set": product.dict()}).upserted_id
    if not product_id:
        raise HTTPException(status_code=404, detail="Product not found")
    updated_product = db.products.find_one({'_id': product_id})
    return Product(**updated_product)

@app.delete('/products/{id}', response_description="Delete product")
def delete(id: PyObjectId):
    if db.products.delete_one({'_id': id}).deleted_count == 1:
        return {'message': 'Product deleted'}
    else:
        raise HTTPException(status_code=404, detail='Product not found')