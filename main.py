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

dumps = json.dumps
def prettyJson(obj):
    return dumps(obj, indent=2)
json.dumps = prettyJson


class MainHandler(Handler):
    def get(self):
        self.render("main.html", var={'playlists': models.Playlist.getAll()})


# return json of all playlists
class allplaylistsJson(Handler):
    def get(self):
        return self.returnJSON(
            json.dumps([p._to_dict() for p in models.Playlist.query()])
        )


# create playlist or return all playlists html
class PlaylistMain(Handler):
    def get(self):
        self.render("main.html", var={'playlists': models.Playlist.getAll()})

    #create playlists
    def post(self):
        # create playlist from post request
        if 'title' not in self.request.POST:
            if self.fromUI():
                return self.redirect('/')
            else:
                return self.returnJSON(None, code=400)
        key = models.Playlist.createAndStore({k: v for k, v in self.request.POST.items() if v})

        if self.fromUI():
            # redirect to add snippet
            return self.redirect(models.Playlist.keyForLinkFromKey(key))

        else:
            return self.returnJSON(json.dumps({'url':models.Playlist.keyForLinkFromKey(key),
                                        'json':models.Playlist.jsonLinkfromKey(key)}), code=201)


class JSONGetter(Handler):
    def get(self, **kwargs):
        if models.Snippet.__name__ in kwargs:
            snpt = models.Snippet.getSnippetFromURL(kwargs)
            if not snpt:
                return self.returnJSON(None, code=404)
            return self.returnJSON(snpt.json())

        if models.Playlist.__name__ in kwargs:
            plist = models.Playlist.getPlaylistFromURL(kwargs)
            if not plist:
                return self.returnJSON(None, code=404)
            return self.returnJSON(plist.json())



# for specific playlists
# /playlist/<playlist>/
class PlaylistRoute(PlaylistHandler):
    def getPlaylist(self, playlist):
        print "here is the playlist", playlist, playlist.snippets
        self.render("view.html", {"playlist": playlist})

    #add a snippet
    def postPlaylist(self, playlist):
        print self.request.POST
        if any((k not in self.request.POST or not self.request.POST[k] for k in
                ("title", "videoID", "startTime", "endTime"))):
            return self.returnJSON(None, code=400, message="Required fields not included")

        print models.getPopulateDictionary(models.Snippet, self.request.POST.items())

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
        pass

    def deletePlaylist(self, playlist):
        for k in playlist.snippetKeys:
            k.key.delete()
        playlist.key.delete()
        return self.returnJSON(None, code=202, message="playlist deleted")

#for specific snippets
class SnippetRoute(Handler):
    def get(self, **kwargs):
        snpt = models.Snippet.getSnippetFromURL(kwargs)
        if not snpt:
            return self.returnJSON(None, code=404)
        self.render("snippet.html", var={'snippet':snpt})

    def delete(self, **kwargs):
        snpt = models.Snippet.getSnippetFromURL(kwargs)
        if not snpt:
            return self.returnJSON(None, code=404)
        plist = snpt.key.parent().get()
        if snpt.key in plist.snippetKeys:
            plist.snippetKeys.remove(snpt.key)
            plist.put()
        snpt.key.delete()
        return self.returnJSON(None, code=202, message="Snippet deleted")

app = webapp2.WSGIApplication([
    webapp2.Route('/', allplaylistsJson),
    webapp2.Route('/playlist.json', allplaylistsJson),
    webapp2.Route('/playlist/<Playlist>/', handler=PlaylistRoute),
    webapp2.Route('/playlist/<Playlist>.json', handler=JSONGetter),
    webapp2.Route('/snippet/<Snippet>/', handler=SnippetRoute),
    webapp2.Route('/snippet/<Snippet>.json', handler=JSONGetter)
], debug=True)



##### previous handler for adding snippets
# class addHandler(Handler):
#     def get(self):
#         playlist = models.Playlist.getPlaylistFromRequest(self.request)
#         if not playlist:
#             return self.redirect('/?' + Handler.warning("Playlist not found"))
#         self.render("add.html", var={"playlist": playlist})
#
#     def post(self):
#         playlist = models.Playlist.getPlaylistFromRequest(self.request)
#
#         if not playlist:
#             return self.redirect("/?" + Handler.warning("Playlist not found"))
#         if any((k not in self.request.POST or not self.request.POST[k] for k in
#                 ("title", "videoID", "startTime", "endTime"))):
#             return self.redirect('/add/?' + Handler.warning("required fields not found") + '&' + playlist.keyForLink())
#
#         self.response.write(models.getPopulateDictionary(models.Snippet, self.request.POST.items()))
#
#         # validate videoID
#         # add part=id,snippet to get title from snippet object
#         result = urlfetch.fetch("https://www.googleapis.com/youtube/v3/videos?id=%s&key=%s&part=id" % (
#             self.request.get('videoID'), credentials.API_KEY))
#         if result.status_code != 200:
#             return self.redirect("/add/?%s&%s" %
#                                  (playlist.keyForLink(), Handler.warning("Youtube unreachable to verify videoID")))
#
#         videoJSON = json.loads(result.content)
#         if not videoJSON['pageInfo']['totalResults']:
#             # todo repopulate fields
#             return self.redirect("/add/?%s&%s" %
#                                  (playlist.keyForLink(), Handler.warning("Invalid YouTube VideoID")))
#
#         # create snippet
#         newSnippet = models.Snippet(**models.getPopulateDictionary(models.Snippet, self.request.POST.items()))
#         # todo validate that start/end times are 0 <= startTime < endTime <= videoLength,  youtube embedd fails gracefully for now
#
#
#         # add it to playlist and put playlist
#         playlist.snippets.append(newSnippet)
#         playlist.put()
#
#         # redirect to view with playlist and status
#         return self.redirect("/view/?%s&%s" %
#                              (playlist.keyForLink(), Handler.status("Snippet added to playlist")))



# class delHandler(PlaylistHandler):
#     def getPlaylist(self, playlist):
#         playlist.key.delete()
#         return self.redirect("/?" + Handler.status("Playlist Deleted"))
#
#
# class delSnippetHandler(PlaylistHandler):
#     def getPlaylist(self, playlist):
#         if playlist.snippets:
#             self.render("removeSnippets.html", {'playlist': playlist, 'delete': True})
#         else:
#             return self.redirect("/view/?" + playlist.keyForLink() + '&' +
#                                  Handler.warning("This playlist has no snippets to remove"))
#
#     def post(self):
#         playlist = models.Playlist.getPlaylistFromRequest(self.request)
#         if not playlist:
#             return self.redirect("/?" + Handler.warning("Playlist not found"))
#
#         delSnippets = [int(v) for v in self.request.get_all('snippetIndex') if 0 <= int(v) < len(playlist.snippets)]
#         playlist.snippets = [s for i, s in enumerate(playlist.snippets) if i not in delSnippets]
#         playlist.put()
#
#         self.redirect("/view/?" + playlist.keyForLink())
#
#
# class editHandler(PlaylistHandler):
#     def getPlaylist(self, playlist):
#         if playlist.snippets:
#             self.render("editPlaylist.html", {'playlist': playlist})
#         else:
#             return self.redirect("/view/?" + playlist.keyForLink() + '&' +
#                                  Handler.warning("This playlist has no snippets to edit"))
#
#     def post(self):
#         playlist = models.Playlist.getPlaylistFromRequest(self.request)
#         if not playlist:
#             return self.redirect("/?" + Handler.warning("Playlist not found"))
#         try:
#             playlist.snippets = [models.Snippet(**{
#                 k: int(self.request.get(key + '_' + k)) if isinstance(getattr(models.Snippet, k),
#                                                                   ndb.IntegerProperty) else self.request.get(key + '_' + k)
#                 for k in models.Snippet._properties}) for key in self.request.get_all('key')]
#         except:
#             print sys.exc_info()[0]
#             self.redirect("/view/?" + playlist.keyForLink() + '&' + Handler.warning("There was a problem applying edits"))
#
#         req_fields = models.Snippet._properties.keys()
#         req_fields.remove('notes')
#
#         if any(not v for v in [getattr(snpt, n) for snpt in playlist.snippets for n in req_fields]):
#             return self.redirect("/view/?" + playlist.keyForLink() + '&' + Handler.warning("Required fields were missing"))
#
#         playlist.put()
#         return self.redirect("/view/?" + playlist.keyForLink() + '&' + Handler.status("Edits applied to playlist"))


# app = webapp2.WSGIApplication([
#     ('/', MainHandler),
#     ('/create/', CreateHandler),
#     ('/add/', addHandler),
#     ('/view/', viewHandler),
#     ('/delete/', delHandler),
#     ('/delsnippets/', delSnippetHandler),
#     ('/edit/', editHandler)
# ], debug=True)
