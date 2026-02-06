import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from itertools import combinations

def get_connection(db_path="orders.db"):
    """
    Establish a connection to the SQLite database.
    Returns a connection object.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# =============================================================================
# LEVEL 1 - WARM-UP TASKS
# =============================================================================

def task1_list_categories(conn):
    """1. List all product categories in the database."""
    query = "SELECT DISTINCT category FROM products ORDER BY category"
    df = pd.read_sql_query(query, conn)
    print("\n=== Task 1: All Product Categories ===")
    for i, row in df.iterrows():
        print(f"  - {row['category']}")
    return df


def task2_count_customers(conn):
    """2. Count the total number of customers."""
    query = "SELECT COUNT(*) as total_customers FROM customers"
    df = pd.read_sql_query(query, conn)
    print(f"\n=== Task 2: Total Number of Customers ===")
    print(f"  Total customers: {df['total_customers'].iloc[0]}")
    return df


def task3_orders_for_customer(conn, email):
    """3. Show all orders for a given customer (by email)."""
    query = """
        SELECT o.order_id, o.order_date, o.status, o.total_amount,
               c.first_name, c.last_name
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE c.email = ?
        ORDER BY o.order_date DESC
    """
    df = pd.read_sql_query(query, conn, params=(email,))
    print(f"\n=== Task 3: Orders for {email} ===")
    if df.empty:
        print("  No orders found for this customer.")
    else:
        print(df.to_string(index=False))
    return df


def task4_products_below_price(conn, price=2.0):
    """4. Display all products priced below a given amount (default £2)."""
    query = """
        SELECT name, category, price
        FROM products
        WHERE price < ?
        ORDER BY price
    """
    df = pd.read_sql_query(query, conn, params=(price,))
    print(f"\n=== Task 4: Products Priced Below £{price} ===")
    print(df.to_string(index=False))
    return df


# =============================================================================
# LEVEL 2 - BASIC ANALYTICS
# =============================================================================

def task5_total_spent_per_customer(conn, top_n=5):
    """5. Compute total spent per customer. Display the top N spenders."""
    query = """
        SELECT c.customer_id, c.first_name, c.last_name, c.email,
               SUM(o.total_amount) as total_spent
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id
        ORDER BY total_spent DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(top_n,))
    print(f"\n=== Task 5: Top {top_n} Spenders ===")
    print(df.to_string(index=False))
    return df


def task6_orders_per_category(conn, show_plot=True):
    """6. Count orders per product category, show in descending order and plot."""
    query = """
        SELECT p.category, COUNT(DISTINCT oi.order_id) as order_count
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        GROUP BY p.category
        ORDER BY order_count DESC
    """
    df = pd.read_sql_query(query, conn)
    print("\n=== Task 6: Orders per Product Category ===")
    print(df.to_string(index=False))
    
    if show_plot:
        plt.figure(figsize=(10, 6))
        plt.bar(df['category'], df['order_count'], color='steelblue')
        plt.xlabel('Category')
        plt.ylabel('Number of Orders')
        plt.title('Orders per Product Category')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('task6_orders_per_category.png')
        plt.show()
    return df


def task7_avg_products_per_order(conn):
    """7. Calculate average number of products per order."""
    query = """
        SELECT AVG(item_count) as avg_products_per_order
        FROM (
            SELECT order_id, SUM(quantity) as item_count
            FROM order_items
            GROUP BY order_id
        )
    """
    df = pd.read_sql_query(query, conn)
    print("\n=== Task 7: Average Products per Order ===")
    print(f"  Average: {df['avg_products_per_order'].iloc[0]:.2f} products per order")
    return df


def task8_deliveries_by_status(conn, show_plot=True):
    """8. Summarize deliveries by status and plot a pie chart."""
    query = """
        SELECT delivery_status, COUNT(*) as count
        FROM deliveries
        GROUP BY delivery_status
    """
    df = pd.read_sql_query(query, conn)
    print("\n=== Task 8: Deliveries by Status ===")
    print(df.to_string(index=False))
    
    if show_plot:
        plt.figure(figsize=(8, 8))
        colors = {'scheduled': 'gold', 'delivered': 'green', 'failed': 'red'}
        plt.pie(df['count'], labels=df['delivery_status'], autopct='%1.1f%%',
                colors=[colors.get(s, 'gray') for s in df['delivery_status']])
        plt.title('Deliveries by Status')
        plt.savefig('task8_deliveries_by_status.png')
        plt.show()
    return df


# =============================================================================
# LEVEL 3 - INTERMEDIATE / ADVANCED
# =============================================================================

def task9_top_products_by_quantity(conn, top_n=10):
    """9. List the top N most popular products by quantity sold."""
    query = """
        SELECT p.product_id, p.name, p.category, SUM(oi.quantity) as total_sold
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        GROUP BY p.product_id
        ORDER BY total_sold DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(top_n,))
    print(f"\n=== Task 9: Top {top_n} Most Popular Products ===")
    print(df.to_string(index=False))
    return df


def task10_revenue_per_category(conn, show_plot=True):
    """10. Compute total revenue per category and visualize."""
    query = """
        SELECT p.category, SUM(oi.quantity * oi.unit_price) as total_revenue
        FROM products p
        JOIN order_items oi ON p.product_id = oi.product_id
        GROUP BY p.category
        ORDER BY total_revenue DESC
    """
    df = pd.read_sql_query(query, conn)
    print("\n=== Task 10: Revenue per Category ===")
    print(df.to_string(index=False))
    
    if show_plot:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Bar chart
        axes[0].bar(df['category'], df['total_revenue'], color='steelblue')
        axes[0].set_xlabel('Category')
        axes[0].set_ylabel('Total Revenue (£)')
        axes[0].set_title('Revenue per Category (Bar Chart)')
        axes[0].tick_params(axis='x', rotation=45)
        
        # Pie chart
        axes[1].pie(df['total_revenue'], labels=df['category'], autopct='%1.1f%%')
        axes[1].set_title('Revenue per Category (Pie Chart)')
        
        plt.tight_layout()
        plt.savefig('task10_revenue_per_category.png')
        plt.show()
    return df


def task11_orders_per_delivery_window(conn, show_plot=True):
    """11. Count orders per delivery time window and visualize busiest slots."""
    query = """
        SELECT delivery_window, COUNT(*) as order_count
        FROM deliveries
        GROUP BY delivery_window
        ORDER BY order_count DESC
    """
    df = pd.read_sql_query(query, conn)
    print("\n=== Task 11: Orders per Delivery Window ===")
    print(df.to_string(index=False))
    
    if show_plot:
        plt.figure(figsize=(10, 6))
        plt.bar(df['delivery_window'], df['order_count'], color='coral')
        plt.xlabel('Delivery Window')
        plt.ylabel('Number of Orders')
        plt.title('Orders per Delivery Time Window')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('task11_orders_per_window.png')
        plt.show()
    return df


def task12_top_customers_by_avg_order(conn, top_n=10):
    """12. Identify top customers by average order value."""
    query = """
        SELECT c.customer_id, c.first_name, c.last_name, c.email,
               AVG(o.total_amount) as avg_order_value,
               COUNT(o.order_id) as order_count
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id
        HAVING order_count >= 1
        ORDER BY avg_order_value DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(top_n,))
    print(f"\n=== Task 12: Top {top_n} Customers by Average Order Value ===")
    print(df.to_string(index=False))
    return df


def task13_delivery_performance_by_window(conn, show_plot=True):
    """13. Compute delivery performance by time window: delivered vs failed."""
    query = """
        SELECT delivery_window, delivery_status, COUNT(*) as count
        FROM deliveries
        GROUP BY delivery_window, delivery_status
        ORDER BY delivery_window
    """
    df = pd.read_sql_query(query, conn)
    
    # Pivot for easier visualization
    pivot_df = df.pivot(index='delivery_window', columns='delivery_status', values='count').fillna(0)
    
    print("\n=== Task 13: Delivery Performance by Time Window ===")
    print(pivot_df.to_string())
    
    if show_plot:
        pivot_df.plot(kind='bar', figsize=(12, 6), color=['red', 'green', 'gold'])
        plt.xlabel('Delivery Window')
        plt.ylabel('Number of Orders')
        plt.title('Delivery Performance by Time Window')
        plt.legend(title='Status')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('task13_delivery_performance.png')
        plt.show()
    return pivot_df


# =============================================================================
# LEVEL 4 - STRETCH / CHALLENGE
# =============================================================================

def task14_repeat_purchase_rate(conn):
    """14. Find customers with more than one order and compute repeat purchase rate."""
    # Get customers with order counts
    query = """
        SELECT c.customer_id, c.first_name, c.last_name, c.email,
               COUNT(o.order_id) as order_count
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id
    """
    df = pd.read_sql_query(query, conn)
    
    total_customers_with_orders = len(df)
    repeat_customers = df[df['order_count'] > 1]
    repeat_rate = len(repeat_customers) / total_customers_with_orders * 100 if total_customers_with_orders > 0 else 0
    
    print("\n=== Task 14: Repeat Purchase Rate ===")
    print(f"  Total customers with orders: {total_customers_with_orders}")
    print(f"  Repeat customers (>1 order): {len(repeat_customers)}")
    print(f"  Repeat purchase rate: {repeat_rate:.2f}%")
    print("\nRepeat customers:")
    print(repeat_customers.to_string(index=False))
    return repeat_customers, repeat_rate


def task15_category_cooccurrence(conn, show_plot=True):
    """15. Determine category co-occurrence: which categories are frequently ordered together."""
    query = """
        SELECT oi.order_id, p.category
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
    """
    df = pd.read_sql_query(query, conn)
    
    # Get unique categories per order
    order_categories = df.groupby('order_id')['category'].apply(lambda x: list(set(x))).reset_index()
    
    # Count co-occurrences
    categories = df['category'].unique()
    cooccurrence = pd.DataFrame(0, index=categories, columns=categories)
    
    for _, row in order_categories.iterrows():
        cats = row['category']
        for cat in cats:
            cooccurrence.loc[cat, cat] += 1
        for cat1, cat2 in combinations(cats, 2):
            cooccurrence.loc[cat1, cat2] += 1
            cooccurrence.loc[cat2, cat1] += 1
    
    print("\n=== Task 15: Category Co-occurrence Matrix ===")
    print(cooccurrence.to_string())
    
    if show_plot:
        plt.figure(figsize=(12, 10))
        plt.imshow(cooccurrence.values, cmap='YlOrRd', aspect='auto')
        plt.colorbar(label='Co-occurrence Count')
        plt.xticks(range(len(categories)), categories, rotation=45, ha='right')
        plt.yticks(range(len(categories)), categories)
        plt.title('Category Co-occurrence Heatmap')
        
        # Add text annotations
        for i in range(len(categories)):
            for j in range(len(categories)):
                plt.text(j, i, int(cooccurrence.iloc[i, j]), ha='center', va='center', fontsize=8)
        
        plt.tight_layout()
        plt.savefig('task15_cooccurrence_heatmap.png')
        plt.show()
    return cooccurrence


def task16_delivery_performance_by_customer(conn, show_plot=True):
    """16. Identify delivery performance by customer: proportion of delivered vs failed."""
    query = """
        SELECT c.customer_id, c.first_name, c.last_name,
               d.delivery_status, COUNT(*) as count
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN deliveries d ON o.order_id = d.order_id
        GROUP BY c.customer_id, d.delivery_status
    """
    df = pd.read_sql_query(query, conn)
    
    # Pivot and calculate percentages
    pivot_df = df.pivot_table(index=['customer_id', 'first_name', 'last_name'], 
                              columns='delivery_status', values='count', 
                              aggfunc='sum', fill_value=0)
    
    pivot_df['total'] = pivot_df.sum(axis=1)
    for col in ['delivered', 'failed', 'scheduled']:
        if col in pivot_df.columns:
            pivot_df[f'{col}_pct'] = (pivot_df[col] / pivot_df['total'] * 100).round(2)
    
    pivot_df = pivot_df.reset_index()
    
    print("\n=== Task 16: Delivery Performance by Customer ===")
    print(pivot_df.to_string(index=False))
    
    if show_plot and 'delivered_pct' in pivot_df.columns:
        # Show top 20 customers by total orders
        top_customers = pivot_df.nlargest(20, 'total')
        
        fig, ax = plt.subplots(figsize=(14, 8))
        x = range(len(top_customers))
        width = 0.25
        
        for i, status in enumerate(['delivered', 'failed', 'scheduled']):
            if status in top_customers.columns:
                ax.bar([xi + i*width for xi in x], top_customers[status], 
                       width, label=status.capitalize())
        
        ax.set_xlabel('Customer')
        ax.set_ylabel('Number of Orders')
        ax.set_title('Delivery Performance by Customer (Top 20)')
        ax.set_xticks([xi + width for xi in x])
        ax.set_xticklabels([f"{r['first_name']}" for _, r in top_customers.iterrows()], 
                          rotation=45, ha='right')
        ax.legend()
        plt.tight_layout()
        plt.savefig('task16_delivery_by_customer.png')
        plt.show()
    return pivot_df


def task17_forecast_revenue(conn, show_plot=True):
    """17. Forecast expected revenue for the next 7 days based on past month's orders."""
    # Get daily revenue for the past month
    query = """
        SELECT DATE(order_date) as date, SUM(total_amount) as daily_revenue
        FROM orders
        WHERE order_date >= DATE('now', '-30 days')
        GROUP BY DATE(order_date)
        ORDER BY date
    """
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        # If no recent data, use all available data
        query = """
            SELECT DATE(order_date) as date, SUM(total_amount) as daily_revenue
            FROM orders
            GROUP BY DATE(order_date)
            ORDER BY date
        """
        df = pd.read_sql_query(query, conn)
    
    print("\n=== Task 17: Revenue Forecast ===")
    
    if len(df) < 2:
        print("  Not enough data to forecast.")
        return None
    
    # Simple moving average forecast
    avg_daily_revenue = df['daily_revenue'].mean()
    forecast_7_days = avg_daily_revenue * 7
    
    print(f"  Historical daily average: £{avg_daily_revenue:.2f}")
    print(f"  Forecast for next 7 days: £{forecast_7_days:.2f}")
    
    # Show trend
    print("\n  Recent daily revenues:")
    print(df.tail(10).to_string(index=False))
    
    if show_plot:
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot historical data
        dates = pd.to_datetime(df['date'])
        ax.plot(dates, df['daily_revenue'], 'b-o', label='Historical')
        
        # Add forecast line
        if len(dates) > 0:
            last_date = dates.max()
            forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=7)
            ax.plot(forecast_dates, [avg_daily_revenue]*7, 'r--s', label='Forecast (Avg)')
            ax.axhline(y=avg_daily_revenue, color='gray', linestyle=':', alpha=0.5)
        
        ax.set_xlabel('Date')
        ax.set_ylabel('Daily Revenue (£)')
        ax.set_title('Daily Revenue with 7-Day Forecast')
        ax.legend()
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('task17_revenue_forecast.png')
        plt.show()
    
    return df, forecast_7_days


# =============================================================================
# LEVEL 5 - ANALYSIS DASHBOARD
# =============================================================================

def dashboard_orders_overview(conn):
    """Dashboard section: Orders Overview."""
    print("\n" + "="*60)
    print("📊 ORDERS OVERVIEW")
    print("="*60)
    
    # Total orders
    total_orders = pd.read_sql_query("SELECT COUNT(*) as count FROM orders", conn)['count'].iloc[0]
    
    # Orders by status
    status_df = pd.read_sql_query("""
        SELECT status, COUNT(*) as count FROM orders GROUP BY status
    """, conn)
    
    # Average basket size
    avg_basket = pd.read_sql_query("""
        SELECT AVG(item_count) as avg_basket
        FROM (SELECT order_id, SUM(quantity) as item_count FROM order_items GROUP BY order_id)
    """, conn)['avg_basket'].iloc[0]
    
    # Orders per category
    category_df = pd.read_sql_query("""
        SELECT p.category, COUNT(DISTINCT oi.order_id) as orders
        FROM products p JOIN order_items oi ON p.product_id = oi.product_id
        GROUP BY p.category ORDER BY orders DESC
    """, conn)
    
    print(f"  Total Orders: {total_orders}")
    print(f"  Average Basket Size: {avg_basket:.2f} items")
    print("\n  Orders by Status:")
    for _, row in status_df.iterrows():
        print(f"    - {row['status']}: {row['count']}")
    print("\n  Orders by Category:")
    for _, row in category_df.iterrows():
        print(f"    - {row['category']}: {row['orders']}")


def dashboard_revenue_analysis(conn, show_plot=True):
    """Dashboard section: Revenue Analysis."""
    print("\n" + "="*60)
    print("💰 REVENUE ANALYSIS")
    print("="*60)
    
    # Total revenue
    total_revenue = pd.read_sql_query("""
        SELECT SUM(total_amount) as total FROM orders
    """, conn)['total'].iloc[0]
    
    # Revenue per category
    category_revenue = pd.read_sql_query("""
        SELECT p.category, SUM(oi.quantity * oi.unit_price) as revenue
        FROM products p JOIN order_items oi ON p.product_id = oi.product_id
        GROUP BY p.category ORDER BY revenue DESC
    """, conn)
    
    # Top 10 products by revenue
    top_products = pd.read_sql_query("""
        SELECT p.name, p.category, SUM(oi.quantity * oi.unit_price) as revenue
        FROM products p JOIN order_items oi ON p.product_id = oi.product_id
        GROUP BY p.product_id ORDER BY revenue DESC LIMIT 10
    """, conn)
    
    print(f"  Total Revenue: £{total_revenue:.2f}")
    print("\n  Revenue by Category:")
    for _, row in category_revenue.iterrows():
        print(f"    - {row['category']}: £{row['revenue']:.2f}")
    print("\n  Top 10 Products by Revenue:")
    print(top_products.to_string(index=False))
    
    if show_plot:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        axes[0].pie(category_revenue['revenue'], labels=category_revenue['category'], autopct='%1.1f%%')
        axes[0].set_title('Revenue by Category')
        axes[1].barh(top_products['name'], top_products['revenue'], color='green')
        axes[1].set_xlabel('Revenue (£)')
        axes[1].set_title('Top 10 Products by Revenue')
        plt.tight_layout()
        plt.savefig('dashboard_revenue.png')
        plt.show()


def dashboard_customer_insights(conn):
    """Dashboard section: Customer Insights."""
    print("\n" + "="*60)
    print("👥 CUSTOMER INSIGHTS")
    print("="*60)
    
    # Total customers
    total_customers = pd.read_sql_query("SELECT COUNT(*) as count FROM customers", conn)['count'].iloc[0]
    
    # Top 5 spenders
    top_spenders = pd.read_sql_query("""
        SELECT c.first_name, c.last_name, SUM(o.total_amount) as total_spent
        FROM customers c JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id ORDER BY total_spent DESC LIMIT 5
    """, conn)
    
    # Repeat purchase rate
    order_counts = pd.read_sql_query("""
        SELECT customer_id, COUNT(*) as orders FROM orders GROUP BY customer_id
    """, conn)
    repeat_rate = (len(order_counts[order_counts['orders'] > 1]) / len(order_counts) * 100) if len(order_counts) > 0 else 0
    
    print(f"  Total Customers: {total_customers}")
    print(f"  Repeat Purchase Rate: {repeat_rate:.2f}%")
    print("\n  Top 5 Spenders:")
    for _, row in top_spenders.iterrows():
        print(f"    - {row['first_name']} {row['last_name']}: £{row['total_spent']:.2f}")


def dashboard_delivery_performance(conn, show_plot=True):
    """Dashboard section: Delivery Performance."""
    print("\n" + "="*60)
    print("🚚 DELIVERY PERFORMANCE")
    print("="*60)
    
    # Delivery status summary
    status_df = pd.read_sql_query("""
        SELECT delivery_status, COUNT(*) as count FROM deliveries GROUP BY delivery_status
    """, conn)
    
    # Orders per delivery window
    window_df = pd.read_sql_query("""
        SELECT delivery_window, COUNT(*) as count FROM deliveries 
        GROUP BY delivery_window ORDER BY count DESC
    """, conn)
    
    print("  Delivery Status Summary:")
    for _, row in status_df.iterrows():
        print(f"    - {row['delivery_status']}: {row['count']}")
    
    print("\n  Orders per Delivery Window:")
    for _, row in window_df.iterrows():
        print(f"    - {row['delivery_window']}: {row['count']}")
    
    if show_plot:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        colors = {'scheduled': 'gold', 'delivered': 'green', 'failed': 'red'}
        axes[0].pie(status_df['count'], labels=status_df['delivery_status'], autopct='%1.1f%%',
                   colors=[colors.get(s, 'gray') for s in status_df['delivery_status']])
        axes[0].set_title('Delivery Status')
        axes[1].bar(window_df['delivery_window'], window_df['count'], color='coral')
        axes[1].set_xlabel('Delivery Window')
        axes[1].set_ylabel('Orders')
        axes[1].set_title('Orders per Delivery Window')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('dashboard_delivery.png')
        plt.show()


def run_dashboard(conn):
    """Level 5: Interactive Dashboard."""
    while True:
        print("\n" + "="*60)
        print("🛒 LEEDSBURIES SUPERMARKET DASHBOARD")
        print("="*60)
        print("\nSelect an option:")
        print("  1. Orders Overview")
        print("  2. Revenue Analysis")
        print("  3. Customer Insights")
        print("  4. Delivery Performance")
        print("  5. Full Dashboard (All Sections)")
        print("  6. Run All Level 1-4 Tasks")
        print("  0. Exit")
        
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == '1':
            dashboard_orders_overview(conn)
        elif choice == '2':
            dashboard_revenue_analysis(conn)
        elif choice == '3':
            dashboard_customer_insights(conn)
        elif choice == '4':
            dashboard_delivery_performance(conn)
        elif choice == '5':
            dashboard_orders_overview(conn)
            dashboard_revenue_analysis(conn, show_plot=False)
            dashboard_customer_insights(conn)
            dashboard_delivery_performance(conn, show_plot=False)
        elif choice == '6':
            run_all_tasks(conn, show_plots=False)
        elif choice == '0':
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice. Please try again.")


def run_all_tasks(conn, show_plots=True):
    """Run all tasks from Level 1-4."""
    print("\n" + "#"*60)
    print("# RUNNING ALL TASKS (LEVEL 1-4)")
    print("#"*60)
    
    # Level 1
    print("\n" + "="*60)
    print("LEVEL 1 - WARM-UP")
    print("="*60)
    task1_list_categories(conn)
    task2_count_customers(conn)
    
    # Get a sample email for task 3
    sample_email = pd.read_sql_query("SELECT email FROM customers LIMIT 1", conn)
    if not sample_email.empty:
        task3_orders_for_customer(conn, sample_email['email'].iloc[0])
    
    task4_products_below_price(conn)
    
    # Level 2
    print("\n" + "="*60)
    print("LEVEL 2 - BASIC ANALYTICS")
    print("="*60)
    task5_total_spent_per_customer(conn)
    task6_orders_per_category(conn, show_plot=show_plots)
    task7_avg_products_per_order(conn)
    task8_deliveries_by_status(conn, show_plot=show_plots)
    
    # Level 3
    print("\n" + "="*60)
    print("LEVEL 3 - INTERMEDIATE/ADVANCED")
    print("="*60)
    task9_top_products_by_quantity(conn)
    task10_revenue_per_category(conn, show_plot=show_plots)
    task11_orders_per_delivery_window(conn, show_plot=show_plots)
    task12_top_customers_by_avg_order(conn)
    task13_delivery_performance_by_window(conn, show_plot=show_plots)
    
    # Level 4
    print("\n" + "="*60)
    print("LEVEL 4 - STRETCH/CHALLENGE")
    print("="*60)
    task14_repeat_purchase_rate(conn)
    task15_category_cooccurrence(conn, show_plot=show_plots)
    task16_delivery_performance_by_customer(conn, show_plot=show_plots)
    task17_forecast_revenue(conn, show_plot=show_plots)


def main():
    """Main function - runs the dashboard."""
    conn = get_connection()
    
    try:
        run_dashboard(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
