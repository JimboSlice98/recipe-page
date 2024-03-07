-- SQL Script to create a new table based on the existing schema and copy data

-- Step 1: Create a new table with the same schema as dbo.user_details_complete
CREATE TABLE dbo.new_user_details_complete (
    UserID INT PRIMARY KEY IDENTITY(1,1), -- Assuming you want to keep this column as an auto-incrementing primary key
    Email VARCHAR(255) NOT NULL,
    DisplayName VARCHAR(255) NULL,
    CookingLevel VARCHAR(255) NULL,
    FavoriteCuisine VARCHAR(255) NULL,
    ShortBio TEXT NULL,
    ProfilePictureUrl VARCHAR(255) NULL,
    PersonalWebsite VARCHAR(255) NULL,
    Location VARCHAR(255) NULL
);

-- Step 2: Copy data from the existing table to the new one
-- Since UserID is an IDENTITY column, we will not copy it from the old table.
-- SQL Server will automatically generate new values for the new table.
INSERT INTO dbo.new_user_details_complete (Email, DisplayName, CookingLevel, FavoriteCuisine, ShortBio, ProfilePictureUrl, PersonalWebsite, Location)
SELECT Email, DisplayName, CookingLevel, FavoriteCuisine, ShortBio, ProfilePictureUrl, PersonalWebsite, Location
FROM dbo.user_details_complete;

-- This script assumes that you want to start UserID from 1 and increment by 1.
-- Adjust the IDENTITY property as needed if you need a different seed or increment.
