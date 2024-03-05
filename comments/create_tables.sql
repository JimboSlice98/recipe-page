CREATE TABLE Comments (
    comment_id VARCHAR(255) PRIMARY KEY,
    time_stamp VARCHAR(255),
    blog_id INT,
    user_id INT,
    message VARCHAR(MAX)
);
