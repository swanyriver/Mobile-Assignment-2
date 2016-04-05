from google.appengine.ext import ndb


class Snippet(ndb.Model):
    title = ndb.StringProperty(indexed=False, required=True)
    notes = ndb.StringProperty(indexed=False, required=False)
    videoID = ndb.StringProperty(indexed=False, required=True)
    startTime = ndb.IntegerProperty(indexed=False, required=True)
    endTime = ndb.IntegerProperty(indexed=False, required=True)
    selectedThumbnail = ndb.IntegerProperty(indexed=False, required=True)

    # Used in debugging, GAE makes use of __str__ so toString is used by m
    def toString(self): return str(self.__dict__)


class Playlist(ndb.Model):
    title = ndb.StringProperty(indexed=False, required=True)
    creator = ndb.StringProperty(indexed=False, required=False)
    snippets = ndb.StructuredProperty(Snippet, repeated=True)
    date_added = ndb.DateTimeProperty(auto_now_add=True)

    # Used in debugging, GAE makes use of __str__ so toString is used by m
    def toString(self):
        st = str(self.title)
        st += str(self.creator)
        for snip in self.snippets: st += snip.toString() + '\n'
        return st

    def keyForForm(self):
        return "<input type=\"hidden\" name=\"%s\" value=\"%s\"></input>"%(Playlist.__name__,self.key.urlsafe())

    def keyForLink(self):
        return "%s=%s"%(Playlist.__name__, self.key.urlsafe())

    @staticmethod
    def getPlaylistFromRequest(request):
        pkey = ndb.Key(urlsafe=request.get(Playlist.__name__))
        return pkey.get()
