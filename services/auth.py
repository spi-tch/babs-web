import logging

import requests
from sqlalchemy import update

from data_access import GoogleCreds, create_google_cred, get_google_cred, update_google_cred, delete_google_cred
from util.app import db

logger = logging.getLogger(__name__)


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}


class AuthService:
  @classmethod
  def store_google_creds(cls, user_id: str, credentials) -> [bool, str]:
    """
    This function will update the credentials of a Google user. This also includes
    revocation and partial authorization
    :param user_id: The user's uuid
    :param credentials: Google Credentials
    :return: tuple (bool, str)
    """
    if get_google_cred(user_id):
      if update_google_cred(credentials_to_dict(credentials), user_id):
        return True, "Credentials updated successfully"
      return False, "Failed to update credentials"

    if create_google_cred(user_id, credentials):
      return True, 'Credentials created successfully'
    return False, "Unable to create credentials"

  @classmethod
  def revoke_creds(cls, user_id):
    # Call Google API to revoke the token
    # Delete the creds from the database
    creds = get_google_cred(user_id)
    response = requests.post('https://oauth2.googleapis.com/revoke', params={'token': creds.token},
                             headers={'content-type': 'application/x-www-form-urlencoded'})
    if response.status_code != 200:
      return False, "Unable to revoke credentials"
    creds = get_google_cred(user_id)
    if creds is None:
      return False, "No credentials found."
    if delete_google_cred(creds):
      return True, "Credentials revoked successfully"
    return False, "Unable to delete application."

