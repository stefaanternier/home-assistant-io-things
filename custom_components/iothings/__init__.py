import asyncio
import requests
import google.cloud
from google.cloud import firestore
from .const import DOMAIN, ACCESS_TOKEN, EMAIL, PASSWORD

async def async_setup(hass, config):
    access_token = config[DOMAIN][ACCESS_TOKEN]
    auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={access_token}"
    data = {
        "email": config[DOMAIN][EMAIL],
        "password": config[DOMAIN][PASSWORD],
        "returnSecureToken": True
    }
    response = await asyncio.to_thread(requests.post, auth_url, json=data)
    response_data = response.json()
    token = response_data["idToken"]

    credentials, project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
    credentials = credentials.with_quota_project(project)
    credentials.token = token

    db = firestore.Client(project=project, credentials=credentials)
    hass.data['iothingsdb'] = db
    return True
