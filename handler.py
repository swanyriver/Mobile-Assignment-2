import webapp2
import jinja2
import os
import urllib
import models
from user import validate_user

class Handler(webapp2.RequestHandler):
    WARNING="warning"
    STATUS="status"
    ACTION="action"
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

    def reqJSON(self):
        return 'application/json' in self.request.accept

    def returnJSON(self, jsonSt, code=200, message=None):
        self.response.set_status(code, message)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(jsonSt or '{}')


class PlaylistHandler(Handler):
    def get(self, **kwargs):
        playlist = models.Playlist.getPlaylistFromURL(kwargs)
        if not playlist:
            return self.returnJSON(None, code=404)

        if playlist.isPublic:
            return self.getPlaylist(playlist)

        user = validate_user(self.request)
        if not user or user.key != playlist.key.parent():
            self.response.set_status(401)
            self.response.write("<h1>Unauthorized Access</h1>")
            return

        self.getPlaylist(playlist)

    def post(self, **kwargs):
        playlist = models.Playlist.getPlaylistFromURL(kwargs)

        if not playlist:
            return self.returnJSON(None, code=404)

        user = validate_user(self.request)
        if not user or user.key != playlist.key.parent():
            return self.returnJSON({"msg": "User Validation Failed"}, code=401)

        self.postPlaylist(playlist)


    def delete(self, **kwargs):
        playlist = models.Playlist.getPlaylistFromURL(kwargs)

        if not playlist:
            return self.returnJSON(None, code=404)

        user = validate_user(self.request)
        if not user or user.key != playlist.key.parent():
            return self.returnJSON({"msg": "User Validation Failed"}, code=401)

        self.deletePlaylist(playlist)
