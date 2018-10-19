import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    db.execute("DROP TABLE REVIEWS;")
    db.execute("CREATE TABLE REVIEWS (id SERIAL PRIMARY KEY,rating INT, review VARCHAR(250) NOT NULL, user_id INT references USERS(user_id), book_id INT references BOOKS(id));")
    db.commit()

if __name__ == "__main__":
    main()







