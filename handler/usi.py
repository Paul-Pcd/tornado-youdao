import tornado.web
import tornado.websocket
from .base import BaseHandler
import json
import random
import re


class UsiHandler(BaseHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')


'''
 # @ UsiSignupHandler
'''
class UsiSignupHandler(UsiHandler):
    def post(self):
        name = self.get_argument("name", None)
        email = self.get_argument("email", None)
        password = self.get_argument("password", None)

        if name and email and password:
            um = self.user_model()

            bool = um.sign_up_object(name, email, password)
            if bool:
                return self.write(json.dumps({'code': 200, 'msg': 'ok', 'data': {}}))
            else:
                return self.write(json.dumps({'code': 1, 'msg': 'not unique', 'data': {}}))

        else:
            return self.write(json.dumps({'code': 2, 'msg': 'bad form', 'data': {}}))



'''
 # @ UsiLoginHandler
'''
class UsiLoginHandler(UsiHandler):
    def post(self):
        name = self.get_argument("name", None)
        password = self.get_argument("password", None)

        if name and password:
            um = self.user_model()
            user = um.valid_user(name, password)
            if user:
                nickname = user['name']
                redis_hash_id = str(user['id']) + random.choice('OA_2954@3S#1cWA')
                self.set_secure_cookie('sessid', redis_hash_id, expires_days=1)
                self.set_secure_cookie('nick', '{nickname}'.format(nickname=nickname), expires_days=1)
                return self.write(json.dumps({'code': 200, 'msg': 'ok', 'data': user}))

            else:
                return self.write(json.dumps({'code': 1, 'msg': 'not valid', 'data': {}}))
        else:
            return self.write(json.dumps({'code': 2, 'msg': 'bad form', 'data': {}}))



'''
 # @ UsiLoginHandler
'''
class UsiLogoutHandler(UsiHandler):
    def post(self):
        self.clear_cookie('sessid')
        self.clear_cookie('nick')
        return self.write(json.dumps({'code': 200, 'msg': 'ok', 'data': {}}))



'''
 # @ UsiGetNoteListHandler
'''
class UsiGetNoteListHandler(UsiHandler):
    def get(self):
        #redis get id
        sessid = self.get_secure_cookie('sessid').decode()
        id = sessid
        if id:
            um = self.user_model()
            note_list = um.get_user_note_list(id)
            return self.write(json.dumps({'code': 200, 'msg': 'ok', 'data': note_list}))
