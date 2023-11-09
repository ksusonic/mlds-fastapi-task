from enum import Enum
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

app = FastAPI()


class DogType(str, Enum):
    terrier = "terrier"
    bulldog = "bulldog"
    dalmatian = "dalmatian"


class Dog(BaseModel):
    name: str
    pk: int
    kind: DogType


class Timestamp(BaseModel):
    id: int
    timestamp: int


dogs_db = {
    0: Dog(name='Bob', pk=0, kind='terrier'),
    1: Dog(name='Marli', pk=1, kind="bulldog"),
    2: Dog(name='Snoopy', pk=2, kind='dalmatian'),
    3: Dog(name='Rex', pk=3, kind='dalmatian'),
    4: Dog(name='Pongo', pk=4, kind='dalmatian'),
    5: Dog(name='Tillman', pk=5, kind='bulldog'),
    6: Dog(name='Uga', pk=6, kind='bulldog')
}

post_db = [
    Timestamp(id=0, timestamp=12),
    Timestamp(id=1, timestamp=10)
]


@app.get('/')
def root():
    return {}


@app.post('/post')
def post():
    return post_db[-1]


@app.get('/dog')
def get_dogs(kind: str) -> List[Dog]:
    return filter(lambda dog: dog.kind == kind, dogs_db.values())


@app.post('/dog')
def post_dog(dog: Dog) -> Dog:
    dogs_db[dog.pk] = dog

    last_timestamp = post_db[-1]
    post_db.append(Timestamp(id=last_timestamp.id + 1, timestamp=last_timestamp.timestamp + 2))
    return dog


@app.get('/dog/{pk}')
def get_dog_by_pk(pk: int):
    dog = dogs_db.get(pk)
    if dog is not None:
        return dog
    raise HTTPException(status_code=404, detail='No such dog')


@app.patch('/dog/{pk}')
def path_dog_by_pk(pk: int, patch_dog: Dog):
    dog = dogs_db.get(pk)
    if dog is None:
        raise HTTPException(status_code=404, detail='No such dog')
    dogs_db[pk] = patch_dog
