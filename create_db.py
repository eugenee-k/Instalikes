import pymysql


conn = pymysql.connect(host = 'localhost', user = 'root', passwd = '')

conn.cursor().execute('DROP DATABASE IF EXISTS instalikes')
conn.cursor().execute('CREATE DATABASE IF NOT EXISTS instalikes')

conn.cursor().execute(
    """
    CREATE TABLE instalikes.users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(30) NOT NULL,
        password VARCHAR(100) NOT NULL,
        question VARCHAR(20) NOT NULL,
        answer VARCHAR(300) NOT NULL
    );
    """)

conn.cursor().execute(
    """
    CREATE TABLE instalikes.likes (
        userid INT NOT NULL,
        image1 LONGBLOB NOT NULL,
        image2 LONGBLOB,
        image3 LONGBLOB,
        image4 LONGBLOB,
        image5 LONGBLOB,
        image6 LONGBLOB,
        image7 LONGBLOB,
        image8 LONGBLOB,
        image9 LONGBLOB,
        image10 LONGBLOB,
        user VARCHAR(30) NOT NULL,
        caption VARCHAR(2500) NOT NULL,
        comments TEXT(50000) NOT NULL,
        bkpdate VARCHAR(20) NOT NULL
    );
    """)

conn.cursor().execute(
    """
    CREATE TABLE instalikes.comments (
        userid INT NOT NULL,
        image MEDIUMBLOB NOT NULL,
        comment VARCHAR(5000) NOT NULL
    );
    """)
