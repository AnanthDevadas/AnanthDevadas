Title: Keyword Exporer

Purpose: The purpose of this app is to explore potential research topics one could do. The ideal example would probably be someone who might want to explore possible ideas thinging about pursuing a Research topic with an institue like a PHD student.

Demo: Give the link to your video demo. Read the video demo section below to understand what contents are expected in your demo.
https://mediaspace.illinois.edu/media/t/1_797x48of

Installation: Data is all the same. 
Create Table university_publication ( 
	Primary Key (university_id,publication_id)
    )
Engine =InnoDB 
select  u.id as university_id, p.id as publication_id, u.name as University, p.title as Journal, p.num_citations
from faculty F
    join university u
		on u.id = F.university_id
	join faculty_publication fp
		on F.id = fp.faculty_id
	join publication p
		on p.id = fp.publication_id
group by  u.id,p.id,u.name , p.title;

ALTER TABLE university_publication
ADD CONSTRAINT fk_uni_id FOREIGN KEY (university_id) REFERENCES university(id);

ALTER TABLE university_publication
ADD CONSTRAINT fk_pub_id FOREIGN KEY (publication_id) REFERENCES publication(id);

-- Necessary to store favorite key words. Constraints make sure that it only adds keywords that bring back results
Create table favorite_keywords (
id INT NOT NULL auto_increment,
keyword_id INT NOT NULL,
keyword_name varchar(255) NOT NULL,
PRIMARY KEY (id),
CONSTRAINT uc_keyword UNIQUE (keyword_id),
CONSTRAINT fk_keyword foreign key (keyword_id) references keyword(id)
);

-- stores favorite data
Create table fav_keywords_summary (
id INT NOT NULL auto_increment,
keyword varchar(255) NOT NULL,
faculty varchar(255) NOT NULL,
university varchar(255) NOT NULL,
publication varchar(255) NOT NULL,
PRIMARY KEY (id),
CONSTRAINT uc_sc_keyword UNIQUE (keyword)
);

-- Necessary to store searched key words. Constraints make sure that it only adds keywords that bring back results
Create table searched_keywords (
id INT NOT NULL auto_increment,
keyword_id INT NOT NULL,
keyword_name varchar(255) NOT NULL,
PRIMARY KEY (id),
CONSTRAINT uc_sc_keyword UNIQUE (keyword_id),
CONSTRAINT fk_sc_keyword foreign key (keyword_id) references keyword(id)
);

Create View University_keyword_score as
select University, Journal, name as keyword, score*num_citations  as actual_score
FROM university_publication as up
 join publication_keyword as p 
	on p.publication_id = up.publication_id
join keyword k
	on k.id = p.keyword_id;


Usage: How to use it? 
Its used by entering a keyword, which then autopoulates the rest of the dashboard. Additional function of storing favorite keywords are there.

Design: What is the design of the application? Overall architecture and components. 
The keyword search bar is at the top which is used to the populate the rest of the dashboard. An initial value of "complexity classes" is there when the dashboard starts as an example. This is followed by the search history which saves the last 5 searches that have been done as well as the favorites. 
The favorites section can be broken down by the actual add/delete favorite button + text field, and then a table with the (at most) 5 favorite keywords with top stats for each catagory. There is some inbuilt error processing but nothing that will display on the dashbaord to the user currently. 
This is followed by the trend over years of the keyword to see if research on this topic is considered "relevant" or if this subject is considered more niche/ not as popular. This could help inform how likely research in the topic will be able to get things such as grants or the general appitite for this topic is.
This is then followed by a section of three tables. 
One for Top faculty that research this topic broken down to what university they work at and relevance. This can help users find out what specific faculty to reach out to, either to learn more about the topic or start communications about research.
One for Top Universities for that topic and their most relevant published paper for that research. This can help determine which institutes to apply for when researching a topic, such as a PHD student.
The last is Top papers for that topic. This is more as a general start to look more into the subject as so one can be more well versed in the topic.

Implementation: How did you implement it? What frameworks and libraries or any tools have you used to realize the dashboard and functionalities? 

Python Libraries used:
mysql.connector
pandas
neo4j
pymongo
dash_bootstrap_components
plotly.express
dash

Database Techniques: What database techniques have you implemented? How? 
The constraints technique was used a lot. Part of it was as part of the create table statments using primary key constraint. There were a lot of additional constraints used, such as the foreign key constraints, mainly to the keyword table to make sure that keywords existed before adding them to favorites or search history to keep the DB in a consistent state in SQL. Additionally a unique constraint was also used in favorites and search history tables to make sure that data wasnt entered twice.

The tranasction technique was used as well when it came to updating both the search history and favorites table. This was done by running multiple select and insert statments which were not commited until the end of the transaction. This way, and errors would seemlessly cause the updates to not happen and not leave the DB in an inconsistent state. This was most important in the favorites table, since it required updating two tables before committing the update, with multiple points of errors that could happen along the way.

The view technique was used when trying to link Keywords to Universities. This was done since tbe query required a multiple join statment that could get messy when trying to filter a lot and avoiding multiple nested queries to increase readability of the query should anyone decided to go back and look at the source code.

Extra-Credit Capabilities: What extra-credit capabilities have you developed if any? 
none
Contributions: I was the only person working on the project. 100% effort :)
