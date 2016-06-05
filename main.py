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
from user import LogHandler, RegHandler, validate_user

dumps = json.dumps
def prettyJson(obj):
    return dumps(obj, indent=2)
json.dumps = prettyJson


# return json of all playlists #/playlist.json
# public playlist or user playlists switched by presence of headers
class allplaylistsJson(Handler):
    def get(self):
        user = validate_user(self.request)
        if not user or "public" in self.request.GET:
            return self.returnJSON(json.dumps(models.Playlist.get_public_playlists()))
        else:
            return self.returnJSON(json.dumps(models.Playlist.get_users_playlists(user)))


# create playlist or return all playlists html # / , /playlist/
class PlaylistMain(Handler):
    def get(self):
        self.render("main.html", var={'playlists': models.Playlist.getAllPublicsForHTML()})

    #create playlists
    def post(self):
        user = validate_user(self.request)
        if not user:
            return self.returnJSON({"msg": "User Validation Failed"}, code=401)

        # create playlist from post request
        if 'title' not in self.request.POST or not self.request.POST['title']:
            return self.returnJSON(None, code=400)
        key = models.Playlist.createAndStore(self.request.POST, user)

        return self.returnJSON(json.dumps({'url':models.Playlist.keyForLinkFromKey(key),
                                    'json':models.Playlist.jsonLinkfromKey(key)}), code=201)

#/playlist/<Playlist>.json
class JSONGetter(Handler):
    def get(self, **kwargs):
        if models.Playlist.__name__ in kwargs:

            plist = models.Playlist.getPlaylistFromURL(kwargs)
            if not plist:
                return self.returnJSON(None, code=404)
            if plist.isPublic:
                return self.returnJSON(plist.json())
            else:
                user = validate_user(self.request)
                if not user or user.key != plist.key.parent():
                    return self.returnJSON({"msg": "User Validation Failed"}, code=401)
                else:
                    return self.returnJSON(plist.json())



# for specific playlists
# /playlist/<playlist>/
class PlaylistRoute(PlaylistHandler):
    def getPlaylist(self, playlist):
        self.render("view.html", {"playlist": playlist})

    #add a snippet
    def postPlaylist(self, playlist):
        #print self.request.POST
        if any((k not in self.request.POST or not self.request.POST[k] for k in
                ("title", "videoID", "startTime", "endTime"))):
            return self.returnJSON(None, code=400, message="Required fields not included")

        #print models.getPopulateDictionary(models.Snippet, self.request.POST.items())

        # validate videoID
        result = urlfetch.fetch("https://www.googleapis.com/youtube/v3/videos?id=%s&key=%s&part=id" % (
            self.request.get('videoID'), credentials.API_KEY))
        if result.status_code != 200:
            return self.returnJSON(None, code=400, message="Invalid YouTube VideoID")

        videoJSON = json.loads(result.content)
        if not videoJSON['pageInfo']['totalResults']:
            return self.returnJSON(None, code=400, message="Invalid YouTube VideoID")

        # create snippet
        newSnippet = models.Snippet(parent=playlist.key, **models.getPopulateDictionary(models.Snippet, self.request.POST.items()))
        # todo validate that start/end times are 0 <= startTime < endTime <= videoLength,  youtube embedd fails gracefully for now

        # put in datastore, then add to playlist
        snptKey = newSnippet.put()
        playlist.snippetKeys.append(snptKey)
        playlist.put()

        # return json with status
        dictout = {"result":"snippet created",
                   "snippet":snptKey.get()._to_dict()}
        return self.returnJSON(json.dumps(dictout), code=201)

    # def putPlaylist(self):
    #     # todo move delete from list and reorder list to here
    #    pass

    def deletePlaylist(self, playlist):
        for k in playlist.snippetKeys:
            k.delete()
        playlist.key.delete()
        return self.returnJSON(None, code=202, message="playlist deleted")

#for specific snippets #/snippet/<Snippet>/
class SnippetRoute(Handler):

    ## Currently not supported, no endpoints for displaying a single snippet ##
    # def get(self, **kwargs):
    #     snpt = models.Snippet.getSnippetFromURL(kwargs)
    #     if not snpt:
    #         return self.returnJSON(None, code=404)
    #     self.render("snippet.html", var={'snippet':snpt})

    def put(self, **kwargs):
        snpt = models.Snippet.getSnippetFromURL(kwargs)
        if not snpt:
            return self.returnJSON(None, code=404)

        #print "SNPT PARENT >>> ", snpt.key.parent().parent()
        user = validate_user(self.request)
        if not user or user.key != snpt.key.parent().parent():
            return self.returnJSON({"msg": "User Validation Failed"}, code=401)

        #update record
        snpt.populate(**models.getPopulateDictionary(models.Snippet, self.request.POST.items()))
        snpt.put()
        return self.returnJSON(json.dumps({"url":self.request.path, "snippet":json.loads(snpt.json())}), code=200, message="snippet updated")


    def delete(self, **kwargs):
        snpt = models.Snippet.getSnippetFromURL(kwargs)
        if not snpt:
            return self.returnJSON(None, code=404)
        plist = snpt.key.parent().get()

        user = validate_user(self.request)
        if not user or user.key != plist.key.parent():
            return self.returnJSON({"msg": "User Validation Failed"}, code=401)

        if snpt.key in plist.snippetKeys:
            plist.snippetKeys.remove(snpt.key)
            plist.put()
        snpt.key.delete()
        return self.returnJSON(None, code=202, message="Snippet deleted")

app = webapp2.WSGIApplication([
    webapp2.Route('/', PlaylistMain),
    webapp2.Route('/playlist.json', allplaylistsJson),
    webapp2.Route('/playlist/', PlaylistMain),
    webapp2.Route('/playlist/<Playlist>/', handler=PlaylistRoute),
    webapp2.Route('/playlist/<Playlist>.json', handler=JSONGetter),
    webapp2.Route('/snippet/<Snippet>/', handler=SnippetRoute),
    #webapp2.Route('/snippet/<Snippet>.json', handler=JSONGetter),
    ('/register', RegHandler),
    ("/login", LogHandler)
], debug=True)
