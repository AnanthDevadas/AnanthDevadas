from pymongo import MongoClient
from pandas import DataFrame
from neo4j import GraphDatabase
import pandas as pd
import mysql.connector

#MongoDB
CONNECTION_STRING = "mongodb://localhost:27017/"

##neo4j
URI = 'bolt://localhost'
password = 'ilovecs411'
DBName = 'fridaynight'
DBMS = 'CS411'
Username = "neo4j"
database="academicworld"

#MySQL
user = "root"
pas = "test_root"
host='127.0.0.1'


##connections class##
class connections:

    ##starts all connections to all DBs ##
    def __init__(self):
        AUTH = (Username, password)
        self.driver = GraphDatabase.driver(URI, auth=AUTH) #neo4j
        self.client = MongoClient(CONNECTION_STRING) #mongodb
        self.cnx = mysql.connector.connect(user=user, password=pas, host='127.0.0.1', database = database)  #mySQL
        self.cnx2 = mysql.connector.connect(user=user, password=pas, host='127.0.0.1', database = database)
        self.cnx4 = mysql.connector.connect(user=user, password=pas, host='127.0.0.1', database = database)

    ##mongo keyword by year##
    def keyword_by_year_mgo(self,keyword = 'complexity classes'):
        keyword = keyword.lower()
        pipeline = [
                { '$unwind': { 'path': '$keywords' } },
                {
                  '$match': {
                    'keywords.name': keyword
                  }
                },
                {
                  '$group': {
                    '_id': '$year',
                    'count': { '$sum': 1 }
                  }
                },
                { '$sort': { '_id': 1 } }
              ]
            

        details = self.client["academicworld"]['publications'].aggregate(pipeline)

        items = DataFrame(details)

        return (items)

    #### top 5 faculty that have research interests with keyword ordered by score Neo4j####
    def relevant_faculty_neo4j(self,keyword = 'complexity classes'):
        keyword = keyword.lower()
        query = """Match (word:KEYWORD)-[i:INTERESTED_IN]-(f:FACULTY)-[a:AFFILIATION_WITH]-(u:INSTITUTE)
        WHERE word.name= '{}' 
        Return f.name as professor_name, u.name as university_name, i.score as score
        ORDER BY score DESC
        LIMIT 5""".format(keyword,keyword)
        result = self.driver.execute_query(query,
                                     database_ = database).records
        return DataFrame(result)

    # #### top 5 universities that have research interests with keyword ordered by score Neo4j####
    # def relevant_uni_neo4j(self,keyword = 'complexity classes'):
    #     query = """Match (i:INSTITUTE)-[:AFFILIATION_WITH]-(f:FACULTY)-[ii:INTERESTED_IN]-(k:KEYWORD)
    #     WHERE  k.name = '{}'
    #     Return i.name, sum(ii.score) as score
    #     ORDER BY score DESC
    #     LIMIT 5""".format(keyword)
    #     result = self.driver.execute_query(query,
    #                                  database_ = database).records
        # return DataFrame(result)

    #### top 5 publications with keywords based on citation*score Neo4j####
    def relevant_publications_neo4j(self,keyword = 'complexity classes'):
        keyword = keyword.lower()
        query = """Match (pub:PUBLICATION)-[l:LABEL_BY]-(k:KEYWORD)
        WHERE  k.name = '{}'
        Return pub.title,pub.venue as venue, l.score*pub.numCitations as score
        ORDER BY score DESC
        LIMIT 5""".format(keyword)
        result = self.driver.execute_query(query,
                                     database_ = database).records
        return DataFrame(result)            
 
 #### top 5 universities that released the highest aggregate citation*score based on keyword #####
    def relevant_uni_mySQL(self, keyword = 'complexity classes'):
        keyword = keyword.lower()
        cursor = self.cnx2.cursor()
        query= """select A.university, Journal, max(B.actual_score)
            From (
                select University, sum(actual_score) as actual_score, max(actual_score) as m_score
                from University_keyword_score
                where keyword = '{}'
                group by University,keyword
                ORDER BY sum(actual_score) DESC
                LIMIT 5
            ) as A 
            join University_keyword_score as B 
                on A.University = B.University and m_score = B.actual_score
            where B.keyword = '{}'
            GROUP BY A.university, B.Journal
            Order by A.actual_score DESC""".format(keyword,keyword)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return(DataFrame(result))

    ###saves searched keywords to table (limit of 5) -> deletes the oldest one ###
    def add_searched_word_mySQL(self, keyword="complexity classes"):
        word = keyword.lower()
        cursor = self.cnx.cursor()
        cursor.execute("""select min(id) from keyword where name = '{}';""".format(word))
        result = cursor.fetchall()
        if result is None:
            cursor.execute("select keyword_name from searched_keywords")
            result = DataFrame(cursor.fetchall())
            cursor.close()
            return(result)
        try:
            cursor.execute("insert into searched_keywords (keyword_id, keyword_name) Values ({},'{}')".format(result[0][0],word))
            cursor.execute("select count(*) from searched_keywords")
            result = cursor.fetchall()
            if result[0][0] >5:
                cursor.execute("select min(id) from searched_keywords")
                result = cursor.fetchall()
                cursor.execute("delete from searched_keywords where id = {}".format(result[0][0]))
            self.cnx.commit()
            cursor.execute("select keyword_name from searched_keywords")
            result = DataFrame(cursor.fetchall())
            cursor.close()
            return(result)
        except:
            cursor.execute("select keyword_name from searched_keywords")
            result = DataFrame(cursor.fetchall())
            cursor.close()
            return(result)


    ### adds favorite keywords ###
    def add_favorite_word_mySQL(self, keyword):
        keyword = keyword.lower()
        cursor = self.cnx4.cursor()
        cursor.execute("select min(id) from keyword where name = '{}'".format(keyword))
        result = cursor.fetchall()[0][0]
        if result is None:
            # print("Not valid keyword")
            return("Not valid keyword")
        try:
            cursor.execute("insert into favorite_keywords (keyword_id, keyword_name) Values ({},'{}')".format(result,keyword))
            cursor.execute("select count(*) from favorite_keywords")
            result = cursor.fetchall()
            if result[0][0] >5:
                raise ValueError("Too many keywords in use") 

            cursor.execute("""select f.name
                from faculty f
                    join Faculty_keyword fk
                        on f.id = fk.faculty_id
                    join keyword k
                        on k.id = fk.keyword_id
                where k.name = "{}"
                group by f.name
                order by  sum(fk.score) DESC
                limit 1""".format(keyword))
            top_faculty = cursor.fetchall()[0][0]

            cursor.execute("""select University
                from University_keyword_score
                where keyword = '{}'
                group by University,keyword
                ORDER BY sum(actual_score) DESC
                LIMIT 1""".format(keyword))
            top_uni = cursor.fetchall()[0][0]

            cursor.execute("""select Journal
                from university_keyword_score
                where keyword = '{}'
                ORDER BY actual_score DESC
                limit 1""".format(keyword))
            top_journal = cursor.fetchall()[0][0]

            cursor.execute("""insert into fav_keywords_summary (keyword, faculty, university,publication)
                values ('{}','{}','{}','{}')""".format(keyword,top_faculty, top_uni,top_journal))
            cursor.fetchall()
            self.cnx4.commit()
            cursor.close()
            return()
        except ValueError as v:
            print(v)
            return(v)
        except:
            print("keyword in favorites already")
            return("keyword in favorites already")


         ### deletes favorite keywords ###
    def delete_favorite_word_mySQL(self, keyword):
        keyword = keyword.lower()
        cursor = self.cnx4.cursor()
        try:
            cursor.execute("""delete from fav_keywords_summary where keyword = '{}'""".format(keyword))
            cursor.execute("""delete from favorite_keywords where keyword_name ='{}' """.format(keyword))

            self.cnx4.commit()
            cursor.fetchall()
            cursor.close()
            return("deleted keyword")
        except:
            return("keyword not in favorites")
    ### 
    def get_fav_keywords(self):
        cursor = self.cnx4.cursor()
        cursor.execute("""select keyword,faculty,university,publication from fav_keywords_summary""")
        result = DataFrame(cursor.fetchall())
        cursor.close()
        return(result)
