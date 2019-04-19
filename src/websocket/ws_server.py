import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.options

class WSServer(tornado.web.Application):
    is_closing = False

    def signal_handler(self, signum, frame):
        print('exiting...')
        self.is_closing = True

    def try_exit(self):
        if self.is_closing:
            # clean up here
            tornado.ioloop.IOLoop.instance().stop()
            print('exit success')