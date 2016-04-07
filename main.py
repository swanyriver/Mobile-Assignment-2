#!/usr/bin/env python

###############################################
# youtube frame################3
## <iframe width="560" height="315" src="https://www.youtube.com/embed/XTTu0k1H2JI?start=30&amp;end=55&amp;version=3" frameborder="0"></iframe>

# youtube thumbnail 0 is large, 1-3 small
# http://img.youtube.com/vi/<insert-youtube-video-id-here>/[0-3].jpg

# dectect if valid video id
# https://www.googleapis.com/youtube/v3/videos?id=<videoID>&key=<API_KEY>&part=id
####################################################


import webapp2
from handler import Handler, PlaylistHandler
import models
import credentials
import json
from google.appengine.api import urlfetch
from google.appengine.ext import ndb


class MainHandler(Handler):
    def get(self):
        self.render("main.html", var={'playlists': models.Playlist.getAll()})


class CreateHandler(Handler):
    def get(self):
        self.render("create.html")

    def post(self):
        # create playlist from post request
        if 'title' not in self.request.POST:
            return self.redirect('/')
        key = models.Playlist.createAndStore({k: v for k, v in self.request.POST.items() if v})

        # redirect to add snippet
        return self.redirect("/add/?" + models.Playlist.keyForLinkFromKey(key))


class addHandler(Handler):
    def get(self):
        playlist = models.Playlist.getPlaylistFromRequest(self.request)
        if not playlist:
            return self.redirect('/?' + Handler.warning("Playlist not found"))
        self.render("add.html", var={"playlist": playlist})

    def post(self):
        playlist = models.Playlist.getPlaylistFromRequest(self.request)

        if not playlist:
            return self.redirect("/?" + Handler.warning("Playlist not found"))
        if any((k not in self.request.POST or not self.request.POST[k] for k in
                ("title", "videoID", "startTime", "endTime"))):
            return self.redirect('/add/?' + Handler.warning("required fields not found") + '&' + playlist.keyForLink())

        self.response.write(models.getPopulateDictionary(models.Snippet, self.request.POST.items()))

        # validate videoID
        # add part=id,snippet to get title from snippet object
        result = urlfetch.fetch("https://www.googleapis.com/youtube/v3/videos?id=%s&key=%s&part=id" % (
            self.request.get('videoID'), credentials.API_KEY))
        if result.status_code != 200:
            return self.redirect("/add/?%s&%s" %
                                 (playlist.keyForLink(), Handler.warning("Youtube unreachable to verify videoID")))

        videoJSON = json.loads(result.content)
        if not videoJSON['pageInfo']['totalResults']:
            return self.redirect("/add/?%s&%s" %
                                 (playlist.keyForLink(), Handler.warning("Invalid YouTube VideoID")))

        # create snippet
        newSnippet = models.Snippet(**models.getPopulateDictionary(models.Snippet, self.request.POST.items()))
        # todo validate that start/end times are 0 <= startTime < endTime <= videoLength,  youtube embedd fails gracefully for now


        # add it to playlist and put playlist
        playlist.snippets.append(newSnippet)
        playlist.put()

        # redirect to view with playlist and status
        return self.redirect("/view/?%s&%s" %
                             (playlist.keyForLink(), Handler.status("Snippet added to playlist")))


class viewHandler(PlaylistHandler):
    def getPlaylist(self, playlist):
        self.render("view.html", {"playlist": playlist})


class delHandler(PlaylistHandler):
    def getPlaylist(self, playlist):
        playlist.key.delete()
        return self.redirect("/?" + Handler.status("Playlist Deleted"))


class delSnippetHandler(PlaylistHandler):
    def getPlaylist(self, playlist):
        self.render("removeSnippets.html", {'playlist': playlist, 'delete': True})

    def post(self):
        playlist = models.Playlist.getPlaylistFromRequest(self.request)
        if not playlist:
            return self.redirect("/?" + Handler.warning("Playlist not found"))

        delSnippets = [int(v) for v in self.request.get_all('snippetIndex') if 0 <= int(v) < len(playlist.snippets)]
        playlist.snippets = [s for i, s in enumerate(playlist.snippets) if i not in delSnippets]
        playlist.put()

        self.redirect("/view/?" + playlist.keyForLink())


class editHandler(PlaylistHandler):
    def getPlaylist(self, playlist):
        self.render("editPlaylist.html", {'playlist': playlist})

    def post(self):
        playlist = models.Playlist.getPlaylistFromRequest(self.request)
        if not playlist:
            return self.redirect("/?" + Handler.warning("Playlist not found"))

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write("%s\n" % self.request.POST)
        self.response.write("%s\n" % self.request.get_all('key'))
        for key in self.request.get_all('key'):
            d = {k: int(self.request.get(key + '_' + k)) if isinstance(
                                                             getattr(models.Snippet, k),
                                                             ndb.IntegerProperty) else
                self.request.get(key+'_'+k) for k in models.Snippet._properties}
            self.response.write("snippet %s: %s\n" % (key, d))
            # self.response.write("snippet %s: %s" % (key,
            #                                         {k: int(self.request.get(key + '_' + k)) if isinstance(
            #                                             getattr(models.Snippet, k),
            #                                             ndb.IntegerProperty) else self.request.get(key + '_' + k) for k
            #                                          in models.Snippet._properties}))

        self.response.write("\n--------------before--------------------------------\n%s\n--------------------------------\n\n"%playlist)
        playlist.snippets = [models.Snippet(**{
            k: int(self.request.get(key + '_' + k)) if isinstance(getattr(models.Snippet, k),
                                                              ndb.IntegerProperty) else self.request.get(key + '_' + k)
            for k in models.Snippet._properties}) for key in self.request.get_all('key')]
        #playlist.put()
        #return self.redirect("/view/?" + playlist.keyForLink())

        self.response.write("\n--------------after--------------------------------\n%s\n--------------------------------\n\n"%playlist)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/create/', CreateHandler),
    ('/add/', addHandler),
    ('/view/', viewHandler),
    ('/delete/', delHandler),
    ('/delsnippets/', delSnippetHandler),
    ('/edit/', editHandler)
], debug=True)
