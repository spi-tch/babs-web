# this is a small script to update the credentials table with the email address of the user
from util.app import create_app
create_app()

from data_access import get_all_users, add_email_to_cred


if __name__ == '__main__':
    for user in get_all_users():
        add_email_to_cred(user.uuid, user.email)
