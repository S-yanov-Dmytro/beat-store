from flask import url_for


class UserLogin:
    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user['id'])

    def getName(self):
        return self.__user['name'] if self.__user else "Без имени"

    def getEmail(self):
        return self.__user['email'] if self.__user else False

    def getLogin(self):
        return self.__user['login'] if self.__user else "Без login"

    def getInstagram(self):
        return self.__user['instagram'] if self.__user else "Don't have Instagram"

    def getTelegram(self):
        return self.__user['telegram'] if self.__user else "Don't have Telegram"

    def getFacebook(self):
        return self.__user['facebook'] if self.__user else "Don't have Facebook"

    def getTikTok(self):
        return self.__user['tik_tok'] if self.__user else "Don't have Tik-Tok"

    def getVK(self):
        return self.__user['vk'] if self.__user else "Don't have VK"

    def getYouTube(self):
        return self.__user['youtube'] if self.__user else "Don't have YouTube"

    def getAvatar(self, app):
        img = None
        if not self.__user['avatar']:
            try:
                with app.open_resource(app.root_path + url_for('static', filename='img/default.jpg'), "rb") as f:
                    img = f.read()
            except FileNotFoundError as e:
                print("Не найден аватар по умолчанию: " + str(e))
        else:
            img = self.__user['avatar']

        return img

    def getHeader(self, app):
        img = None
        if not self.__user['header']:
            try:
                with app.open_resource(app.root_path + url_for('static', filename='img/default_header.jpg'), "rb") as f:
                    img = f.read()
            except FileNotFoundError as e:
                print("Не найден аватар по умолчанию: " + str(e))
        else:
            img = self.__user['header']

        return img

    def verifyExt(self, filename):
        ext = filename.rsplit('.', 1)[1]
        if ext == 'png' or 'PNG' or 'jpg' or 'JPG' or 'mp3':
            return True
        return False