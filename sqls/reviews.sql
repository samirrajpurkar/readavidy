CREATE TABLE REVIEWS (
  id SERIAL PRIMARY KEY,
  rating INT,
  review VARCHAR(250) NOT NULL,
  user_id INT references USERS(user_id),
  book_id INT references BOOKS(id)
);