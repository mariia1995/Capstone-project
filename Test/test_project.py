import os
import pytest
import requests
from faker import Faker
from dotenv import load_dotenv

fake = Faker()
load_dotenv()


@pytest.fixture
def get_token():
    headers = {
        'Content-Type': 'application/json'
    }
    body = {"username": "mbelova", "password": "123"}
    url = os.getenv('BASE_URL') + "api/auth"
    response = requests.post(url, headers=headers, json=body)
    return response.json()['token']


data1 = {
    "name": fake.company(),
    "description": ""
}
data2 = {
    "name": fake.company(),
    "description": "description"
}
data3 = {
    "name": "",
    "description": "description"
}


@pytest.mark.parametrize("data, er", [
    (data1, 200),
    (data2, 200),
    (data3, 409)
])
def test_create_project(get_token, data, er):
    body = data
    headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {get_token}'}
    url = os.getenv('BASE_URL') + "api/project"
    response = requests.post(url, headers=headers, json=body)
    assert response.status_code == er
