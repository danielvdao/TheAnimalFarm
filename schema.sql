-- #Main table: Contains all the topics of discussion through titles and texts. 
drop table if exists topics;
create table topics (
  id integer primary key autoincrement,
  title text not null,
  text text not null
);

-- #Comment table: A table which contains a topic id and is linked by a foreign key. Also contains userID which helps to connect anonymous 
-- #posters to all their posts. Table is used to check if user already posted on here so program doesn't give them a new name.
drop table if exists comments; 
create table comments(
  topicid integer, 
  userid integer,
  animal_username text not null,
  comment text not null,  
  time integer,
  FOREIGN KEY(topicid) REFERENCES topics(id)
  FOREIGN KEY(userid) REFERENCES users(id)
);

-- #Main user table: Contains the user sign ins and passwords. Also an ID to identify users when they post comments (hidden from user) 
drop table if exists users;
create table users(
  id integer primary key autoincrement, 
  main_username text not null, 
  password text not null
);
