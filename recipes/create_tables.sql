CREATE TABLE Recipes (
  recipe_id INT IDENTITY(1,1) PRIMARY KEY,
  title VARCHAR(255),
  user_id INT,
  ingredients VARCHAR(MAX),
  steps VARCHAR(MAX)
);
