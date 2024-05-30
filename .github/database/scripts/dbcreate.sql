-- Create the relational tables for delivery database
use delivery;
create table Customer ( 
    customer_num int,
    name varchar(50) not null,
    balance float not null,
    phone varchar(15) not null,
    address varchar(50) not null,

    -- internal constraints
    constraint pk_customer primary key (customer_num),
    constraint ck_cus_1 unique (phone),
    constraint ck_cus_2 unique (name, address),


 );

create table Membership (
    customer_num int not null,
    discount float not null,

    -- internal constraints
    constraint pk_membership primary key (customer_name),

    -- foreign key constraints
    constraint fk_membership_1 foreign key (customer_num) references Customer(customer_num) on delete cascade
);


 create table Restaurant (
    restaurant_num int auto_increment,
    name varchar(50) not null,
    phone varchar(15) not null,
    address varchar(50) not null,
    category varchar(50) not null,

    -- internal constraints
    constraint pk_restaurant primary key (restaurant_num),
    constraint ck_rest_1 unique (address),
    constraint ck_rest_2 unique (phone)

 );

 create table Order (
    order_num int auto_increment,
    customer_num int not null,
    restaurant_num int not null,
    order_date date not null,
    delivery_date date not null,
    delivery_time time not null,
    total float not null,
    status varchar(50) not null,

    -- internal constraints
    constraint pk_order primary key (order_num),
    constraint ck_order_1 check (status in ('pending', 'delivered', 'cancelled')),

    -- foreign key constraints
    constraint fk_order_1 foreign key (customer_num) references Customer(customer_num),
    constraint fk_order_2 foreign key (restaurant_num) references Restaurant(restaurant_num)
 );

 create table Feedback (
   feedback_num int auto_increment not null,
   order_num int not null,
   customer_name varchar(50) not null,
   restaurant_num int not null,
   feedback_date date not null,
   feedback_text varchar(500) not null,
   rating int not null,

   -- internal constraints
   constraint pk_feed primary key (feedback_num),
   constraint ck_feed_1 check (rating between 1 and 5),

   -- foreign key constraints
   constraint fk_feedback_1 foreign key (restaurant_num) references Restaurant(restaurant_num) on delete cascade,
   constraint fk_feedback_2 foreign key (customer_name) references Customer(name)
 );

create table FoodItem (
    food_num int auto_increment,
    restaurant_num int not null,
    name varchar(50) not null,
    price float not null,
    category varchar(50) not null,

    -- internal constraints
    constraint pk_food primary key (food_num),

    -- foreign key constraints
    constraint fk_food_1 foreign key (restaurant_num) references Restaurant(restaurant_num) on delete cascade
);

create table OrderItem (
    order_num int not null,
    food_num int not null,
    quantity int not null,

    -- internal constraints
    constraint pk_order_item primary key (order_num, food_num),

    -- foreign key constraints
    constraint fk_order_item_1 foreign key (order_num) references Order(order_num) on delete cascade,
    constraint fk_order_item_2 foreign key (food_num) references FoodItem(food_num)
);
