from flask_babel import _, lazy_gettext

from qp.api.models import users

LANGUAGES = {
    "en": "English",
    "ru": "Русский"
}

GROUPS = {
    users.UserGroup: lazy_gettext("User"),
    users.ModeratorGroup: lazy_gettext("Moderator"),
    users.AdminGroup: lazy_gettext("Admin"),
    users.OwnerGroup: lazy_gettext("Owner")
}

INTERNAL_ERROR_MSG = _("Internal error. Try again.")
NO_RIGHTS_ERROR_MSG = _("You have no rights to do this.")
