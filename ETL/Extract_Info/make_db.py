

import mysql
from mysql.connector import Error
import re

def exec_sql_file(cursor, sql_com):
    #print("\n[INFO] Executing SQL script file: '%s'" % (sql_com))
    statement = ""

    for line in sql_com.splitlines():
        if re.match(r'--', line):  # ignore sql comment lines
            continue
        if not re.search(r';$', line):  # keep appending lines that don't end in ';'
            statement = statement + line
        else:  # when you get a line ending in ';' then exec statement and reset for next statement
            statement = statement + line
            #print "\n\n[DEBUG] Executing SQL statement:\n%s" % (statement)
            try:
                cursor.execute(statement)
            except Error as e:
                print("\n[WARN] MySQLError during execute statement \n\tArgs: '%s'" % (str(e.args)))

            statement = ""

def db():
    try:
        conn = mysql.connector.connect(host='127.0.0.1',port = 3307,user='root',database = "explorer_db",password = '')
        if conn.is_connected():
            print("Connection successful: ",conn.get_server_info())
        cur = conn.cursor()
        sql_com = '''
            SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
            SET AUTOCOMMIT = 0;
            START TRANSACTION;
            SET time_zone = "+00:00";
            /*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
            /*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
            /*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
            /*!40101 SET NAMES utf8mb4 */;
            CREATE DATABASE IF NOT EXISTS `explorer_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
            USE `explorer_db`;
            CREATE TABLE `activity_log` (
            `activity_key` int(11) NOT NULL COMMENT 'Key of all the activity history',
            `user_id` int(10) NOT NULL COMMENT 'use key that the activity belongs to',
            `activity_date` date NOT NULL COMMENT 'Date of activity',
            `activity_time` time NOT NULL COMMENT 'Time of activity',
            `event_key` int(30) NOT NULL COMMENT 'Event key that user clicked on',
            `activity_rating` int(5) NOT NULL DEFAULT -1 COMMENT 'Rating of event by user.-1 for not rated [0-5]'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Contains the activity log of users for recommendation system';
            CREATE TABLE `event` (
            `event_key` int(11) NOT NULL COMMENT 'Key value for events',
            `event_title` text DEFAULT NULL COMMENT 'The title of the article',
            `event_text` varchar(10000) DEFAULT NULL COMMENT 'The full size article with link to source',
            `event_year` varchar(20) DEFAULT NULL COMMENT 'Year the event occurred',
            `event_genre` int(10) DEFAULT NULL COMMENT 'Genre of the event from genre table',
            `event_lat` varchar(30) DEFAULT NULL COMMENT 'Latitude of the event ',
            `event_long` varchar(30) DEFAULT NULL COMMENT 'Longitude of the event',
            `event_location` varchar(200) DEFAULT NULL COMMENT 'Location name of the event',
            `url` text NOT NULL COMMENT 'The URL of the given event',
            `html` mediumtext DEFAULT NULL COMMENT 'The html page of the scraped document',
            `error` int(11) DEFAULT NULL COMMENT 'The error received when scraping',
            `old_rank` double DEFAULT NULL COMMENT 'The old pagerank',
            `new_rank` double NOT NULL COMMENT 'The new pagerank based on old_rank',
            `htext` mediumtext DEFAULT NULL COMMENT 'The text extracted from HTML of the document'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Contains the articles and their details';
            CREATE TABLE `event_samples` (
            `event_key` int(11) NOT NULL COMMENT 'Key value for events',
            `event_title` varchar(200) NOT NULL COMMENT 'The title of the article',
            `event_text` varchar(10000) NOT NULL COMMENT 'The full size article with link to source',
            `event_year` varchar(20) NOT NULL COMMENT 'Year the event occurred',
            `event_genre` varchar(100) NOT NULL COMMENT 'Genre of the event',
            `event_lat` varchar(30) NOT NULL COMMENT 'Latitude of the event ',
            `event_long` varchar(30) NOT NULL COMMENT 'Longitude of the event',
            `event_location` varchar(200) NOT NULL COMMENT 'Location name of the event'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Contains the articles and their details';
            CREATE TABLE `flag_log` (
            `flag_key` int(11) NOT NULL COMMENT 'Key for all flags',
            `event_key` int(30) NOT NULL COMMENT 'Foreign key from events.The event that has been flagged',
            `flag_date` date NOT NULL COMMENT 'Date of flag',
            `flag_time` time NOT NULL COMMENT 'Time of flag',
            `flag_description` varchar(200) NOT NULL COMMENT 'Description of flag',
            `user_id` int(10) NOT NULL COMMENT 'user key of the flagger',
            `flag_approved` int(1) NOT NULL DEFAULT 0 COMMENT '0 is not approved. 1 is approved'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Contains the flag details ';
            CREATE TABLE `genre` (
            `genre_id` int(11) NOT NULL COMMENT 'Unique ID for genres',
            `genre_text` varchar(100) NOT NULL COMMENT 'The actual genre '
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Contains genre keys and genre to be used in event table';
            CREATE TABLE `links` (
            `from_id` int(11) NOT NULL COMMENT 'The from_id link pointer',
            `to_id` int(11) NOT NULL COMMENT 'The to_id link pointer'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Contains link pointers for pagerank';
            CREATE TABLE `role` (
            `role_id` int(11) NOT NULL COMMENT 'Primary key, auto incremented',
            `role_name` varchar(100) NOT NULL COMMENT 'short name of the role',
            `role_description` varchar(300) NOT NULL COMMENT 'description  of the privileges of the role'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Contains role identities that are used in user table';
            CREATE TABLE `user` (
            `user_id` int(11) NOT NULL COMMENT 'Primary key of users',
            `user_email` varchar(100) NOT NULL COMMENT 'Email of the user.Unique',
            `user_name` varchar(150) NOT NULL COMMENT 'Name of the user',
            `user_pass` varchar(200) NOT NULL COMMENT 'Password.Salted and Hashed',
            `role_id` int(10) NOT NULL DEFAULT 1 COMMENT 'Foreign key from role table.'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Contains user details.';
            CREATE TABLE `webs` (
            `url` text NOT NULL COMMENT 'THe website to scrape data from. '
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Restricts the website to scrape from';
            ALTER TABLE `activity_log`
            ADD PRIMARY KEY (`activity_key`),
            ADD KEY `user_id` (`user_id`),
            ADD KEY `activity_log_ibfk_1` (`event_key`);
            ALTER TABLE `event`
            ADD PRIMARY KEY (`event_key`),
            ADD UNIQUE KEY `url_2` (`url`) USING HASH,
            ADD KEY `event_ibfk_1` (`event_genre`),
            ADD KEY `url` (`url`(768)) USING HASH;
            ALTER TABLE `event_samples`
            ADD PRIMARY KEY (`event_key`);
            ALTER TABLE `flag_log`
            ADD PRIMARY KEY (`flag_key`),
            ADD KEY `user_id` (`user_id`),
            ADD KEY `flag_log_ibfk_1` (`event_key`);
            ALTER TABLE `genre`
            ADD PRIMARY KEY (`genre_id`),
            ADD UNIQUE KEY `genre_text` (`genre_text`);
            ALTER TABLE `links`
            ADD UNIQUE KEY `from_id` (`from_id`,`to_id`),
            ADD KEY `to_id` (`to_id`);
            ALTER TABLE `role`
            ADD PRIMARY KEY (`role_id`);
            ALTER TABLE `user`
            ADD PRIMARY KEY (`user_id`),
            ADD KEY `user_ibfk_1` (`role_id`);
            ALTER TABLE `webs`
            ADD UNIQUE KEY `url` (`url`) USING HASH;
            ALTER TABLE `activity_log`
            MODIFY `activity_key` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Key of all the activity history';
            ALTER TABLE `event`
            MODIFY `event_key` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Key value for events', AUTO_INCREMENT=114372;
            ALTER TABLE `event_samples`
            MODIFY `event_key` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Key value for events', AUTO_INCREMENT=245;
            ALTER TABLE `flag_log`
            MODIFY `flag_key` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Key for all flags';
            ALTER TABLE `genre`
            MODIFY `genre_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Unique ID for genres', AUTO_INCREMENT=5;
            ALTER TABLE `role`
            MODIFY `role_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key, auto incremented', AUTO_INCREMENT=4;
            ALTER TABLE `user`
            MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key of users';
            ALTER TABLE `activity_log`
            ADD CONSTRAINT `activity_log_ibfk_1` FOREIGN KEY (`event_key`) REFERENCES `event` (`event_key`) ON DELETE CASCADE ON UPDATE CASCADE,
            ADD CONSTRAINT `activity_log_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`);
            ALTER TABLE `event`
            ADD CONSTRAINT `event_ibfk_1` FOREIGN KEY (`event_genre`) REFERENCES `genre` (`genre_id`) ON UPDATE CASCADE;
            ALTER TABLE `flag_log`
            ADD CONSTRAINT `flag_log_ibfk_1` FOREIGN KEY (`event_key`) REFERENCES `event` (`event_key`) ON DELETE CASCADE ON UPDATE CASCADE,
            ADD CONSTRAINT `flag_log_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`);
            ALTER TABLE `links`
            ADD CONSTRAINT `links_ibfk_1` FOREIGN KEY (`from_id`) REFERENCES `event` (`event_key`) ON DELETE CASCADE ON UPDATE CASCADE,
            ADD CONSTRAINT `links_ibfk_2` FOREIGN KEY (`to_id`) REFERENCES `event` (`event_key`) ON DELETE CASCADE ON UPDATE CASCADE;
            ALTER TABLE `user`
            ADD CONSTRAINT `user_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `role` (`role_id`) ON UPDATE CASCADE;
            COMMIT;
            /*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
            /*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
            /*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
            '''
        exec_sql_file(cur,sql_com)
        conn.commit()
        cur.close()
        conn.close()
        conn = mysql.connector.connect(host='127.0.0.1',port = 3307,database = "explorer_db",user='root',password = '')
        if conn.is_connected():
            print("Connection successful: ",conn.get_server_info())
        conn.close()
    except Error as e:
        print("\nError connecting to MySQL\n",e)

db()

