-- Users table
CREATE TABLE Users (
    id INTEGER PRIMARY KEY NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

-- Author table
CREATE TABLE Author (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL
);

-- Publisher table
CREATE TABLE Publisher (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL
);

-- Inventory table
CREATE TABLE Inventory (
    id INTEGER PRIMARY KEY NOT NULL,
    quantity INTEGER NOT NULL
);

-- Books table
CREATE TABLE Books (
    id INTEGER PRIMARY KEY NOT NULL,
    title TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    publisher_id INTEGER NOT NULL,
    inventory_id INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES Author(id),
    FOREIGN KEY (publisher_id) REFERENCES Publisher(id),
    FOREIGN KEY (inventory_id) REFERENCES Inventory(id)
);

-- Customers table
CREATE TABLE Customers (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    phone varchar(50),
    address varchar(200),
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

-- Orders table
CREATE TABLE Orders (
    id INTEGER PRIMARY KEY NOT NULL,
    book_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (book_id) REFERENCES Books(id),
    FOREIGN KEY (customer_id) REFERENCES Customers(id)
);


-- Payment table
CREATE TABLE Payment (
    id INTEGER PRIMARY KEY NOT NULL,
    amount REAL NOT NULL,
    order_id INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(id)
);

-- Invoice table
CREATE TABLE Invoice (
    id INTEGER PRIMARY KEY NOT NULL,
    total REAL NOT NULL,
    customer_id INTEGER NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customers(id)
);

-- Priority table
CREATE TABLE Priority (
    id INTEGER PRIMARY KEY NOT NULL,
    level TEXT NOT NULL
);

-- SalesRecord table
CREATE TABLE SalesRecord (
    id INTEGER PRIMARY KEY NOT NULL,
    order_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(id)
);

-- ShoppingCart table
CREATE TABLE ShoppingCart (
    id INTEGER PRIMARY KEY NOT NULL,
    customer_id INTEGER NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customers(id)
);

-- CartItem table
CREATE TABLE CartItem (
    id INTEGER PRIMARY KEY NOT NULL,
    cart_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (cart_id) REFERENCES ShoppingCart(id),
    FOREIGN KEY (book_id) REFERENCES Books(id)
);


ALTER TABLE Books ADD COLUMN price FLOAT;
ALTER TABLE Orders ADD COLUMN order_date DATETIME;
ALTER TABLE Orders ADD COLUMN priority_id int;
