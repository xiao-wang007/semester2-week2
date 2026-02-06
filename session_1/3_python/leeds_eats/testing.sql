-- Enable readable output format
.mode columns
.headers on

-- Instructions for students:
-- 1. Open SQLite in terminal: sqlite3 food_delivery.db
-- 2. Load this script: .read testing.sql
-- 3. Exit SQLite: .exit


-- You can use this to test your sql before you write it into your program.

-- ==================================================
-- Section 1 – Summaries
-- ==================================================

-- 1. Display the total number of customers
SELECT COUNT(*) AS total_customers FROM customers;

-- 2. Show the earliest and latest customer signup dates
SELECT MIN(signup_date) AS earliest_signup, MAX(signup_date) AS latest_signup FROM customers;

-- 3. Display total number of orders, average order value, highest and lowest order totals
SELECT 
    COUNT(*) AS total_orders,
    AVG(order_total) AS average_order_value,
    MAX(order_total) AS highest_order,
    MIN(order_total) AS lowest_order
FROM orders;

-- 4. Display the total number of drivers and their hire dates
SELECT COUNT(*) AS total_drivers FROM drivers;
SELECT driver_name, hire_date FROM drivers ORDER BY hire_date;

-- ==================================================
-- Section 2 – Key Statistics
-- ==================================================

-- 5. Orders per customer - Customer name, Number of orders, Total amount spent
SELECT 
    c.customer_name,
    COUNT(o.order_id) AS number_of_orders,
    COALESCE(SUM(o.order_total), 0) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id
ORDER BY total_spent DESC;

-- 6. Driver workload - Driver name, Number of deliveries completed
SELECT 
    d.driver_name,
    COUNT(del.delivery_id) AS deliveries_completed
FROM drivers d
LEFT JOIN deliveries del ON d.driver_id = del.driver_id
GROUP BY d.driver_id
ORDER BY deliveries_completed DESC;

-- 7. Order delivery lookup - search for an order by ID (example with ID 1)
SELECT 
    o.order_id,
    c.customer_name,
    o.order_total,
    del.delivery_date,
    d.driver_name
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN deliveries del ON o.order_id = del.order_id
LEFT JOIN drivers d ON del.driver_id = d.driver_id
WHERE o.order_id = 1;

-- ==================================================
-- Section 3 – Time-based Summaries
-- ==================================================

-- 8. Count the number of orders per order date
SELECT order_date, COUNT(*) AS order_count
FROM orders
GROUP BY order_date
ORDER BY order_date;

-- 9. Count the number of deliveries per delivery date
SELECT delivery_date, COUNT(*) AS delivery_count
FROM deliveries
GROUP BY delivery_date
ORDER BY delivery_date;

-- 10. Count customer signups per month
SELECT 
    strftime('%Y-%m', signup_date) AS signup_month,
    COUNT(*) AS signup_count
FROM customers
GROUP BY signup_month
ORDER BY signup_month;

-- ==================================================
-- Section 4 – Performance and Rankings
-- ==================================================

-- 11. List the top 5 customers by total spend
SELECT 
    c.customer_name,
    SUM(o.order_total) AS total_spend
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id
ORDER BY total_spend DESC
LIMIT 5;

-- 12. Rank drivers by number of deliveries completed
SELECT 
    d.driver_name,
    COUNT(del.delivery_id) AS deliveries_completed,
    RANK() OVER (ORDER BY COUNT(del.delivery_id) DESC) AS rank
FROM drivers d
LEFT JOIN deliveries del ON d.driver_id = del.driver_id
GROUP BY d.driver_id
ORDER BY deliveries_completed DESC;

-- 13. Display all orders above a threshold (e.g. £100)
SELECT 
    o.order_id,
    c.customer_name,
    o.order_total,
    o.order_date
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_total > 100
ORDER BY o.order_total DESC;
