CREATE TABLE City(
    city_name VARCHAR(10) NOT NULL,
    state VARCHAR(10) NOT NULL,
    population INT NOT NULL,
    zip_code INT NOT NULL,
    city_size INT NOT NULL,
    PRIMARY KEY(city_name)
);


CREATE TABLE Store(
        store_ID INT NOT NULL,
    phone_number INT NOT NULL,
    street_address VARCHAR(20) NOT NULL,
    childcare_limit INT NOT NULL,
         city_name VARCHAR(10) NOT NULL,
PRIMARY KEY(store_ID),
FOREIGN KEY(city_name) REFERENCES City(city_name)
);


CREATE TABLE Store_StoreAffiliates(
        store_ID int NOT NULL,
        store_affiliates varchar(20) NOT NULL,
        PRIMARY KEY(store_ID, store_affiliates)
);
CREATE TABLE Date(
date datetime NOT NULL,
PRIMARY KEY(date));


CREATE TABLE Holiday(
date datetime NOT NULL,
holiday varchar(50) NOT NULL
PRIMARY KEY(date, holiday),
FOREIGN KEY(date) REFERENCES Date(date));


CREATE TABLE AdCampaign(
date datetime NOT NULL,
ad_compaign_description varchar(100) NOT NULL
PRIMARY KEY(date, ad_compaign_description),
FOREIGN KEY(date) REFERENCES Date(date));


CREATE TABLE Sales(
        saleID int NOT NULL,
        quantity_sold int NOT NULL,
    date datetime NOT NULL,
    store_ID int NOT NULL,
        PRIMARY KEY(saleID),
        FOREIGN KEY(date) REFERENCES Date(date),
        FOREIGN KEY(store_ID) REFERENCES Store(store_ID)
);


CREATE TABLE Product(
        PID INT NOT NULL,
        product_name varchar(20) NOT NULL,
        regular_price float NOT NULL,
        saleID int NOT NULL,
        PRIMARY KEY(PID),
    FOREIGN KEY(saleID) REFERENCES Sales(saleID)
);


CREATE TABLE DiscountPrice(
        PID INT NOT NULL,
        date datetime NOT NULL,
        discount_price float NOT NULL,
        PRIMARY KEY(PID, date),
    FOREIGN KEY(PID) REFERENCES Product(PID),
    FOREIGN KEY(date) REFERENCES Date(date)
);




CREATE TABLE Sales_Product(
    PID INT NOT NULL,
    saleID int NOT NULL,
    FOREIGN KEY(PID) REFERENCES Product(PID),
        FOREIGN KEY(saleID) REFERENCES Sales(SaleID)
);


CREATE TABLE Category (
        category_name varchar(20) NOT NULL,
    PRIMARY KEY (category_name)
);


CREATE TABLE Product_Category(
        PID INT NOT NULL,
        category_name varchar(20) NOT NULL,
        PRIMARY KEY(PID, category_name),
    FOREIGN KEY(PID) REFERENCES Product(PID),
    FOREIGN KEY(category_name) REFERENCES Category(category_name)
);


UPDATE City
SET city_size = CASE WHEN population < 3700000 THEN 'Small'
                               WHEN population <6700000 THEN 'Medium'
                               WHEN population <9000000 THEN 'Large'
                               ELSE 'Extra Large' END
;