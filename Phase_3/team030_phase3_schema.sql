DROP DATABASE IF EXISTS cs6400_2021_01_Team030; 
SET default_storage_engine=InnoDB;
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS cs6400_2021_01_Team030;
USE cs6400_2021_01_Team030;


CREATE TABLE IF NOT EXISTS Store(
    store_ID INT NOT NULL,
    phone_number VARCHAR(50) NOT NULL,
    street_address VARCHAR(50) NOT NULL,
    city_name VARCHAR(50) NOT NULL,
    state VARCHAR(20) NOT NULL,
    restaurant VARCHAR(20) NOT NULL,
    snackbar VARCHAR(20) NOT NULL,
    childcare_limit INT DEFAULT 0,
    PRIMARY KEY(store_ID)
);

CREATE TABLE IF NOT EXISTS Population(
    city_name VARCHAR(50) NOT NULL,
    state VARCHAR(20) NOT NULL,
    population INT NOT NULL,
    city_size VARCHAR(20) NOT NULL,
    PRIMARY KEY(city_name, state)
);


CREATE TABLE IF NOT EXISTS Day(
    day date NOT NULL,
    PRIMARY KEY(day)
);

CREATE TABLE IF NOT EXISTS Holiday(
    day date NOT NULL,
    holiday varchar(50) NOT NULL,
    PRIMARY KEY(day, holiday),
    FOREIGN KEY(day) REFERENCES Day(day)
);


CREATE TABLE IF NOT EXISTS AdCampaign(
    day date NOT NULL,
    ad_campaign_description varchar(100) NOT NULL,
    PRIMARY KEY(day, ad_campaign_description),
    FOREIGN KEY(day) REFERENCES Day(day)
    );

CREATE TABLE IF NOT EXISTS Product(
    PID INT NOT NULL,
    product_name varchar(20) NOT NULL,
    regular_price float NOT NULL,
    PRIMARY KEY(PID)
);

CREATE TABLE IF NOT EXISTS DiscountPrice(
    PID INT NOT NULL,
    day date NOT NULL,
    discount_price float NOT NULL,
    PRIMARY KEY(PID, day),
    CONSTRAINT fk_pid_dis
    FOREIGN KEY(PID) REFERENCES Product(PID),
    CONSTRAINT fk_day_dis
    FOREIGN KEY(day) REFERENCES Day(day)

);

CREATE TABLE IF NOT EXISTS Sales(
    saleID int NOT NULL AUTO_INCREMENT,
    quantity_sold int NOT NULL,
    day date NOT NULL,
    store_ID int NOT NULL,
    PID INT NOT NULL,
    PRIMARY KEY(saleID),
    UNIQUE KEY(day, store_ID,PID),
    CONSTRAINT fk_store_id
    FOREIGN KEY(store_ID) REFERENCES Store(store_ID),
    CONSTRAINT fk_pid_sales
    FOREIGN KEY(PID) REFERENCES Product(PID),
    CONSTRAINT fk_day_sales
    FOREIGN KEY(day) REFERENCES Day(day)

);

CREATE TABLE IF NOT EXISTS Category (
    category_name varchar(20) NOT NULL,
    PRIMARY KEY (category_name)
);


CREATE TABLE IF NOT EXISTS Product_Category(
    PID INT NOT NULL,
    category_name varchar(20) NOT NULL,
    PRIMARY KEY(PID, category_name),
    CONSTRAINT fk_pid_cat
    FOREIGN KEY(PID) REFERENCES Product(PID),
    CONSTRAINT fk_category
    FOREIGN KEY(category_name) REFERENCES Category(category_name)
);

delimiter //
CREATE TRIGGER derive_city_size
BEFORE INSERT ON Population
FOR EACH ROW
BEGIN
IF NEW.population < 3700000 THEN SET NEW.city_size = "Small";
ELSEIF NEW.population <6700000 THEN 
	SET  NEW.city_size = 'Medium';
ELSEIF NEW.population <9000000 THEN 
	SET NEW.city_size = 'Large';
ELSE SET NEW.city_size = 'Extra Large';
END IF;
END;//


