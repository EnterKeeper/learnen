class UserGroup:
    id = 0
    title = "User"

    @classmethod
    def is_allowed(cls, user_group_id):
        return user_group_id >= cls.id


class ModeratorGroup(UserGroup):
    id = 1
    title = "Moderator"


class AdminGroup(UserGroup):
    id = 10
    title = "Admin"


groups = (UserGroup, ModeratorGroup, AdminGroup)


def get_group(id=None, title=None):
    for group in groups:
        if group.id == id or group.title == title:
            return group
    return None
