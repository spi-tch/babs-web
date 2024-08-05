# this is a small script to update the application for all users since we added a new field to the user model

from util.app import create_app
create_app()

from data_access import get_all_users, update_app


def update_app_for_user(uuid, email):
    update_app(uuid, email)


if __name__ == '__main__':
    for user in get_all_users():
        update_app_for_user(user.uuid, user.email)
