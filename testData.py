#!/usr/bin/env python
import webapp2
import models
from google.appengine.ext import ndb
import handler


# models.Snippet(
#     title="",
#     notes="",
#     videoID="",
#     startTime="",
#     endTime="",
#     selectedThumbnail=""
# )


class MainHandler(handler.Handler):
    def get(self):

        # obliterate testing data
        #pKey = ndb.Key(models.Playlist, TESTING_KEY)
        #for p in  models.Playlist.query(ancestor=pKey).fetch(): p.key.delete()

        for p in models.Playlist.query():
            p.key.delete()


        # regenerate testing data
        snippets = [
            [
                models.Snippet(
                    title="hertz1",
                    notes="check this out",
                    videoID="ByQD6tAE2yU",
                    startTime=0,
                    endTime=15,
                ),
                models.Snippet(
                    title="heartz2",
                    videoID="ByQD6tAE2yU",
                    startTime=30,
                    endTime=55,
                ),
                models.Snippet(
                    title="ute",
                    notes="here is a different lookout",
                    videoID="YLZoPcGKq7M",
                    startTime=65,
                    endTime=120,
                ),
            ],
            [
                models.Snippet(
                    title="top of the morning",
                    videoID="TLBIufF7G1I",
                    startTime=0,
                    endTime=5,
                ),
                models.Snippet(
                    title="jack truck",
                    notes="super truck super truck super truck super truck",
                    videoID="TLBIufF7G1I",
                    startTime=20,
                    endTime=400,
                ),
                models.Snippet(
                    title="punch the like button",
                    notes="<Like a Boss!!!!>",
                    videoID="TLBIufF7G1I",
                    startTime=882,
                    endTime=887,
                )
            ],
            [
                models.Snippet(
                    title="short computerphile",
                    videoID="vrjAIBgxm_w",
                    startTime=20,
                    endTime=21,
                )
            ]

        ]
        playlists = [
            models.Playlist(parent=ndb.Key(models.Playlist, 'a@mail.com'), title="Playlist A", creator="a@mail.com"),

            models.Playlist(parent=models.Playlist.AnonymousParent, title="Playlist B"),

            models.Playlist(parent=ndb.Key(models.Playlist, 'a@mail.com'), title="Playlist C", creator="a@mail.com")
        ]

        # store new data
        ndb.put_multi(playlists)

        for p,snpts in zip(playlists, snippets):
            k=p.put()
            for snp in snpts:
                snp.parent = k
                p.snippets.append(snp.put())
            p.put()



        # query for playlists
        # playlistQuery = models.Playlist.query(ancestor=pKey).order(-models.Playlist.date_added)
        # playlists = playlistQuery.fetch()
        #playlists = models.Playlist.getAll(TESTING_KEY)


        # update one and put it (mostly to generate .yaml)
        #playlists[0].title += " updated"
        #playlists[0].put()

        # display them with jinja template

        #self.render("viewAll.html", var={"playlists": playlists})
        #for p in playlists: self.response.write(p.toString() + "\n------------------------------------------------\n")

        #self.response.write("Testing Data populated")

        self.response.headers['Content-Type'] = 'text/plain'
        for p in models.Playlist.query():
            self.response.write("%r\n"%p)
            for snp in p.snippets:
                snp = snp.get()
                self.response.write("%r\n"%snp)
            self.response.write("----------------------------------------\n")


class viewOne(handler.Handler):
    def get(self):
        self.render("viewAll.html", var={'playlists': [models.Playlist.getPlaylistFromRequest(self.request)]})

app = webapp2.WSGIApplication([
    ('/testData/playlist/', viewOne),
    ('/testData/', MainHandler)
], debug=True)
