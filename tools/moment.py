from flask_babel import get_locale
from jinja2 import Markup


class MomentJs:
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def render(self, format):
        script = f"""
        var dt = moment.utc('{self.timestamp}');
        dt.locale('{get_locale().language}');
        var formatted = dt.{format};
        """
        return Markup(f"<script>{script}document.write(formatted);</script>")

    def standard(self):
        return self.render("format('LLL')")

    def from_now(self):
        return self.render("fromNow()")
