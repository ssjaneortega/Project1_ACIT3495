import pymysql
import pymongo

mysql_conn = pymysql.connect(host="mysql_db", user="user", password="password", database="analytics_db")
mongo_client = pymongo.MongoClient("mongodb://mongo_db:27017/")
mongo_db = mongo_client["analytics"]

cursor = mysql_conn.cursor()
cursor.execute("SELECT MAX(value), MIN(value), AVG(value) FROM data")
max_val, min_val, avg_val = cursor.fetchone()

mongo_db.stats.insert_one({"max": max_val, "min": min_val, "avg": avg_val})

print("Analytics saved to MongoDB")
mysql_conn.close()
