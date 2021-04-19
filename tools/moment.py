from jinja2 import Markup


class MomentJs:
    def __init__(self, timestamp):
        self.timestamp = timestamp

    def render(self, format):
        return Markup(f"<script>document.write(moment.utc('{self.timestamp}').{format});</script>")

    def standard(self):
        return self.render("format('LLL')")

    def from_now(self):
        return self.render("fromNow()")
