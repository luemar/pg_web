import sqlite3

conn = sqlite3.connect("app.db")
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS allowed_emails (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                            email TEXT UNIQUE)""")

cur.execute("""CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                   username TEXT UNIQUE, email TEXT)""")

cur.execute("INSERT INTO allowed_emails(email) VALUES ('paul.m.eugster@bluewin.ch')")
cur.execute("INSERT INTO allowed_emails(email) VALUES ('ub@bruhin-tax.ch')")
cur.execute("INSERT INTO allowed_emails(email) VALUES ('reto@fintschin.ch')")
cur.execute("INSERT INTO allowed_emails(email) VALUES ('ludwig.kaminski@adon.li')")
cur.execute("INSERT INTO allowed_emails(email) VALUES ('marcus.luetolf@bluewin.ch')")
cur.execute("INSERT INTO allowed_emails(email) VALUES ('w.nuener@powersurf.li')")
cur.execute("INSERT INTO allowed_emails(email) VALUES ('andreas.petermann.li')")
cur.execute("INSERT INTO allowed_emails(email) VALUES ('schaedler@robertjohann.com')")
cur.execute("INSERT INTO allowed_emails(email) VALUES ('e.schluep@bluewin.ch')")
cur.execute("INSERT INTO allowed_emails(email) VALUES ('g.schober@bluewin.ch')")
cur.execute("INSERT INTO allowed_emails(email) VALUES ('silviozanolari@hotmail.com')")
cur.execute("INSERT INTO allowed_emails(email) VALUES ('s.maerk@maerk-arch.ch')")
cur.execute("INSERT INTO allowed_emails(email) VALUES ('paul.frei51@gmail.com')")

conn.commit()
conn.close()

print("Database initialized.")
