import sqlite3

import pub_config as pc
import network.config as config
from network.util import *


"""Return: [(uid, uname, gid, text, timesteamp, msgid), ... ]"""


class Recorder:
    def __init__(self):
        self.conn = sqlite3.connect(config.DB_NAME)
        self._insert_cmd = "insert into record (uid, uname, gid, text, timestamp, msgid) values (?,?,?,?,?,?)"
        self._show_tables_cmd = "select * from sqlite_master"
        self._create_cmd = "create table record (uid char(64), uname char(128), gid char(64), text char(10240), " \
                           "timestamp char(64), msgid char(64), primary key(uid, gid, msgid, timestamp))"
        self._select_id_cmd = "select * from record where gid is ? AND msgid between ? and ?"
        self._select_time_cmd = "select * from record where gid is ? AND timestamp between ? and ?"

        self._create_db()

    def _create_db(self):
        tables = self.conn.execute(self._show_tables_cmd).fetchall()
        if not any([t[1] == 'record' for t in tables]):
            dprint("re-creation")
            self.conn.execute("drop table if exists record;")
            self.conn.commit()
            self.conn.execute(self._create_cmd)
            self.conn.commit()

    @exception_log
    def add_history(self, user_id, user_name, group_id, text, timestamp, msg_id):
        try:
            self.conn.execute(self._insert_cmd, (user_id, user_name, group_id, text, timestamp, msg_id))
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            log_str = "Integrity check failed\n" + str(e)
            logging.warning(log_str)
            dprint(log_str)
            return False

    @exception_log
    def fetch_history_id(self, group_id, msg_id_a, msg_id_b):
        l = self.conn.execute(self._select_id_cmd, (group_id, msg_id_a, msg_id_b)).fetchall()
        return l

    @exception_log
    def fetch_history_time(self, group_id, timestamp_a, timestamp_b):
        l = self.conn.execute(self._select_time_cmd, (group_id, timestamp_a, timestamp_b)).fetchall()
        return l

    @exception_log
    def fetch_all(self):
        l = self.conn.execute("select * from record").fetchall()
        return l

        # sqlite3.OperationalError: no such table / table already exists
        # sqlite3.ProgrammingError: Cannot operate on a closed database.


if __name__ == "__main__":
    r = Recorder()
    # r.add_history(1,2,3,4,5,6)
    l = r.fetch_history_id(3, -5, 8)
    print(l)
    print(r.fetch_all())
