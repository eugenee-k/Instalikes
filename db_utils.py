from datetime import datetime
import pymysql


db_config = {
    'host': 'localhost',
    'user': 'root'
}
conn = pymysql.connect(**db_config)


def add_like(userid, ims, user, caption, comments):
    cursor = conn.cursor()
    sql = """INSERT INTO instalikes.likes (userid, image1, image2, image3, image4, image5, image6, image7, 
                                            image8, image9, image10, user, caption, comments, bkpdate)
                                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    cursor.execute(sql, (userid, ims[0], ims[1], ims[2], ims[3], ims[4], ims[5], ims[6], 
        ims[7], ims[8], ims[9], user, caption, comments, datetime.now().strftime("%Y-%m-%d  %H:%M")))
    conn.commit()

    cursor.close()


def add_comment(userid, image, comment):
    cursor = conn.cursor()
    sql = """INSERT INTO instalikes.comments (userid, image, comment)
                                      VALUES (%s, %s, %s)"""
    cursor.execute(sql, (userid, image, comment))
    conn.commit()

    cursor.close()


def get_all_likes():
    cursor = conn.cursor()
    cursor.execute(
        """SELECT userid, user, caption, comments, bkpdate, 
                TO_BASE64(image1) AS encoded_image, 
                TO_BASE64(image2) AS encoded_image, 
                TO_BASE64(image3) AS encoded_image, 
                TO_BASE64(image4) AS encoded_image, 
                TO_BASE64(image5) AS encoded_image, 
                TO_BASE64(image6) AS encoded_image, 
                TO_BASE64(image7) AS encoded_image, 
                TO_BASE64(image8) AS encoded_image, 
                TO_BASE64(image9) AS encoded_image, 
                TO_BASE64(image10) AS encoded_image
           FROM instalikes.likes""")

    all_likes = list(cursor.fetchall())
    all_likes.reverse()
    cursor.close()

    return all_likes


def get_all_comments():
    cursor = conn.cursor()
    cursor.execute(
        "SELECT userid, comment, TO_BASE64(image) AS encoded_image FROM instalikes.comments")

    allcomments = cursor.fetchall()
    all_comments = []

    for i in allcomments:
        x = [i[0]]
        userName = i[1].split('\n')[0].split(' ')[0]
        caption = i[1].split('\n')[0].split(userName)[1]
        myUserName = i[1].split('\n')[2].split(' ')[0]
        comment = i[1].split('\n')[2].split(myUserName)[1]
        
        x.append(userName)
        x.append(caption)
        x.append(myUserName)
        x.append(comment)
        x.append(i[2])
        all_comments.append(x)

    cursor.close()
    all_comments.reverse()

    return all_comments


def get_user(username):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM instalikes.users WHERE username=%s", (username,))
    user = cursor.fetchone()
    cursor.close()

    return user
