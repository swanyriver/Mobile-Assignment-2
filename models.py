from google.appengine.ext import ndb
import sys


def getPopulateDictionary(model_class, request):
    return {k: int(v) if isinstance(getattr(model_class, k), ndb.IntegerProperty) else v for k, v in request if k in model_class._properties }


class Snippet(ndb.Model):
    title = ndb.StringProperty(indexed=False, required=True)
    notes = ndb.StringProperty(indexed=False, required=False)
    videoID = ndb.StringProperty(indexed=False, required=True)
    startTime = ndb.IntegerProperty(indexed=False, required=True)
    endTime = ndb.IntegerProperty(indexed=False, required=True)

    # Used in debugging, GAE makes use of __str__ so toString is used by me
    #def toString(self): return str(self.__dict__)


class Playlist(ndb.Model):
    AnonymousParent = ndb.Key('Playlist', "Anonymous")

    title = ndb.StringProperty(indexed=False, required=True)
    creator = ndb.StringProperty(indexed=False, required=True, default="Anonymous")
    snippetKeys = ndb.KeyProperty(kind=Snippet, repeated=True, indexed=False)
    date_added = ndb.DateTimeProperty(auto_now_add=True)


    # Used in debugging, GAE makes use of __str__ so toString is used by me
    # def toString(self):
    #     st = str(self.title)
    #     st += str(self.creator)
    #     for snip in self.snippets: st += snip.toString() + '\n'
    #     return st

    # todo need to use URLs instead
    # def keyForForm(self):
    #     return "<input type=\"hidden\" name=\"%s\" value=\"%s\"></input>"%(Playlist.__name__, self.key.urlsafe())

    @staticmethod
    def keyForLinkFromKey(key):
        return "/playlist/%s/" % (key.urlsafe())

    def keyForLink(self):
        return Playlist.keyForLinkFromKey(self.key)

    @staticmethod
    def getAll(ancestor=None):
        if ancestor:
            pkey = ndb.Key(Playlist, ancestor)
            pquery = Playlist.query(ancestor=pkey).order(-Playlist.date_added)
            return pquery.fetch()
        #todo test this, homepage, get all
        else:
            return Playlist.query()


    #todo get from url
    @classmethod
    def getPlaylistFromURL(cls, kwargs):
        if cls.__name__ not in kwargs: return None
        try:
            pkey = ndb.Key(urlsafe=kwargs[cls.__name__])
            print pkey
            plist = pkey.get()
            print plist
        except:
            print sys.exc_info()[0]
            return None

        # todo reconstruct selected thumbnail
        plist.snippets = ndb.get_multi(plist.snippetKeys)
        return plist

    # def getSnippetsFromPlaylist(self):
    #     return ndb.get_multi(self.snippetKeys)

    @staticmethod
    def createAndStore(kv):
        newPlaylist = Playlist(parent=ndb.Key(Playlist, kv['creator']))
        newPlaylist.populate(**kv)
        return newPlaylist.put()

