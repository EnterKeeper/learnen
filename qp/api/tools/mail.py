from flask import render_template
from flask_babel import _
from flask_mail import Message


class MessageGenerator:
    def __init__(self, *emails):
        self.emails = list(emails)

    def reset_password(self, user, token):
        msg = Message(subject=_("Reset password"),
                      recipients=self.emails,
                      html=render_template("mail/reset_password.html", token=token, user=user)
                      )
        return msg

    def confirm_email(self, user, token):
        msg = Message(subject=_("Confirm email"),
                      recipients=self.emails,
                      html=render_template("mail/confirm_email.html", token=token, user=user)
                      )
        return msg
