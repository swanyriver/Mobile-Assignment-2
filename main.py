#!/usr/bin/env python

###############################################
# youtube frame################3
## <iframe width="560" height="315" src="https://www.youtube.com/embed/XTTu0k1H2JI?start=30&amp;end=55&amp;version=3" frameborder="0"></iframe>

# youtube thumbnail 0 is large, 1-3 small
#http://img.youtube.com/vi/<insert-youtube-video-id-here>/[0-3].jpg

# dectect if valid video id
# https://www.googleapis.com/youtube/v3/videos?id=<videoID>&key=<API_KEY>&part=id
####################################################


import webapp2
from handler import Handler
import models


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
        if any((k not in self.request.POST or not self.request.POST[k] for k in ("title", "videoID", "startTime", "endTime"))):
            return self.redirect('/add/?' + Handler.warning("required fields not found") + '&' + playlist.keyForLink())

        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(playlist.toString())
        self.response.write('\n')
        self.response.write(self.request.POST)
        self.response.write('\n')

        #self.response.write(models.Snippet._properties)
        # for k,v in models.Snippet._properties.items():
        #     self.response.write("%s : %s %s\n"%(k, str(type(v)), isinstance(v, ndb.IntegerProperty)))
        # snp = models.Snippet(**self.request.POST)
        # self.response.write('\n')
        # self.response.write(snp.toString())

        self.response.write(models.getPopulateDictionary(models.Snippet, self.request.POST.items()))

        # validate video

        # create snippet
        newSnippet = models.Snippet(**models.getPopulateDictionary(models.Snippet, self.request.POST.items()))

        self.response.write('\n')
        self.response.write(newSnippet.toString())

        # add it to playlist and put playlist

        # redirect to view with playlist and status



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/create/', CreateHandler),
    ('/add/', addHandler)
], debug=True)
