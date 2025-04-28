import requests

requests.post(
    "http://localhost:3000/login", data={"username": "trigger", "password": "gadget"}
)