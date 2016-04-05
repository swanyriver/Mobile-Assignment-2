import webapp2
import jinja2
import os


class Handler(webapp2.RequestHandler):
    JINJA_ENVIRONMENT = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)

    def render(self, template, var=None):
        self.response.headers['Content-Type'] = 'text/html'
        jTemplate = self.JINJA_ENVIRONMENT.get_template(template)
        if var :self.response.write(jTemplate.render(var))
        else: self.response.write(jTemplate.render())
