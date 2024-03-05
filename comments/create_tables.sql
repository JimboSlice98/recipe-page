CREATE TABLE Comments (
    time_stamp VARCHAR(255) PRIMARY KEY,
    blog_id INT,
    user_id INT,
    message VARCHAR(MAX)
);