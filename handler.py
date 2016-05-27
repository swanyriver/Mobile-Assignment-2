import webapp2
import jinja2
import os
import urllib
import models


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
        else:
            self.getPlaylist(playlist)

    def post(self, **kwargs):
        playlist = models.Playlist.getPlaylistFromURL(kwargs)

        if not playlist:
            return self.returnJSON(None, code=404)
        else:
            self.postPlaylist(playlist)

    # def put(self, **kwargs):
    #     playlist = models.Playlist.getPlaylistFromURL(kwargs)
    #
    #     if not playlist:
    #         return self.returnJSON(None, code=404)
    #     else:
    #         self.putPlaylist(playlist)

    def delete(self, **kwargs):
        playlist = models.Playlist.getPlaylistFromURL(kwargs)

        if not playlist:
            return self.returnJSON(None, code=404)
        else:
            self.deletePlaylist(playlist)
