import json
import logging

import discord
import pymysql


class LoggerBot(discord.Client):
    def on_socket_raw_send(self, msg):
        self.log_msg(True, msg)

    def on_socket_raw_receive(self, msg):
        self.log_msg(False, msg)

    def log_msg(self, is_send, msg):
        raw = str(msg)
        dr = int(is_send)

        backlog = [('', json.loads(raw))]
        while len(backlog):
            n, e = backlog.pop()
            if type(e) == dict:
                backlog.extend([(k, v) for k, v in e.items()])
            elif type(e) == list:
                backlog.extend([('', v) for v in e])
            elif n in ('session_id', 'token'):
                raw = raw.replace(e, '[REDACTED]')

        m = json.loads(raw)
        if 'op' in m and 'd' in m:

            if 's' in m and 't' in m:
                with connection.cursor() as cursor:
                    sql = ("INSERT INTO message (dir, op, s, t, raw) "
                           "VALUES (%s, %s, %s, %s, %s)")
                    cursor.execute(sql, (dr, m['op'], m['s'], m['t'], raw))
            elif 's' in m:
                with connection.cursor() as cursor:
                    sql = ("INSERT INTO message (dir, op, s, raw) "
                           "VALUES (%s, %s, %s, %s)")
                    cursor.execute(sql, (dr, m['op'], m['s'], raw))
            else:
                with connection.cursor() as cursor:
                    sql = ("INSERT INTO message (dir, op, raw) "
                           "VALUES (%s, %s, %s)")
                    cursor.execute(sql, (dr, m['op'], raw))
        else:
            with connection.cursor() as cursor:
                sql = ("INSERT INTO message (dir, raw) VALUES (%s, %s)")
                cursor.execute(sql, (dr, raw))

        connection.commit()

if __name__ == '__main__':
    global connection
    config = eval(open('config').read())
    logging.basicConfig(level=logging.INFO)
    connection = pymysql.connect(host=config['db_host'],
                                 user=config['db_user'],
                                 password=config['db_password'],
                                 db=config['db_schema'],
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    bot = LoggerBot()
    bot.login(config['bot_user'], config['bot_password'])
    bot.run()
