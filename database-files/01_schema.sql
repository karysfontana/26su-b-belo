DROP DATABASE IF EXISTS BELO;
CREATE DATABASE BELO;


USE BELO;


DROP TABLE IF EXISTS Admin;
CREATE TABLE Admin (
   adminID INT PRIMARY KEY,
   firstname varchar(40),
   lastname varchar(40)
);


DROP TABLE IF EXISTS Log;
CREATE TABLE Log (
   logID INT AUTO_INCREMENT PRIMARY KEY,
   date DATETIME,
   action TEXT NOT NULL,
   adminID INT,
   FOREIGN KEY (adminID) REFERENCES Admin(adminID)
);


DROP TABLE IF EXISTS User;
CREATE TABLE User (
   UserID INT AUTO_INCREMENT PRIMARY KEY,
   status varchar(9) NOT NULL,
   signUpDate DATETIME DEFAULT (CURRENT_TIMESTAMP),
   flaggedBy INT,
   FOREIGN KEY (flaggedBy) REFERENCES Admin(adminID)
);


DROP TABLE IF EXISTS Follows;
CREATE TABLE Follows (
   followerID INT,
   followingID INT,
   PRIMARY KEY (followerID, followingID),
   FOREIGN KEY (followerID) REFERENCES User(UserID),
   FOREIGN KEY (followingID) REFERENCES User(UserID)
);


DROP TABLE IF EXISTS Manager;
CREATE TABLE Manager (
   ManagerID INT PRIMARY KEY,
   firstname varchar(40),
   lastname varchar(40),
   userID INT,
   FOREIGN KEY (userID) REFERENCES User(UserID)
);

DROP TABLE IF EXISTS Customer;
CREATE TABLE Customer (
   customerID INT AUTO_INCREMENT PRIMARY KEY,
   firstname varchar(40),
   lastname varchar(40),
   userID INT,
   FOREIGN KEY (userID) REFERENCES User(UserID)
);




DROP TABLE IF EXISTS Menu;
CREATE TABLE Menu (
   menuID INT PRIMARY KEY
);


DROP TABLE IF EXISTS Menu_Item;
CREATE TABLE Menu_Item (
   itemID INT,
   menuID INT,
   price DECIMAL(5,2),
   name varchar(40),
   PRIMARY KEY (itemID, menuID),
   FOREIGN KEY (menuID) REFERENCES Menu(menuID)
);


DROP TABLE IF EXISTS Cuisine_Tags;
CREATE TABLE Cuisine_Tags (
   cuisineID INT PRIMARY KEY,
   CuisineType varchar(40),
   createdBy INT NOT NULL,
   FOREIGN KEY (createdBy) REFERENCES Admin(adminID)
                         ON DELETE RESTRICT
);


#price range can be $,$$,$$$, or $$$$
DROP TABLE IF EXISTS Restaurants;
CREATE TABLE Restaurants (
   RestaurantID INT AUTO_INCREMENT PRIMARY KEY,
   name varchar(40) NOT NULL,
   openTime TIME,
   closeTime TIME,
   priceRange varchar(4),
   country CHAR(2),
   state varchar(100),
   city varchar(100),
   street varchar(100) UNIQUE,
   isPartner BOOL NOT NULL,
   Status varchar(7) NOT NULL,
   ManagerID INT NOT NULL,
   MenuID INT NOT NULL,
   FOREIGN KEY (ManagerID) REFERENCES Manager(ManagerID),
   FOREIGN KEY (MenuID) REFERENCES Menu(menuID)
);

DROP TABLE IF EXISTS Restaurant_cuisine;
CREATE TABLE Restaurant_cuisine (
   CuisineID INT,
   RestaurantID INT,
   PRIMARY KEY (CuisineID, RestaurantID),
   FOREIGN KEY (CuisineID) REFERENCES Cuisine_Tags(cuisineID),
   FOREIGN KEY (RestaurantID) REFERENCES Restaurants(RestaurantID)
);


DROP TABLE IF EXISTS Reviews;
CREATE TABLE Reviews (
   reviewID INT AUTO_INCREMENT PRIMARY KEY,
   comment TEXT,
   createdAt DATETIME NOT NULL,
   Status varchar(7) NOT NULL,
   customerID INT NOT NULL,
   flaggedBy INT,
   RestaurantID INT NOT NULL,
   FOREIGN KEY (customerID) REFERENCES Customer(customerID)
                    ON DELETE RESTRICT
                    ON UPDATE RESTRICT,
   FOREIGN KEY (flaggedBy) REFERENCES Admin(adminID)
                    ON DELETE RESTRICT
                    ON UPDATE RESTRICT,
   FOREIGN KEY (RestaurantID) REFERENCES Restaurants(RestaurantID)
			  ON DELETE RESTRICT
                    ON UPDATE RESTRICT
);


DROP TABLE IF EXISTS Rating;
CREATE TABLE Rating (
   RatingID INT,
   reviewID INT,
   rate INT UNSIGNED NOT NULL,
   ratingType varchar(7) NOT NULL,
   PRIMARY KEY(RatingID, reviewID),
   FOREIGN KEY (reviewID) REFERENCES Reviews(reviewID)
                   ON DELETE CASCADE
);


DROP TABLE IF EXISTS flagged_restaurant;
CREATE TABLE flagged_restaurant (
   adminID INT,
   RestaurantID INT,
   PRIMARY KEY (adminID, RestaurantID),
   FOREIGN KEY (adminID) REFERENCES Admin(adminID),
   FOREIGN KEY (RestaurantID) REFERENCES Restaurants(RestaurantID)
);


DROP TABLE IF EXISTS Neighborhood_Tag;
CREATE TABLE Neighborhood_Tag (
   NeighborhoodID INT PRIMARY KEY,
   city varchar(100) NOT NULL,
   State varchar(100) NOT NULL,
   name varchar(50) NOT NULL UNIQUE,
   CreatedBy INT NOT NULL,
   FOREIGN KEY (CreatedBy) REFERENCES Admin(adminID)
);


DROP TABLE IF EXISTS Restaurant_Neighborhood;
CREATE TABLE Restaurant_Neighborhood (
   NeighborhoodID INT,
   RestaurantID Int,
   PRIMARY KEY (NeighborhoodID,RestaurantID),
   FOREIGN KEY (NeighborhoodID) REFERENCES Neighborhood_Tag(NeighborhoodID),
   FOREIGN KEY (RestaurantID) REFERENCES Restaurants(RestaurantID)
);


DROP TABLE IF EXISTS Claim;
CREATE TABLE Claim (
   claimID INT AUTO_INCREMENT PRIMARY KEY,
   dateSubmitted DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
   dateResolved DATETIME,
   status varchar(10),
   adminReviewed INT,
   restaurantID INT NOT NULL,
   managerID INT NOT NULL,
   FOREIGN KEY (adminReviewed) REFERENCES Admin(adminID),
   FOREIGN KEY (restaurantID) REFERENCES Restaurants(RestaurantID),
   FOREIGN KEY (managerID) REFERENCES Manager(ManagerID)
);


DROP TABLE IF EXISTS Reservation;
CREATE TABLE Reservation (
   resvID INT AUTO_INCREMENT PRIMARY KEY,
   date DATETIME NOT NULL,
   request TEXT,
   partySize INT NOT NULL,
   status varchar(9),
   CustomerID INT NOT NULL,
   AppManagerID INT,
   RestaurantID INT NOT NULL,
   FOREIGN KEY (CustomerID) REFERENCES Customer(customerID),
   FOREIGN KEY (AppManagerID) REFERENCES Manager(ManagerID),
   FOREIGN KEY (RestaurantID) REFERENCES Restaurants(RestaurantID)
);


DROP TABLE IF EXISTS SeatingChart;
CREATE TABLE SeatingChart (
   chartID INT AUTO_INCREMENT PRIMARY KEY,
   totalCovers INT,
   date DATE,
   openTable INT,
   RestaurantID INT NOT NULL,
   FOREIGN KEY (RestaurantID) REFERENCES Restaurants(RestaurantID)
);


DROP TABLE IF EXISTS ReservedSeating;
CREATE TABLE ReservedSeating (
   resvID INT,
   chartID INT,
   PRIMARY KEY (resvID,chartID),
   FOREIGN KEY (resvID) REFERENCES Reservation(resvID),
   FOREIGN KEY (chartID) REFERENCES SeatingChart(chartID)
);


DROP TABLE IF EXISTS WaitList;
CREATE TABLE WaitList (
   entryID INT AUTO_INCREMENT PRIMARY KEY,
   partySize INT,
   firstName varchar(40),
   lastName varchar(40),
   arrivalTime DATETIME,
   seatedTime DATETIME,
   ManagerEdit INT,
   RestaurantID INT NOT NULL,
   FOREIGN KEY (ManagerEdit) REFERENCES Manager(ManagerID),
   FOREIGN KEY (RestaurantID) REFERENCES Restaurants(RestaurantID)
);


DROP TABLE IF EXISTS seating_WaitList;
CREATE TABLE seating_WaitList (
   chartID INT,
   entryID INT,
   PRIMARY KEY (chartID,entryID),
   FOREIGN KEY (chartID) REFERENCES SeatingChart(chartID),
   FOREIGN KEY (entryID) REFERENCES WaitList(entryID)
);