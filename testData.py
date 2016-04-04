#!/usr/bin/env python
import webapp2
import models
from google.appengine.ext import ndb

# models.Snippet(
#     title="",
#     notes="",
#     videoID="",
#     startTime="",
#     endTime="",
#     selectedThumbnail=""
# )

TESTING_KEY = "TESTING"


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'

        # obliterate testing data
        pKey = ndb.Key(models.Playlist, TESTING_KEY)
        pKey.delete()

        # regenerate testing data
        playlists = [
            models.Playlist(parent=pKey, title="Playlist A", creator="a@mail.com", snippets=[
                 models.Snippet(
                     title="hertz1",
                     notes="check this out",
                     videoID="ByQD6tAE2yU",
                     startTime=0,
                     endTime=15,
                     selectedThumbnail=1
                 ),
                 models.Snippet(
                     title="heartz2",
                     videoID="ByQD6tAE2yU",
                     startTime=30,
                     endTime=55,
                     selectedThumbnail=2
                 ),
                 models.Snippet(
                     title="ute",
                     notes="here is a different lookout",
                     videoID="YLZoPcGKq7M",
                     startTime=65,
                     endTime=120,
                     selectedThumbnail=3
                 ),
             ]),

            models.Playlist(parent=pKey, title="Playlist B", snippets=[
                models.Snippet(
                    title="top of the morning",
                    videoID="TLBIufF7G1I",
                    startTime=0,
                    endTime=5,
                    selectedThumbnail=3
                ),
                models.Snippet(
                    title="jack truck",
                    notes="super truck super truck super truck super truck",
                    videoID="TLBIufF7G1I",
                    startTime=20,
                    endTime=400,
                    selectedThumbnail=2
                ),
                models.Snippet(
                    title="punch the like button",
                    notes="<Like a Boss!!!!>",
                    videoID="TLBIufF7G1I",
                    startTime=882,
                    endTime=887,
                    selectedThumbnail=1
                )
            ]),

            models.Playlist(parent=pKey, title="Playlist C", creator="C@mail.com", snippets=[
                models.Snippet(
                    title="short computerphile",
                    videoID="vrjAIBgxm_w",
                    startTime=20,
                    endTime=21,
                    selectedThumbnail=2
                )
            ])
        ]

        # store new data
        ndb.put_multi(playlists)


        # query for playlists
        # update one and put it (mostly to generate .yaml)
        # display them with jinja template
        self.response.write("Testing Data populated")
app = webapp2.WSGIApplication([
    ('/testData/', MainHandler)
], debug=True)
