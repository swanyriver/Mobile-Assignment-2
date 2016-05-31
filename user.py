import webapp2
from webapp2_extras import auth
import json


def jsonMsg(response,msg):
    response.write(json.dumps({"msg": msg}) + '\n')


class RegHandler(webapp2.RequestHandler):
    def post(self):
        print self.request.POST

        name = self.request.POST.get('name')
        passw = self.request.POST.get('password')

        if not name or not passw:
            jsonMsg(self.response, 'Missing Required Field')
            self.response.set_status(400, "Missing required field")
            return

        success, user = auth.get_auth().store.user_model.create_user(name, password_raw=passw)

        if not success:
            prefix='Unable to create that user:'

            if 'auth_id' in user:
                jsonMsg(self.response, prefix + " Username Already Taken")
                self.response.set_status(400)
            else:
                jsonMsg(self.response, prefix + " Server Error")
                self.response.set_status(500)
            return

        else:
            print user
            self.response.write(
                json.dumps({"msg": "User Created",
                            'username': name,
                            'userid': user.key.id(),
                            'token': user.create_auth_token(user.key.id())}
                           ))
            self.response.write("\n")
            self.response.set_status(200)
            return


class LogHandler(webapp2.RequestHandler):
    def post(self):
        #print self.request.POST

        name = self.request.POST.get('name')
        passw = self.request.POST.get('password')

        if not name or not passw:
            jsonMsg(self.response, 'Missing required field')
            self.response.set_status(400, "Missing required field")
            return

        try:
            #user = auth.get_auth().get_user_by_password(name, passw, save_session=False)
            user = auth.get_auth().store.user_model.get_by_auth_password(name, passw)
        except auth.InvalidPasswordError:
            jsonMsg(self.response, "Invalid Password")
            self.response.set_status(401)
            return
        except auth.InvalidAuthIdError:
            jsonMsg(self.response, "User Does Not Exist")
            self.response.set_status(401)
            return

        if not user:
            jsonMsg(self.response, "Login Failed")
            self.response.set_status(500)
            return
        else:
            #print user
            self.response.write(
                json.dumps({"msg": "User Logged In",
                            'username': name,
                            'userid': user.key.id(),
                            'token': user.create_auth_token(user.key.id())}
                           ))
            self.response.write("\n")
            self.response.set_status(200)
            return

def validate_user(request):
    #print request.POST
    print request.headers

    id = request.headers.get('id')
    token = request.headers.get('token')

    if not id or not token:
        print 'TOKEN AUTH ERROR: Missing required field'
        return None
    if not id.isdigit():
        print 'TOKEN AUTH ERROR: ID must be numeric'
        return None
    user, timestamp = auth.get_auth().store.user_model.get_by_auth_token(int(id), token)
    print "TOKEN RETRIEVED:", user
    return user
