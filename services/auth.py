import logging

import requests

from data_access import (
    create_google_cred, get_google_cred, update_google_cred,
    delete_google_cred, get_notion_cred,
    update_notion_cred, create_notion_cred
)

logger = logging.getLogger(__name__)


def google_cred_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


class AuthService:
    @classmethod
    def store_google_creds(cls, user_id: str, credentials, email) -> [bool, str]:
        """
    This function will update the credentials of a Google user. This also includes
    revocation and partial authorization
    :param user_id: The user's uuid
    :param credentials: Google Credentials
    :param email: The user's email address
    :return: tuple (bool, str)
    """
        if get_google_cred(user_id, email):
            if update_google_cred(google_cred_to_dict(credentials), user_id, email):
                return True, "Credentials updated successfully"
            return False, "Failed to update credentials"

        if create_google_cred(user_id, credentials, email):
            return True, 'Credentials created successfully'
        return False, "Unable to create credentials"

    @classmethod
    def store_notion_creds(cls, user, creds):
        if get_notion_cred(user):
            if update_notion_cred(creds, user):
                return True, "Credentials updated successfully"
            return False, "Failed to update credentials"

        if create_notion_cred(user, creds):
            return True, 'Credentials created successfully'
        return False, "Unable to create credentials"

    @classmethod
    def revoke_creds(cls, user_id, email):
        # Call Google API to revoke the token
        # Delete the creds from the database
        creds = get_google_cred(user_id, email)
        response = requests.post('https://oauth2.googleapis.com/revoke', params={'token': creds.token},
                                 headers={'content-type': 'application/x-www-form-urlencoded'})
        if response.status_code != 200:
            return False, "Unable to revoke credentials"
        creds = get_google_cred(user_id, email)
        if creds is None:
            return False, "No credentials found."
        if delete_google_cred(creds):
            return True, "Credentials revoked successfully"
        return False, "Unable to delete application."
