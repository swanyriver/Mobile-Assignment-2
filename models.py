from google.appengine.ext import ndb
import sys
import json

# dumps = json.dumps
# def prettyJson(obj):
#     return dumps(obj, indent=2)
# json.dumps = prettyJson


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

    def json(self):
        dict = self.to_dict()
        return json.dumps(dict)

    def _to_dict(self):
        dict = super(Snippet,self)._to_dict()
        dict["Key"] = self.key.id()
        dict["url"] = self.keyForLink()
        dict["json"] = self.jsonLink()
        return dict

    @staticmethod
    def keyForLinkFromKey(key):
        return "/snippet/%s/" % (key.urlsafe())

    @staticmethod
    def jsonLinkfromKey(key):
        return "/snippet/%s.json" % (key.urlsafe())

    def jsonLink(self):
        return Snippet.jsonLinkfromKey(self.key)

    def keyForLink(self):
        return Snippet.keyForLinkFromKey(self.key)

    @classmethod
    def getSnippetFromURL(cls, kwargs):
        if cls.__name__ not in kwargs: return None
        try:
            skey = ndb.Key(urlsafe=kwargs[cls.__name__])
            #print skey
            snpt = skey.get()
            #print snpt
        except:
            print sys.exc_info()[0]
            return None

        return snpt


class Playlist(ndb.Model):
    isPublic = ndb.BooleanProperty(indexed=True, required=True, default=False)
    title = ndb.StringProperty(indexed=False, required=True)
    creator = ndb.StringProperty(indexed=False, required=True)
    snippetKeys = ndb.KeyProperty(kind=Snippet, repeated=True, indexed=False)
    date_added = ndb.DateTimeProperty(auto_now_add=True)

    def _to_dict(self):
        dict = super(Playlist, self)._to_dict()
        dict.pop('date_added')
        dict['Key'] = self.key.id()
        dict['snippetKeys'] = [k.id() for k in dict['snippetKeys']]
        dict['url'] = self.keyForLink()
        dict['json'] = self.jsonLink()
        return dict

    def json(self):
        dict = self.to_dict()
        dict.pop('date_added')
        dict['Key'] = self.key.id()
        dict['snippetKeys'] = [k.id() for k in dict['snippetKeys']]
        dict['snippets'] = [snp._to_dict() for snp in self.snippets]
        return json.dumps(dict)

    @staticmethod
    def keyForLinkFromKey(key):
        return "/playlist/%s/" % (key.urlsafe())

    @staticmethod
    def jsonLinkfromKey(key):
        return "/playlist/%s.json" % (key.urlsafe())

    def jsonLink(self):
        return Playlist.jsonLinkfromKey(self.key)

    def keyForLink(self):
        return Playlist.keyForLinkFromKey(self.key)

    #for html representation
    @staticmethod
    def getAllPublicsForHTML():
        plists = Playlist.query(Playlist.isPublic == True).order(-Playlist.date_added)
        for p in plists: p.snippets = ndb.get_multi(p.snippetKeys)
        return plists


    @classmethod
    def getPlaylistFromURL(cls, kwargs):
        if cls.__name__ not in kwargs: return None
        try:
            pkey = ndb.Key(urlsafe=kwargs[cls.__name__])
            #print pkey
            plist = pkey.get()
            #print plist
        except:
            print sys.exc_info()[0]
            return None

        # todo reconstruct selected thumbnail
        if plist: plist.snippets = ndb.get_multi(plist.snippetKeys)
        return plist

    # def getSnippetsFromPlaylist(self):
    #     return ndb.get_multi(self.snippetKeys)

    @staticmethod
    def createAndStore(kv, user):
        newPlaylist = Playlist(parent = user.key)
        newPlaylist.creator = user.auth_ids[0]
        newPlaylist.title = kv['title']
        newPlaylist.isPublic = "public" in kv
        #print newPlaylist

        return newPlaylist.put()

    @classmethod
    def get_public_playlists(cls):
        return [p._to_dict() for p in cls.query(Playlist.isPublic == True).order(-cls.date_added)]

    @classmethod
    def get_users_playlists(cls, user):
        return [p._to_dict() for p in cls.query(ancestor=user.key).order(-cls.date_added)]

