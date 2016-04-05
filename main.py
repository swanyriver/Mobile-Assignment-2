#!/usr/bin/env python

###############################################
# youtube frame################3
## <iframe width="560" height="315" src="https://www.youtube.com/embed/XTTu0k1H2JI?start=30&amp;end=55&amp;version=3" frameborder="0"></iframe>

# youtube thumbnail 0 is large, 1-3 small
#http://img.youtube.com/vi/<insert-youtube-video-id-here>/[0-3].jpg

# dectect if valid video id
# https://www.googleapis.com/youtube/v3/videos?id=<videoID>&key=<API_KEY>&part=id
####################################################


from credentials import API_KEY
import webapp2
import handler
import models

class MainHandler(handler.handler):
    def get(self):
        #self.render("main.html")
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(self.request.GET)
        self.response.write('\n')
        self.response.write(self.request.get_all("what"))
        self.response.write(models.Snippet._properties.keys())

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
