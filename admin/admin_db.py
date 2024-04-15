class AdminDatabase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getAllUser(self):
        self.__cur.execute("SELECT * FROM user")

        res = self.__cur.fetchall()
        posts = []
        if res:
            for row in res:
                user = {
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'login': row[3],
                    'psw': row[4],
                    'avatar': row[5] if row[5] else "static/img/default.jpg",
                    'header': row[6] if row[6] else "static/img/default_header.jpg",
                    'instagram': row[7],
                    'telegram': row[8],
                    'facebook': row[9],
                    'tik_tok': row[10],
                    'vk': row[11],
                    'youtube': row[12],
                }
                posts.append(user)
        return posts

    def deleteUser(self, login):
        self.__cur.execute("DELETE FROM user WHERE login = ?", (login,))
        self.__cur.execute("DELETE FROM users_card WHERE login = ?", (login,))
        self.__cur.execute("DELETE FROM posts WHERE login = ?", (login,))
        self.__db.commit()

    def countBeat(self):
        res = self.__cur.execute("SELECT COUNT(*) FROM users_card").fetchone()
        if res:
            return res[0]
        else:
            return False

    def countPosts(self):
        res = self.__cur.execute("SELECT COUNT(*) FROM posts").fetchone()
        if res:
            return res[0]
        else:
            return False

    def countUser(self):
        res = self.__cur.execute("SELECT COUNT(*) FROM user").fetchone()
        if res:
            return res[0]
        else:
            return False

