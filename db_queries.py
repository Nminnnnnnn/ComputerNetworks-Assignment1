import sqlite3

def get_all_users():
    try:
        cnt = sqlite3.connect('user.db')
        cursor = cnt.execute('''SELECT NAME FROM client;''')
        user_list = []
        for row in cursor:
            user_list.append(row[0])
        cursor.close()
    except sqlite3.Error as error:
        print('Error occured - ', error)
    finally:
        if cnt:
            cnt.close()
        return user_list

def get_user_password(username):
    try:
        cnt = sqlite3.connect('user.db')
        cursor = cnt.execute('''SELECT PASSWORD FROM client WHERE NAME = ?;''', (username,))
        result = []
        for row in cursor:
            result.append(row[0])
        cursor.close()
    except sqlite3.Error as error:
        print('Error occured - ', error)
    finally:
        if cnt:
            cnt.close()
        return str(result[0])

def get_user_path(username):
    path_list = []
    try:
        cnt = sqlite3.connect('user.db')
        cursor = cnt.execute('''SELECT f.FILEPATH FROM client c INNER JOIN file f ON c.ID = f.CLIENT_ID WHERE c.NAME = ?;''', (username,))
        for row in cursor:
            path_list.append(row[0])
        cursor.close()
    except sqlite3.Error as error:
        print('Error occured - ', error)
    finally:
        if cnt:
            cnt.close()
        return path_list

def get_user_file(username):
    file_list = []
    try:
        cnt = sqlite3.connect('user.db')
        cursor = cnt.execute('''SELECT f.NAME FROM client c INNER JOIN file f ON c.ID = f.CLIENT_ID WHERE c.NAME = ?;''', (username,))
        for row in cursor:
            file_list.append(row[0])
        cursor.close()
    except sqlite3.Error as error:
        print('Error occured - ', error)
    finally:
        if cnt:
            cnt.close()
        return file_list

def add_new_user(username, password):
    try:
        cnt = sqlite3.connect('user.db')
        cnt.execute('''INSERT INTO client (NAME,PASSWORD) VALUES(?,?);''', (username,password,))
        cnt.commit()
    except sqlite3.Error as error:
        print('Error occured - ', error)
    finally:
        if cnt:
            cnt.close()

def add_onl_user(username):
    try:
        cnt = sqlite3.connect('user.db')
        cnt.execute('''INSERT INTO online (NAME) VALUES (?);''', (username,))
        cnt.commit()
    except sqlite3.Error as error:
        print('Error occured - ', error)
    finally:
        if cnt:
            cnt.close()

def remove_onl_user(username):
    try:
        cnt = sqlite3.connect('user.db')
        cnt.execute('''DELETE FROM online WHERE NAME = ?;''', (username,))
        cnt.commit()
    except sqlite3.Error as error:
        print('Error occured - ', error)
    finally:
        if cnt:
            cnt.close()

def get_onl_users():
    try:
        cnt = sqlite3.connect('user.db')
        cursor = cnt.execute('''SELECT NAME FROM online;''')
        user_list = []
        for row in cursor:
            user_list.append(row[0])
        cursor.close()
    except sqlite3.Error as error:
        print('Error occured - ', error)
    finally:
        if cnt:
            cnt.close()
        return user_list

def delete_all_onl_users():
    try:
        cnt = sqlite3.connect('user.db')
        cnt.execute('''DELETE FROM online;''')
        cnt.commit()
    except sqlite3.Error as error:
        print('Error occured - ', error)
    finally:
        if cnt:
            cnt.close()

def delete_user(username):
    try:
        cnt = sqlite3.connect('user.db')
        cnt.execute('''DELETE FROM client WHERE NAME = ?;''', (username,))
        cnt.commit()
    except sqlite3.Error as error:
        print('Error occured - ', error)
    finally:
        if cnt:
            cnt.close()

def add_new_file(username, filename, filepath):
    try:
        cnt = sqlite3.connect('user.db')
        cursor = cnt.execute('''SELECT ID FROM client WHERE NAME = ?;''', (username,))
        user_id = cursor.fetchone()
        if user_id:
            user_id = user_id[0]
            cnt.execute('''INSERT INTO file (CLIENT_ID, NAME, FILEPATH) VALUES (?, ?, ?);''', (user_id, filename, filepath))
            cnt.commit()
    except sqlite3.Error as error:
        print('Error occurred - ', error)
    finally:
        if cnt:
            cnt.close()

def delete_file(username, filename):
    try:
        cnt = sqlite3.connect('user.db')
        cursor = cnt.execute('''SELECT ID FROM client WHERE NAME = ?;''', (username,))
        user_id = cursor.fetchone()
        if user_id:
            user_id = user_id[0]
            cnt.execute('''DELETE FROM file WHERE (CLIENT_ID, NAME) = (?, ?);''', (user_id, filename))
            cnt.commit()
    except sqlite3.Error as error:
        print('Error occured - ', error)
    finally:
        if cnt:
            cnt.close()

def search_file_name(filename):
    userlist = []
    try:
        cnt = sqlite3.connect('user.db')
        cursor = cnt.execute('''SELECT c.NAME FROM client c JOIN file s ON c.ID = s.CLIENT_ID WHERE s.NAME = ?;''', (filename,))
        for row in cursor:
            user_list.append(row[0])
        cursor.close()
    except sqlite3.Error as error:
        print('Error occured - ', error)
    finally:
        if cnt:
            cnt.close()
        return user_list

def update_user_password(username, password):
    try:
        cnt = sqlite3.connect('user.db')
        cnt.execute('''UPDATE client SET PASSWORD = ? WHERE NAME = ?;''', (password, username,))
        cnt.commit()
    except sqlite3.Error as error:
        print('Error occured - ', error)
    finally:
        if cnt:
            cnt.close()

def update_user_address_port(username, ipaddress, port):
    try:
        cnt = sqlite3.connect('user.db')
        cnt.execute('''UPDATE client SET IPADDRESS = ?, PORT = ? WHERE NAME = ?;''', (ipaddress, port, username))
        cnt.commit()
    except sqlite3.Error as error:
        print('Error occured - ', error)
    finally:
        if cnt:
            cnt.close()

def get_all_table():
    try:
        cnt = sqlite3.connect('user.db')
        cursor = cnt.execute('''SELECT * FROM client;''')
        user_list = []
        for row in cursor:
            user_list.append(row)
        cursor.close()
    except sqlite3.Error as error:
        print('Error occured - ', error)
    finally:
        if cnt:
            cnt.close()
        print(user_list)

def delete_all_users():
    try:
        cnt = sqlite3.connect('user.db')
        cnt.execute('''DELETE FROM client;''')
        cnt.commit()
    except sqlite3.Error as error:
        print('Error occured - ', error)
    finally:
        if cnt:
            cnt.close()
