import sqlite3
from sqlite3 import Error


class InstaDbService:
    """This service provide all logic for work with db."""

    def __init__(self):
        """Init connection and try create table if not exists"""
        self.database_name = "ourdbserver.db"

        self.conn = self.create_connection()
        if self.conn is not None:
            self.create_table()
        else:
            print("Error! cannot create the database connection.")

    def create_connection(self):
        """Create a database connection to the SQLite database
                specified by self.database_name

        :return: Connection object or None
        """

        try:
            conn = sqlite3.connect(self.database_name)
            return conn
        except Error as e:
            print(e)

        return None

    def create_table(self):
        """Create a table for project if it not exists."""
        sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS saved_posts (
                                                    id integer PRIMARY KEY,
                                                    insta_url text NOT NULL UNIQUE,
                                                    dropbox_id text,
                                                    owner_url text,
                                                    owner_name text,
                                                    posted_at text
                                                ); """
        try:
            c = self.conn.cursor()
            c.execute(sql_create_projects_table)
        except Error as e:
            print(e)

    def add_new_saved_post(self, row_data):
        """Insert new row if not exists

        :param row_data -> str insta_url (permalink on post).
        """

        sql = """ INSERT OR IGNORE INTO saved_posts(insta_url) VALUES(?);"""
        c = self.conn.cursor()

        c.execute(sql, (row_data,))
        self.conn.commit()

    def get_urls_for_parse_info(self):
        """Get all unparsed urls

        :return list with rows
        """

        sql = """ SELECT * FROM saved_posts WHERE dropbox_id IS NULL;"""
        c = self.conn.cursor()
        rows = c.execute(sql)
        return rows

    def update_post_row(self, data):
        """Update post row

        :param data -> tuple (dropbox_id, owner_url, owner_name, id)
        """

        sql = ''' UPDATE saved_posts
                  SET dropbox_id = ? ,
                      owner_url = ? ,
                      owner_name = ?
                  WHERE id = ?'''

        c = self.conn.cursor()
        c.execute(sql, data)
        self.conn.commit()

    def get_unposted_posts(self):
        """Get all unposted post.

        :return list with rows
        """

        sql = """SELECT * FROM saved_posts WHERE dropbox_id IS NOT NULL AND posted_at IS NULL;"""
        c = self.conn.cursor()
        rows = c.execute(sql)
        return rows

    def mark_as_posted(self, post_id):
        """Mark post as posted in DB"""

        sql = """UPDATE saved_posts SET posted_at = datetime('now') WHERE id = ?;"""
        c = self.conn.cursor()
        c.execute(sql, (post_id,))
        self.conn.commit()
