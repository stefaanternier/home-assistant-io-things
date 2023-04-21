import asyncio
import requests
import logging

import google.cloud
from google.cloud import firestore
from .const import DOMAIN, ACCESS_TOKEN, EMAIL, PASSWORD

_LOGGER = logging.getLogger(__name__)

async def authenicate_firebase(hass, config):  # relies on service account, so we would use it in public code
    try:
        access_token = config[DOMAIN][ACCESS_TOKEN]
        hass.data[DOMAIN][ACCESS_TOKEN] = config[DOMAIN][ACCESS_TOKEN]
        access_token2 = hass.data[DOMAIN][ACCESS_TOKEN]
        print(f'at is {access_token2}')
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

    except Exception as e:
        print(f"Caught exception: {e}")

async def async_setup(hass, config):
    _LOGGER.info(
        "=> Io-things setup has started",
    )
    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][ACCESS_TOKEN] = config[DOMAIN][ACCESS_TOKEN]
    access_token2 = hass.data[DOMAIN][ACCESS_TOKEN]
    print(f'at is {access_token2}')
    # task = asyncio.create_task(authenicate(hass, config))
    return True
