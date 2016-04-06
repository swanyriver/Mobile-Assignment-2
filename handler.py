import webapp2
import jinja2
import os
import urllib

class Handler(webapp2.RequestHandler):
    WARNING="warning"
    STATUS="status"
    JINJA_ENVIRONMENT = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)

    def render(self, template, var={}):

        var[Handler.STATUS] = self.getStatus()
        var[Handler.WARNING] = self.getWarning()

        self.response.headers['Content-Type'] = 'text/html'
        jTemplate = self.JINJA_ENVIRONMENT.get_template(template)
        self.response.write(jTemplate.render(var))

    @staticmethod
    def warning(text):
        return "%s=%s"%(Handler.WARNING, urllib.quote(text))

    @staticmethod
    def status(text):
        return "%s=%s"%(Handler.STATUS, urllib.quote(text))

    def getReqVal(self, k):
        val = self.request.get(k)
        if val is None: return None
        return urllib.unquote(val)

    def getWarning(self):
        return self.getReqVal(Handler.WARNING)

    def getStatus(self):
        return self.getReqVal(Handler.STATUS)
