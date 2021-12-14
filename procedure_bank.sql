-- CS4400: Introduction to Database Systems (Fall 2021)
-- Phase III: Stored Procedures & Views [v0] Tuesday, November 9, 2021 @ 12:00am EDT
-- Team 58
-- Yi-Shin Gan (ygan41)
-- Roman Karmazin (rkarmazin3)
-- Wang Xie (wxie48)
-- Zhe Zhang (zzhang901)
-- Directions:
-- Please follow all instructions for Phase III as listed on Canvas.
-- Fill in the team number and names and GT usernames for all members above.


-- ID: 1a
-- Name: register_customer
drop procedure if exists register_customer;
delimiter //
create procedure register_customer (
    in i_email varchar(50),
    in i_first_name varchar(100),
    in i_last_name varchar(100),
    in i_password varchar(50),
    in i_phone_number char(12),
    in i_cc_number varchar(19),
    in i_cvv char(3),
    in i_exp_date date,
    in i_location varchar(50)
)
sp_main: begin
-- TODO: Implement your solution here
if i_email not like ''%@%'' then leave sp_main; end if;

    if i_email in (select email from clients
    where email in (select email from owners) and email not in (select email from customer))

    then
    insert into
    customer values
    (i_email, i_cc_number, i_cvv, i_exp_date, i_location);

    else
    insert into accounts
    values (i_email, i_first_name, i_last_name, i_password);

    insert into clients values
    (i_email, i_phone_number);

    insert into customer values
    (i_email, i_cc_number, i_cvv, i_exp_date, i_location);
    end if;
end //
delimiter ;


-- ID: 1b
-- Name: register_owner
drop procedure if exists register_owner;
delimiter //
create procedure register_owner (
    in i_email varchar(50),
    in i_first_name varchar(100),
    in i_last_name varchar(100),
    in i_password varchar(50),
    in i_phone_number char(12)
)
sp_main: begin
-- TODO: Implement your solution here
if i_email not like ''%@%'' then leave sp_main; end if;
        if i_email in (select email from accounts
    where email not in (select email from owners) and email in (select email from customer))

    then
    insert into
    owners values
    (i_email);

    else
    insert into accounts
    values (i_email, i_first_name, i_last_name, i_password);

    insert into clients values
    (i_email, i_phone_number);

    insert into owners values
    (i_email);
    end if;
end //
delimiter ;


-- ID: 1c
-- Name: remove_owner
drop procedure if exists remove_owner;
delimiter //
create procedure remove_owner (
    in i_owner_email varchar(50)
)
sp_main: begin
-- TODO: Implement your solution here
if i_owner_email not in (select owner_email from property)
    then
if i_owner_email in (select email from clients where email in (select email from owners) and email not in (select email from customer))
	then
	delete from owners where email = i_owner_email;
	delete from clients where email = i_owner_email;
	delete from accounts where email = i_owner_email;

elseif i_owner_email in (select email from clients
	where email in (select email from owners) and email in (select email from customer))
	then
	delete from owners where email = i_owner_email;
else leave sp_main;
	end if;
  end if;
end //
delimiter ;


-- ID: 2a
-- Name: schedule_flight
drop procedure if exists schedule_flight;
delimiter //
create procedure schedule_flight (
    in i_flight_num char(5),
    in i_airline_name varchar(50),
    in i_from_airport char(3),
    in i_to_airport char(3),
    in i_departure_time time,
    in i_arrival_time time,
    in i_flight_date date,
    in i_cost decimal(6, 2),
    in i_capacity int,
    in i_current_date date
)
sp_main: begin
-- TODO: Implement your solution here
	if i_flight_date < i_current_date then leave sp_main; end if;
	if (i_from_airport, i_to_airport) in (select From_Airport, To_Airport from flight) then leave sp_main; end if;
    insert into flight values (i_flight_num, i_airline_name, i_from_airport, i_to_airport, i_departure_time,
    i_arrival_time, i_flight_date, i_cost, i_capacity);
end //
delimiter ;


-- ID: 2b
-- Name: remove_flight
drop procedure if exists remove_flight;
delimiter //
create procedure remove_flight (
    in i_flight_num char(5),
    in i_airline_name varchar(50),
    in i_current_date date
)
sp_main: begin
-- TODO: Implement your solution here
	if (i_flight_num, i_airline_name) not in (select Flight_Num, Airline_Name from flight) then leave sp_main; end if;
	if (select flight_date from flight where (flight_num, airline_name) =(i_flight_num, i_airline_name)) <
    i_current_date then leave sp_main; end if;
    delete from book where (flight_num, airline_name) =(i_flight_num, i_airline_name);
    delete from flight where (flight_num, airline_name) =(i_flight_num, i_airline_name);
end //
delimiter ;


-- ID: 3a
-- Name: book_flight
drop procedure if exists book_flight;
delimiter //
create procedure book_flight (
    in i_customer_email varchar(50),
    in i_flight_num char(5),
    in i_airline_name varchar(50),
    in i_num_seats int,
    in i_current_date date
)
sp_main: begin
-- TODO: Implement your solution here
	if (i_customer_email  in  (select Customer from Book)) and (i_flight_num  in (select Flight_Num from Book ))
    and (i_airline_name  in (select Airline_Name from Book ))
    and (i_num_seats in (select Capacity from Flight where Flight_Num = i_flight_num )) >= (i_num_seats in (select Num_Seats from Book where Flight_Num = i_flight_num and Was_Cancelled = 0))
		then
        update Book set Num_Seats = (Num_Seats + i_num_seats) where Customer = i_customer_email and Flight_Num = i_flight_num;
	elseif   (i_num_seats in (select Capacity from Flight where Flight_Num = i_flight_num )) >= (i_num_seats in (select Num_Seats from Book where Flight_Num = i_flight_num and Was_Cancelled = 0))
    and (i_current_date <= (select Flight_Date from Flight where Flight_Num = i_flight_num ))
    and (i_customer_email, i_flight_num, i_airline_name) not in (select Customer, Flight_Num, Airline_Name from Book)
		then
		insert into Book values (i_customer_email, i_flight_num, i_airline_name, i_num_seats, 0);
	end if;
end //
delimiter ;

-- ID: 3b
-- Name: cancel_flight_booking
drop procedure if exists cancel_flight_booking;
delimiter //
create procedure cancel_flight_booking (
    in i_customer_email varchar(50),
    in i_flight_num char(5),
    in i_airline_name varchar(50),
    in i_current_date date
)
sp_main: begin
-- TODO: Implement your solution here
	if (i_customer_email  = (select Customer from Book where Flight_Num = i_flight_num))
    and (i_current_date <= (select Flight_Date from Flight where Flight_Num = i_flight_num ))
		then
		update Book set Was_Cancelled = 1 where Customer = i_customer_email and Flight_Num = i_flight_num;
	end if;
end //
delimiter ;


-- ID: 3c
-- Name: view_flight
create or replace view view_flight (
    flight_id,
    flight_date,
    airline,
    destination,
    seat_cost,
    num_empty_seats,
    total_spent
) as
-- TODO: replace this select query with your solution
SELECT
    f.Flight_Num AS "flight_id",
    f.Flight_Date AS "flight_date",
    f.Airline_Name AS "airline",
    f.To_Airport AS "destination",
    f.Cost AS "seat_cost",
    f.capacity - SUM(IF(b.Was_Cancelled = 0, b.Num_Seats, 0)) AS "num_empty_seats",
    (SUM(IF(b.Was_Cancelled = 1,
        (b.Num_Seats * f.cost * 0.2),
        0)) + SUM(IF(b.Was_Cancelled = 0,
        (b.Num_Seats * f.cost),
        0))) AS "total_spent"
FROM
    Flight AS f
        LEFT OUTER JOIN
    Book AS b ON b.Flight_Num = f.Flight_Num
GROUP BY f.Flight_Num , f.Flight_Date , f.Airline_Name;


-- ID: 4a
-- Name: add_property
drop procedure if exists add_property;
delimiter //
create procedure add_property (
    in i_property_name varchar(50),
    in i_owner_email varchar(50),
    in i_description varchar(500),
    in i_capacity int,
    in i_cost decimal(6, 2),
    in i_street varchar(50),
    in i_city varchar(50),
    in i_state char(2),
    in i_zip char(5),
    in i_nearest_airport_id char(3),
    in i_dist_to_airport int
)
sp_main: begin
-- TODO: Implement your solution here
	if (i_property_name, i_owner_email) in (select Property_Name, Owner_Email from Property) then leave sp_main; end if;

	if (i_street, i_city, i_state, i_zip) not in (select Street, City, State, Zip from Property)
	and (i_property_name, i_owner_email) not in (select Property_Name, Owner_Email from Property)
	and i_nearest_airport_id  in (select Airport_Id from Airport)
		then
		insert into Property values(i_property_name, i_owner_email, i_description, i_capacity, i_cost, i_street, i_city, i_state, i_zip);
		insert into Is_Close_To values (i_property_name, i_owner_email, i_nearest_airport_id, i_dist_to_airport);
	elseif (i_street, i_city, i_state, i_zip) not in (select Street, City, State, Zip from Property)
	and (i_property_name, i_owner_email) not in (select Property_Name, Owner_Email from Property)
	and i_nearest_airport_id not in (select Airport_Id from Airport)
		then
		insert into Property values(i_property_name, i_owner_email, i_description, i_capacity, i_cost, i_street, i_city, i_state, i_zip);

	elseif (i_street, i_city, i_state, i_zip) not in (select Street, City, State, Zip from Property)
	and (i_property_name, i_owner_email) not in (select Property_Name, Owner_Email from Property)
	and i_nearest_airport_id = NULL or i_dist_to_airport = NULL
		then
		insert into Property values(i_property_name, i_owner_email, i_description, i_capacity, i_cost, i_street, i_city, i_state, i_zip);
		insert into Is_Close_To values (i_property_name, i_owner_email, NULL, NULL);
	end if;
end //
delimiter ;


-- ID: 4b
-- Name: remove_property
drop procedure if exists remove_property;
delimiter //
create procedure remove_property (
    in i_property_name varchar(50),
    in i_owner_email varchar(50),
    in i_current_date date
)
sp_main: begin
-- TODO: Implement your solution here


SELECT
    COUNT(*)
INTO @reserved FROM
    reserve
WHERE
    (Property_Name = i_property_name)
        AND (Owner_Email = i_owner_email)
        AND (Was_Cancelled = 0)
        AND i_current_date BETWEEN Start_Date AND End_Date;

If @reserved >= 0
then
    delete from Reserve where (Property_Name = i_property_name and  Owner_Email = i_owner_email);
DELETE FROM Review
WHERE
    (Property_Name = i_property_name
    AND Owner_Email = i_owner_email);
	DELETE FROM Amenity
WHERE
    (Property_Name = i_property_name
    AND Property_Owner = i_owner_email);
DELETE FROM Is_Close_To
WHERE
    (Property_Name = i_property_name
    AND Owner_Email = i_owner_email);
DELETE FROM Property
WHERE
    (Property_Name = i_property_name
    AND Owner_Email = i_owner_email);
    end if;
end //
delimiter ;

-- ID: 5a
-- Name: reserve_property
drop procedure if exists reserve_property;
delimiter //
create procedure reserve_property (
    in i_property_name varchar(50),
    in i_owner_email varchar(50),
    in i_customer_email varchar(50),
    in i_start_date date,
    in i_end_date date,
    in i_num_guests int,
    in i_current_date date
)
sp_main: begin
-- TODO: Implement your solution here
if i_start_date < i_current_date then leave sp_main; end if;
    if i_start_date between (select Start_Date from reserve where (customer, Start_Date, was_cancelled) = (i_customer_email,i_start_date,0))
    and (select end_Date from reserve where (customer, end_Date, was_cancelled)=(i_customer_email,i_start_date,0))
		then leave sp_main; end if;
    if i_num_guests > (select capacity - sum(Num_Guests) from reserve natural join property
    where (Property_Name, Owner_Email)= (i_property_name, i_owner_email) and (start_date, end_date)=(i_start_date,i_end_date)
		group by Property_Name, Owner_Email)
		then leave sp_main; end if;
		insert into reserve values (i_property_name, i_owner_email, i_customer_email, i_start_date, i_end_date, i_num_guests, 0);
end //
delimiter ;

-- ID: 5b
-- Name: cancel_property_reservation
drop procedure if exists cancel_property_reservation;
delimiter //
create procedure cancel_property_reservation (
    in i_property_name varchar(50),
    in i_owner_email varchar(50),
    in i_customer_email varchar(50),
    in i_current_date date
)
sp_main: begin
-- TODO: Implement your solution here
if (select was_cancelled from reserve where
    (Property_Name, Owner_Email, customer)=(i_property_name, i_owner_email, i_customer_email)) = 1
		then leave sp_main; end if;
    if i_current_date < (select start_date from reserve where (Property_Name,Owner_Email, customer)=
    (i_property_name, i_owner_email, i_customer_email))
		then
		update reserve set was_cancelled = 1
		where (Property_Name, Owner_Email, customer) = (i_property_name, i_owner_email, i_customer_email);
    end if;
end //
delimiter ;


-- ID: 5c
-- Name: customer_review_property
drop procedure if exists customer_review_property;
delimiter //
create procedure customer_review_property (
    in i_property_name varchar(50),
    in i_owner_email varchar(50),
    in i_customer_email varchar(50),
    in i_content varchar(500),
    in i_score int,
    in i_current_date date
)
sp_main: begin
-- TODO: Implement your solution here
if (select start_date from reserve where (Property_Name, owner_Email, customer, was_cancelled)=
    (i_property_name,i_owner_email,i_customer_email,0)) <= i_current_date
		then
		insert into review values
    (i_property_name,i_owner_email,i_customer_email,i_content,i_score);
    end if;
end //
delimiter ;


-- ID: 5d
-- Name: view_properties
create or replace view view_properties (
    property_name,
    average_rating_score,
    description,
    address,
    capacity,
    cost_per_night
) as
-- TODO: replace this select query with your solution
select property.Property_Name, avg(Score), Descr, concat(Street,'', '', city, '', '', State, '', '', zip),
Capacity, Cost
from property left join review on property.property_name = review.property_name and property.owner_email = review.owner_email
group by property.Property_Name, property.Owner_Email;


-- ID: 5e
-- Name: view_individual_property_reservations
drop procedure if exists view_individual_property_reservations;
delimiter //
create procedure view_individual_property_reservations (
    in i_property_name varchar(50),
    in i_owner_email varchar(50)
)
sp_main: begin
    drop table if exists view_individual_property_reservations;
    create table view_individual_property_reservations (
        property_name varchar(50),
        start_date date,
        end_date date,
        customer_email varchar(50),
        customer_phone_num char(12),
        total_booking_cost decimal(6,2),
        rating_score int,
        review varchar(500)
    ) as
    -- TODO: replace this select query with your solution
select reserve.Property_Name as property_name, Start_Date, End_Date, reserve.Customer as customer_email, Phone_Number as customer_phone_num,
case when was_cancelled = 1
	then
	((end_date-start_date) + 1) * Cost * 0.2
	else
	((end_date-start_date) + 1) * Cost
end as total_booking_cost, score as rating_score, content as review
from reserve left join clients on reserve.customer=clients.email
left join property on (reserve.Property_Name, reserve.owner_email)=(property.Property_Name, property.owner_email)
left join review on (reserve.Property_Name, reserve.owner_email, Reserve.customer)=(review.property_name, review.owner_email, review.customer)
where (Reserve.property_name, reserve.owner_email) = (i_property_name, i_owner_email);
end //
delimiter ;

call view_individual_property_reservations(''New York City Property'', ''cbing10@gmail.com'');
-- ID: 6a
-- Name: customer_rates_owner
drop procedure if exists customer_rates_owner;
delimiter //
create procedure customer_rates_owner (
    in i_customer_email varchar(50),
    in i_owner_email varchar(50),
    in i_score int,
    in i_current_date date
)
sp_main: begin
-- TODO: Implement your solution here
if ((select was_cancelled from reserve where
    (Owner_Email, customer) = (i_owner_email, i_customer_email)) = 0)
    and ((select start_date from reserve where
    (Owner_Email, customer) = (i_owner_email, i_customer_email)) <= i_current_date)
    and ((i_customer_email, i_owner_email) not in (select customer, owner_email from Customers_Rate_Owners))
then
    insert into Customers_Rate_Owners values
    (i_customer_email, i_owner_email, i_score);
    end if;
end //
delimiter ;


-- ID: 6b
-- Name: owner_rates_customer
drop procedure if exists owner_rates_customer;
delimiter //
create procedure owner_rates_customer (
    in i_owner_email varchar(50),
    in i_customer_email varchar(50),
    in i_score int,
    in i_current_date date
)
sp_main: begin
-- TODO: Implement your solution here
if ((select was_cancelled from reserve where
    (Owner_Email, customer) = (i_owner_email, i_customer_email)) = 0)
    and ((select start_date from reserve where
    (Owner_Email, customer) = (i_owner_email, i_customer_email)) <= i_current_date)
    and ((i_owner_email, i_customer_email) not in (select owner_email, customer from Owners_Rate_Customers))
then
    insert into Owners_Rate_Customers values
    (i_owner_email, i_customer_email, i_score);
    end if;
end //
delimiter ;


-- ID: 7a
-- Name: view_airports
CREATE OR REPLACE VIEW view_airports (airport_id , airport_name , time_zone , total_arriving_flights , total_departing_flights , avg_departing_flight_cost) AS
    SELECT
        t1.Airport_Id, Airport_Name, Time_Zone, t1.a, t2.b, t2.c
    FROM
        (SELECT
            Airport_Id, COUNT(DISTINCT (From_Airport)) AS a
        FROM
            Airport
        LEFT OUTER JOIN Flight ON Airport_Id = To_Airport
        GROUP BY Airport_Id) AS t1,
        (SELECT
            Airport_Id,
                Airport_Name,
                Time_Zone,
                COUNT(DISTINCT (To_Airport)) AS b,
                SUM(Cost) / COUNT(DISTINCT (To_Airport)) AS c
        FROM
            Airport
        LEFT OUTER JOIN Flight ON Airport_Id = From_Airport
        GROUP BY Airport_Id) AS t2
    WHERE
        t1.Airport_Id = t2.Airport_Id;

-- ID: 7b
-- Name: view_airlines
CREATE OR REPLACE VIEW view_airlines (airline_name , rating , total_flights , min_flight_cost) AS
    SELECT
        Airline.Airline_Name,
        Rating,
        COUNT((Flight.Airline_Name)),
        MIN(Cost)
    FROM
        Airline
            LEFT OUTER JOIN
        Flight ON Airline.Airline_Name = Flight.Airline_Name
    GROUP BY Airline.Airline_Name;


-- ID: 8a
-- Name: view_customers
create or replace view view_customers (
    customer_name,
    avg_rating,
    location,
    is_owner,
    total_seats_purchased
) as
-- TODO: replace this select query with your solution
-- view customers
select concat(first_name, '' '', last_name), avg(Score), location,
case
when email in
(select email from owners)
then 1 else 0 end, COALESCE(sum(num_seats), 0)
from customer natural join accounts
left join book on book.customer=customer.email
left join Owners_Rate_Customers on Owners_Rate_Customers.customer=customer.email
group by customer.email;


-- ID: 8b
-- Name: view_owners
create or replace view view_owners (
    owner_name,
    avg_rating,
    num_properties_owned,
    avg_property_rating
) as
-- TODO: replace this select query with your solution

SELECT
    CONCAT(first_name, '' '', last_name) AS owner_name,
    c.Score AS avg_rating,
    COALESCE(p.Own_Email, 0) AS num_properties_owned,
    r.Review AS avg_property_rating
FROM
    Owners o
        JOIN
    Accounts AS a ON a.Email = o.Email
        LEFT JOIN
    (SELECT
        Owner_Email, AVG(Score) AS Score
    FROM
        Customers_Rate_Owners
    GROUP BY Owner_Email) c ON c.Owner_Email = o.Email
        LEFT JOIN
    (SELECT
       Owner_Email, count(Owner_Email) AS Own_Email
    FROM
        Property
    GROUP BY Owner_Email) p ON p.Owner_Email = o.Email
        LEFT JOIN
    (SELECT
        Owner_Email, AVG(Score) AS Review
    FROM
        Review
    GROUP BY Owner_Email) r ON r.Owner_Email = o.Email
ORDER BY o.Email;


-- ID: 9a
-- Name: process_date
drop procedure if exists process_date;
delimiter //
create procedure process_date (
    in i_current_date date
)
sp_main: begin
-- TODO: Implement your solution here
update Customer
left outer join Book on Customer.Email = Book.Customer
left outer join Flight on Book.Flight_Num = Flight.Flight_Num
left outer join  Airport on Airport.Airport_Id = Flight.To_Airport
set Customer.Location = Airport.State
where Book.Was_Cancelled = 0 and i_current_date = Flight.Flight_date;
end //
delimiter ;
