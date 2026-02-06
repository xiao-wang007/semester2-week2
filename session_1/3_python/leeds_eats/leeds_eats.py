import sqlite3

# ==================================================
# Section 1 – Summaries
# ==================================================

def total_customers(conn):
    query = "SELECT COUNT(*) AS total_customers FROM customers;"
    cursor = conn.execute(query)
    result = cursor.fetchone()
    print(f"Total customers: {result[0]}")


def customer_signup_range(conn):
    query = "SELECT MIN(signup_date) AS earliest, MAX(signup_date) AS latest FROM customers;"
    cursor = conn.execute(query)
    result = cursor.fetchone()
    print(f"Earliest signup: {result[0]}\nLatest signup: {result[1]}")


def order_summary_stats(conn):
    query = '''
        SELECT 
            COUNT(*) AS total_orders,
            AVG(order_total) AS average_order_value,
            MAX(order_total) AS highest_order,
            MIN(order_total) AS lowest_order
        FROM orders;
    '''
    cursor = conn.execute(query)
    result = cursor.fetchone()
    print(f"Total orders: {result[0]}")
    print(f"Average order value: £{result[1]:.2f}")
    print(f"Highest order: £{result[2]:.2f}")
    print(f"Lowest order: £{result[3]:.2f}")


def driver_summary(conn):
    count_query = "SELECT COUNT(*) FROM drivers;"
    cursor = conn.execute(count_query)
    total = cursor.fetchone()[0]
    print(f"Total drivers: {total}\n")
    
    query = "SELECT driver_name, hire_date FROM drivers ORDER BY hire_date;"
    cursor = conn.execute(query)
    print("Driver Hire Dates:")
    for driver in cursor:
        print(f"  {driver[0]}\t{driver[1]}")


# ==================================================
# Section 2 – Key Statistics
# ==================================================

def orders_per_customer(conn):
    query = '''
        SELECT 
            c.customer_name,
            COUNT(o.order_id) AS number_of_orders,
            COALESCE(SUM(o.order_total), 0) AS total_spent
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id
        ORDER BY total_spent DESC;
    '''
    cursor = conn.execute(query)
    print("Customer\t\tOrders\tTotal Spent")
    print("-" * 45)
    for row in cursor:
        print(f"{row[0]}\t\t{row[1]}\t£{row[2]:.2f}")


def driver_workload(conn):
    query = '''
        SELECT 
            d.driver_name,
            COUNT(del.delivery_id) AS deliveries_completed
        FROM drivers d
        LEFT JOIN deliveries del ON d.driver_id = del.driver_id
        GROUP BY d.driver_id
        ORDER BY deliveries_completed DESC;
    '''
    cursor = conn.execute(query)
    print("Driver\t\t\tDeliveries")
    print("-" * 35)
    for row in cursor:
        print(f"{row[0]}\t\t{row[1]}")


def delivery_lookup_by_id(conn, order_id):
    query = '''
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
        WHERE o.order_id = ?;
    '''
    cursor = conn.execute(query, (order_id,))
    result = cursor.fetchone()
    if result:
        print(f"Order ID: {result[0]}")
        print(f"Customer: {result[1]}")
        print(f"Order Total: £{result[2]:.2f}")
        print(f"Delivery Date: {result[3] if result[3] else 'Not delivered yet'}")
        print(f"Driver: {result[4] if result[4] else 'Not assigned'}")
    else:
        print(f"Order {order_id} not found.")


# ==================================================
# Section 3 – Time-based Summaries
# ==================================================

def orders_per_date(conn):
    query = '''
        SELECT order_date, COUNT(*) AS order_count
        FROM orders
        GROUP BY order_date
        ORDER BY order_date;
    '''
    cursor = conn.execute(query)
    print("Date\t\tOrders")
    print("-" * 25)
    for row in cursor:
        print(f"{row[0]}\t{row[1]}")


def deliveries_per_date(conn):
    query = '''
        SELECT delivery_date, COUNT(*) AS delivery_count
        FROM deliveries
        GROUP BY delivery_date
        ORDER BY delivery_date;
    '''
    cursor = conn.execute(query)
    print("Date\t\tDeliveries")
    print("-" * 25)
    for row in cursor:
        print(f"{row[0]}\t{row[1]}")


def customer_signups_per_month(conn):
    query = '''
        SELECT 
            strftime('%Y-%m', signup_date) AS signup_month,
            COUNT(*) AS signup_count
        FROM customers
        GROUP BY signup_month
        ORDER BY signup_month;
    '''
    cursor = conn.execute(query)
    print("Month\t\tSignups")
    print("-" * 25)
    for row in cursor:
        print(f"{row[0]}\t{row[1]}")


# ==================================================
# Section 4 – Performance and Rankings
# ==================================================

def top_customers_by_spend(conn, limit=5):
    query = '''
        SELECT 
            c.customer_name,
            SUM(o.order_total) AS total_spend
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id
        ORDER BY total_spend DESC
        LIMIT ?;
    '''
    cursor = conn.execute(query, (limit,))
    print(f"Top {limit} Customers by Spend")
    print("-" * 35)
    rank = 1
    for row in cursor:
        print(f"{rank}. {row[0]}\t£{row[1]:.2f}")
        rank += 1


def rank_drivers_by_deliveries(conn):
    query = '''
        SELECT 
            d.driver_name,
            COUNT(del.delivery_id) AS deliveries_completed
        FROM drivers d
        LEFT JOIN deliveries del ON d.driver_id = del.driver_id
        GROUP BY d.driver_id
        ORDER BY deliveries_completed DESC;
    '''
    cursor = conn.execute(query)
    print("Rank\tDriver\t\tDeliveries")
    print("-" * 40)
    rank = 1
    for row in cursor:
        print(f"{rank}\t{row[0]}\t\t{row[1]}")
        rank += 1


def high_value_orders(conn, threshold):
    query = '''
        SELECT 
            o.order_id,
            c.customer_name,
            o.order_total,
            o.order_date
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_total > ?
        ORDER BY o.order_total DESC;
    '''
    cursor = conn.execute(query, (threshold,))
    print(f"Orders above £{threshold:.2f}")
    print("-" * 50)
    print("ID\tCustomer\t\tTotal\t\tDate")
    count = 0
    for row in cursor:
        print(f"{row[0]}\t{row[1]}\t\t£{row[2]:.2f}\t\t{row[3]}")
        count += 1
    if count == 0:
        print("No orders found above this threshold.")


# ==================================================
# Menus - You should not need to change any code below this point until the stretch tasks.
# ==================================================

def section_1_menu(conn):
    while True:
        print("\nSection 1 – Summaries")
        print("1. Total number of customers")
        print("2. Customer signup date range")
        print("3. Order summary statistics")
        print("4. Driver summary")
        print("0. Back to main menu")

        choice = input("Select an option: ")

        if choice == "1":
            total_customers(conn)
        elif choice == "2":
            customer_signup_range(conn)
        elif choice == "3":
            order_summary_stats(conn)
        elif choice == "4":
            driver_summary(conn)
        elif choice == "0":
            break
        else:
            print("Invalid option. Please try again.")


def section_2_menu(conn):
    while True:
        print("\nSection 2 – Key Statistics")
        print("1. Orders per customer")
        print("2. Driver workload")
        print("3. Order delivery overview")
        print("0. Back to main menu")

        choice = input("Select an option: ")

        if choice == "1":
            orders_per_customer(conn)
        elif choice == "2":
            driver_workload(conn)
        elif choice == "3":
            order_id = input("Enter order ID: ").strip()
            if not order_id.isdigit():
                print("Please enter a valid integer order ID.")
                continue
            delivery_lookup_by_id(conn, int(order_id))
        elif choice == "0":
            break
        else:
            print("Invalid option. Please try again.")


def section_3_menu(conn):
    while True:
        print("\nSection 3 – Time-based Summaries")
        print("1. Orders per date")
        print("2. Deliveries per date")
        print("3. Customer signups per month")
        print("0. Back to main menu")

        choice = input("Select an option: ")

        if choice == "1":
            orders_per_date(conn)
        elif choice == "2":
            deliveries_per_date(conn)
        elif choice == "3":
            customer_signups_per_month(conn)
        elif choice == "0":
            break
        else:
            print("Invalid option. Please try again.")


def section_4_menu(conn):
    while True:
        print("\nSection 4 – Performance and Rankings")
        print("1. Top 5 customers by total spend")
        print("2. Rank drivers by deliveries completed")
        print("3. High-value orders")
        print("0. Back to main menu")

        choice = input("Select an option: ")

        if choice == "1":
            top_customers_by_spend(conn)
        elif choice == "2":
            rank_drivers_by_deliveries(conn)
        elif choice == "3":
            try:
                threshold = float(input("Enter order value threshold (£): "))
                high_value_orders(conn, threshold)
            except:
                print("Please enter a valid numerical value.")
        elif choice == "0":
            break
        else:
            print("Invalid option. Please try again.")


def main_menu(conn):
    while True:
        print("\n=== Delivery Service Management Dashboard ===")
        print("1. Section 1 – Summaries")
        print("2. Section 2 – Key Statistics")
        print("3. Section 3 – Time-based Summaries")
        print("4. Section 4 – Performance and Rankings")
        print("0. Exit")

        choice = input("Select an option: ")

        if choice == "1":
            section_1_menu(conn)
        elif choice == "2":
            section_2_menu(conn)
        elif choice == "3":
            section_3_menu(conn)
        elif choice == "4":
            section_4_menu(conn)
        elif choice == "0":
            print("Exiting dashboard.")
            break
        else:
            print("Invalid option. Please try again.")

def get_connection(db_path="food_delivery.db"):
    """
    Establish a connection to the SQLite database.
    Returns a connection object.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == "__main__":
    conn = get_connection()
    main_menu(conn)
    conn.close()