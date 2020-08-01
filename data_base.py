import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE facebook_insights")

mycursor = mydb.cursor()

mycursor.execute("CREATE TABLE ad_company (campaign_id INT, clicks INT, "
                 "spend INT, impressions INT, date_start DATE, date_stop DATE)")
