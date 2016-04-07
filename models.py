from google.appengine.ext import ndb
import sys

DATASTORE_KEY = "DEV"


def getPopulateDictionary(model_class, request):
    return {k: int(v) if isinstance(getattr(model_class, k), ndb.IntegerProperty) else v for k, v in request if k in model_class._properties }

class Snippet(ndb.Model):
    title = ndb.StringProperty(indexed=False, required=True)
    notes = ndb.StringProperty(indexed=False, required=False)
    videoID = ndb.StringProperty(indexed=False, required=True)
    startTime = ndb.IntegerProperty(indexed=False, required=True)
    endTime = ndb.IntegerProperty(indexed=False, required=True)
    selectedThumbnail = ndb.IntegerProperty(indexed=False, required=True, default=1)

    # Used in debugging, GAE makes use of __str__ so toString is used by me
    def toString(self): return str(self.__dict__)


class Playlist(ndb.Model):
    title = ndb.StringProperty(indexed=False, required=True)
    creator = ndb.StringProperty(indexed=False, required=True, default="Anonymous")
    snippets = ndb.StructuredProperty(Snippet, repeated=True)
    date_added = ndb.DateTimeProperty(auto_now_add=True)

    # Used in debugging, GAE makes use of __str__ so toString is used by me
    def toString(self):
        st = str(self.title)
        st += str(self.creator)
        for snip in self.snippets: st += snip.toString() + '\n'
        return st

    def keyForForm(self):
        return "<input type=\"hidden\" name=\"%s\" value=\"%s\"></input>"%(Playlist.__name__, self.key.urlsafe())

    @staticmethod
    def keyForLinkFromKey(key):
        return "%s=%s" % (Playlist.__name__, key.urlsafe())

    def keyForLink(self):
        return Playlist.keyForLinkFromKey(self.key)

    @staticmethod
    def getAll(ancestor=DATASTORE_KEY):
        pkey = ndb.Key(Playlist, ancestor)
        pquery = Playlist.query(ancestor=pkey).order(-Playlist.date_added)
        return pquery.fetch()

    @staticmethod
    def getPlaylistFromRequest(request):
        try:
            pkey = ndb.Key(urlsafe=request.get(Playlist.__name__))
            print pkey
            return pkey.get()
        except:
            print sys.exc_info()[0]
            return None

    @staticmethod
    def createAndStore(kv):
        newPlaylist = Playlist(parent=ndb.Key(Playlist, DATASTORE_KEY))
        newPlaylist.populate(**kv)
        return newPlaylist.put()

