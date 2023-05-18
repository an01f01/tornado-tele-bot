import os
import json
import asyncio
import tornado.httpserver
import tornado.options
import tornado.ioloop
import tornado.web
import tornado.wsgi

from tornado import gen, web, template

import requests
import telegram

BOT_TOKEN = os.environ['TELE_BOT']
BOT_URL = os.environ['TELE_BOT_URL']
bot = telegram.Bot(token=BOT_TOKEN)

tornado.options.define('port', default='8000', help='REST API Port', type=int)

def tel_parse_message(message):
    print("message-->",message)
    try:
        chat_id = message['message']['chat']['id']
        txt = message['message']['text']
        print("chat_id-->", chat_id)
        print("txt-->", txt)
        return chat_id,txt
    except:
        print("NO text found-->>")
 
def tel_send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    r = requests.post(url,json=payload)
    return r

class BaseHandler(tornado.web.RequestHandler):
    """
    Base handler gonna to be used instead of RequestHandler
    """
    def write_error(self, status_code, **kwargs):
        if status_code in [403, 404, 500, 503]:
            self.write('Error %s' % status_code)
        else:
            self.write('BOOM!')

class ErrorHandler(tornado.web.ErrorHandler, BaseHandler):
    """
    Default handler gonna to be used in case of 404 error
    """
    pass

class WebhookHandler(BaseHandler):
    """
    GET handler for fetching numbers from database
    """
    @gen.coroutine
    def get(self):
        s = bot.setWebhook(f'{0}{1}'.format(BOT_URL, BOT_TOKEN))
        if s:
            self.set_status(200)
            self.finish({'message': 'Webhook setup OK!'})
        else:
            self.set_status(400)
            self.finish({'message': 'Webhook setup failed :/'})

class BotHandler(BaseHandler):
    """
    GET handler for fetching numbers from database
    """
    @gen.coroutine
    def get(self):
        self.set_status(200)
        self.write({'message': 'Bot is A-OK'})
        self.finish()
    """
    POST handler for telegram message in json
    """
    @gen.coroutine
    def post(self, **params):
        msg         = self.request.body.decode('utf-8')
        bot_json    = tornado.escape.json_decode(msg)
        try:
            chat_id, txt = tel_parse_message(bot_json)
            if txt == "hi":
                tel_send_message(chat_id,"Hello, world!")
            else:
                tel_send_message(chat_id, 'from webhook')
        except:
            print("from index-->")

        self.set_status(200)
        self.finish('Ok')

def make_app():
    settings = dict(
        cookie_secret=str(os.urandom(45)),
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        default_handler_class=ErrorHandler,
        default_handler_args=dict(status_code=404)
    )
    return tornado.web.Application([
        (r"/", BotHandler),
        (r"/(?P<token>[^\/]+)", BotHandler),
        (r"/bot/setwebhook", WebhookHandler),
        ], **settings)

async def main():
    print("starting tornado server..........")
    app = make_app()
    app.listen(tornado.options.options.port)
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())