from subprocess import check_output
import json

root = "http://swansonbassign4.appspot.com"
#root = "http://127.0.0.1:8080"

snippets = [
    [
        {
            "title":"hertz1",
            "notes":"check this out",
            "videoID":"ByQD6tAE2yU",
            "startTime":0,
            "endTime":15
        },
        {
            "title":"heartz2",
            "videoID":"ByQD6tAE2yU",
            "startTime":30,
            "endTime":55
        },
        {
            "title":"ute",
            "notes":"here is a different lookout",
            "videoID":"YLZoPcGKq7M",
            "startTime":65,
            "endTime":120
        }
    ],
    [
        {
            "title":"top of the morning",
            "videoID":"TLBIufF7G1I",
            "startTime":0,
            "endTime":5
        },
        {
            "title":"jack truck",
            "notes":"super truck super truck super truck super truck",
            "videoID":"TLBIufF7G1I",
            "startTime":20,
            "endTime":400
        },
        {
            "title":"punch the like button",
            "notes":"<Like a Boss!!!!>",
            "videoID":"TLBIufF7G1I",
            "startTime":882,
            "endTime":887
        }
    ],
    [
        {
            "title":"short computerphile",
            "videoID":"vrjAIBgxm_w",
            "startTime":20,
            "endTime":21
        }
    ]

]
testPlaylists = [
    {"title":"Playlist A", "creator":"a@mail.com"},
    {"title": "Playlist B"},
    {"title": "Playlist C", "creator": "a@mail.com"},
]

def sendCurl(st, data=None):

    if data:
        data = ["--data", "\"%s\""%"&".join("%s=%s"%(k,v) for k,v in data.items())]
    else:
        data = []

    args = ["curl"] + data + st.split(' ')
    print "SENDING CURL CALL: ", " ".join(args)
    return  check_output(' '.join(args), shell=True)

#######GET all current playlists#############
print "Retrieving all existing playlists"
res = check_output(["curl", "%s/playlist.json"%root])
print res
playlists = [p['url'] for p in json.loads(res)]
print "Deleting all existing playlists and snippets"

for p in playlists:
    #res = check_output(["curl", "-X DELETE \"%s%s\""%(root,p)])
    res = sendCurl("-X DELETE %s%s" % (root, p))
    print res

print "checking that all existing playlists were deleted"
res = check_output(["curl", "%s/playlist.json"%root])
print res

print "Creating Test data"
print "create 3 playlists and after creating each one create and associate snippets"
for p,snps in zip(testPlaylists, snippets):
    print p,snps
    res = sendCurl("-X POST %s"%root, data=p)
    print res
    res = json.loads(res)
    purl = res['url']
    print "adding snippets"
    for s in snps:
        res = sendCurl("-X POST %s%s"%(root,purl), data=s)
        print res


print "Retrieving all existing playlists"
res = check_output(["curl", "%s/playlist.json"%root])
print res
playlist = [p['json'] for p in json.loads(res)][0]

print "getting json of one snippet"
res = sendCurl("%s%s"%(root,playlist))
print res

print  "updating values of a snippet"
res = json.loads(res)
snpturl = res['snippets'][0]['url']

print snpturl

res = sendCurl("-X PUT %s%s"%(root,snpturl),data={"title":"new title","startTime":40})
print res

