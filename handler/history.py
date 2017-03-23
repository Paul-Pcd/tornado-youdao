import tornado.web
import tornado.gen
from .base import BaseHandler

'''
 #
 #
 # HistoryHandler
 #
 # BaseHandler来自./base.py文件
 #
 #
'''

class HistoryHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, hash_id):
        '''
        #redis get id
        '''
        if hash_id:
            sessid = self.get_secure_cookie('sessid').decode()
            uid = self.redis_object().get(sessid).decode()
            um = self.user_model()
            nt = self.note_model()
            nid = nt.clear_hash(hash_id)

            ifHas = um.has_this_note(uid, nid)

            note = yield tornado.gen.Task(nt.get_note, nid)
            diff = yield tornado.gen.Task(nt.fetch_diff, nid)

            print(diff)

            if ifHas is True:
                self.render('history.html', diff=diff, note=note)
            else:
                self.redirect('/home/', permanent=False)
        else:
            self.redirect('/home/', permanent=False)

