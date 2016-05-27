from subprocess import check_output
import json

#root = "http://swansonbfinalproject.appspot.com"
#root = "http://swansonbassign4.appspot.com"
root = "http://127.0.0.1:8080"

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
    ],
    [
        {
            "title":"Wythecombe",
            "videoID":"Z4Mfx59GA6I",
            "startTime":72,
            "endTime":90,
            "notes": "When I started my first degree this building was still boarded up"
        },
        {
            "title":"OMG Goats",
            "videoID":"Z4Mfx59GA6I",
            "startTime":178,
            "endTime":182
        },
        {
            "title":"KBVR-FM production studio",
            "videoID":"FHKNBl1RxZc",
            "startTime":236,
            "endTime":250,
            "notes": "I used to work here, with that guy"
        },
        {
            "title":"This is the only building shown in the brochure",
            "videoID":"5NZikvFrfEM",
            "startTime":14,
            "endTime":15,
            "notes": "Aint that the truth, It's just a dorm"
        }
    ]

]


testPlaylists = [
    {"title":"Lookouts"},
    {"title": "Super Truck", "public":None},
    {"title": "Computerphile", "public":None},
    {"title": "OSU Tour"}
]

# users = [
#     {"name":"Brandon", "password":"bpass", "playlists": testPlaylists[:2]},
#     {"name":"JackABoy", "password":"jpass", "playlists": testPlaylists[2:]}
# ]
class user:
    def __init__(self):
        pass

jack = user()
jack.name = {"name":"JackABoy", "password":"jpass"}
jack.playlists = zip(testPlaylists[:2], snippets[:2])

brandon = user()
brandon.name = {"name":"Brandon", "password":"bpass"}
brandon.playlists = zip(testPlaylists[2:], snippets[2:])
users = [jack, brandon]

def sendCurl(st, data=None, headers=None):

    if data:
        data = ["--data", "\"%s\""%"&".join("%s=%s"%(k,v) for k,v in data.items())]
    else:
        data = []

    headArray = []
    if headers:
        for k,v in headers.items():
            headArray.append("-H \"%s:%s\""%(k,v))


    args = ["curl"] + headArray + data + st.split(' ')
    print "SENDING CURL CALL: ", " ".join(args)
    return check_output(' '.join(args), shell=True)

#########SIGN UP USERS#########


#######GET all current playlists#############
print "Retrieving all existing playlists"
res = check_output(["curl", "%s/playlist.json"%root])
print res
playlists = [p['url'] for p in json.loads(res)]
print playlists

##create users###
for u in users:
    res = sendCurl("-X POST %s%s"%(root, "/register"), data=u.name)
    print res
    res = json.loads(res)
    #print res.has_key("token") or in works
    if "token" in res and "userid" in res:
        u.tokenDir={"id":res["userid"], "token":res["token"]}
    else:
        res = sendCurl("-X POST %s%s" % (root, "/login"), data=u.name)
        print res
        res = json.loads(res)
        if "token" not in res or "userid" not in res:
            print "CRITICAL FAILURE, user not able to reg or log in"
            exit()
        u.tokenDir={"id":res["userid"], "token":res["token"]}


#create playlists
for u in users:
    for p,snpts in u.playlists:
        res = sendCurl("-X POST %s"%root, data=p, headers=u.tokenDir)
        print res
        p.update(json.loads(res))
        #res = json.loads(res)
        # purl = res['url']
        # pjson = res['json']


        # for s in snpts:
        #     res = sendCurl("-X POST %s%s" % (root, purl), data=s)

        #check playlist  #far too verbose
        # print "Retrieveing %s playlist <%s> without auth"%("PUBLIC" if "public" in p else "", p["title"])
        # res = sendCurl("%s%s"%(root, pjson))
        # print res
        # # res = sendCurl("%s%s"%(root,purl))
        # # print res
        #
        # print "Retrieveing %s playlist <%s> with auth" % ("PUBLIC" if "public" in p else "", p["title"])
        # res = sendCurl("%s%s" % (root, pjson), headers=u.tokenDir)
        # print res
        # # res = sendCurl("%s%s" % (root, purl), headers=u.tokenDir)
        # # print res

#check public playlists
public_playlists = sendCurl(root + "/playlist.json")
print "PUBLIC PLAYLISTS"
print public_playlists
check_output('google-chrome ' + root, shell=True)



#test public/private GET of playlist HTML/JSON
print "JACKS PlAYLISTS"
print sendCurl(root + "/playlist.json", headers=jack.tokenDir)
for p,snpts in jack.playlists:
    check_output('google-chrome ' + root + p['url'], shell=True)
    if "public" in p:
        print "retrieve public playlist json without auth"
        print sendCurl("%s%s"%(root, p['json']))
    else:
        print "retrieve PRIVATE playlist json without auth"
        print sendCurl("%s%s" % (root, p['json']))

        print "retrieve PRIVATE playlist json with wrong auth"
        print sendCurl("%s%s" % (root, p['json']), headers=brandon.tokenDir)

        print "retrieve PRIVATE playlist json with auth"
        print sendCurl("%s%s" % (root, p['json']), headers=jack.tokenDir)







# print "Deleting all existing playlists and snippets"
#
# for p in playlists:
#     #res = check_output(["curl", "-X DELETE \"%s%s\""%(root,p)])
#     res = sendCurl("-X DELETE %s%s" % (root, p))
#     print res

# print "checking that all existing playlists were deleted"
# res = check_output(["curl", "%s/playlist.json"%root])
# print res
#
# print "Creating Test data"
# print "create 3 playlists and after creating each one create and associate snippets"
# for p,snps in zip(testPlaylists, snippets):
#     print p,snps
#     res = sendCurl("-X POST %s"%root, data=p)
#     print res
#     res = json.loads(res)
#     purl = res['url']
#     print "adding snippets"
#     for s in snps:
#         res = sendCurl("-X POST %s%s"%(root,purl), data=s)
#         print res
#
#
# print "Retrieving all existing playlists"
# res = check_output(["curl", "%s/playlist.json"%root])
# print res
# playlist = [p['json'] for p in json.loads(res)][0]


