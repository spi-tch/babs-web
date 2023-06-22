from constants import FREE_PLAN
from data_access import User, update_user, delete_user_channel, get_user_channels


def downgrade_user(user: User, plan=FREE_PLAN):
    """"""
    # set user's tier/plan to "free"
    update_user(user, {"tier": plan})

    # pause their channels except the first one they connected
    channels = get_user_channels(user.uuid)
    for channel in channels[1:]:
        # the channel is deleted, but in this case, their messages are left intact.
        delete_user_channel(user.uuid, channel.sender_id)
