CREATE TABLE Blogs (
    blog_id INT PRIMARY KEY,
    title VARCHAR(255) -- Add additional columns as needed
);

CREATE TABLE Users (
    user_id INT PRIMARY KEY,
    username VARCHAR(255),
    -- Add additional columns as needed, such as email, password (hashed), etc.
);

CREATE TABLE Comments (
    comment_id INT PRIMARY KEY,
    blog_id INT,
    user_id INT,
    message TEXT,
    FOREIGN KEY (blog_id) REFERENCES Blogs(blog_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
