import sqlite3

DATABASE = "articles.db"

def search_articles(query):
    conn = sqlite3.connect(DATABASE)