from google.appengine.ext import ndb


class Snippet(ndb.Model):
    title = ndb.StringProperty(indexed=False, required=True)
    notes = ndb.StringProperty(indexed=False, required=False)
    videoID = ndb.StringProperty(indexed=False, required=True)
    startTime = ndb.IntegerProperty(indexed=False, required=True)
    endTime = ndb.IntegerProperty(indexed=False, required=True)
    selectedThumbnail = ndb.IntegerProperty(indexed=False, required=True)

    def toString(self): return str(self.__dict__)


class Playlist(ndb.Model):
    title = ndb.StringProperty(indexed=False, required=True)
    creator = ndb.StringProperty(indexed=False, required=False)
    snippets = ndb.StructuredProperty(Snippet, repeated=True)
    date_added = ndb.DateTimeProperty(auto_now_add=True)

    def toString(self):
        st = str(self.title)
        st += str(self.creator)
        for snip in self.snippets: st += snip.toString() + '\n'
        return st
