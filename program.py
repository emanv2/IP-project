import pandas as pd
import os
import datetime

# --- FILE PATH CONFIGURE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "menu.csv")
USERS_FILE = os.path.join(BASE_DIR, "users.csv")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.csv")


# --- DATABASE OPERATIONS USING PANDAS ---

def save_order(order_id, order_cart, menu_df):
    """Logs each item in the cart as a separate row in orders.csv using pandas .loc."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if os.path.exists(ORDERS_FILE):
        orders_df = pd.read_csv(ORDERS_FILE)
    else:
        orders_df = pd.DataFrame(columns=['order_id', 'timestamp', 'item_name', 'quantity', 'price'])
    
    for item_id, qty in order_cart.items():
        item_row = menu_df[menu_df['id'] == item_id].iloc[0]
        item_price = float(item_row['price']) * qty
        orders_df.loc[len(orders_df)] = [order_id, timestamp, item_row['name'], qty, round(item_price, 2)]
    
    orders_df.to_csv(ORDERS_FILE, index=False)


def get_next_order_id():
    """Calculates the next order number based on unique order IDs."""
    if not os.path.exists(ORDERS_FILE):
        return "ORD1"
    
    try:
        orders_df = pd.read_csv(ORDERS_FILE)
        if orders_df.empty:
            return "ORD1"
        unique_order_count = orders_df['order_id'].nunique()
        return f"ORD{unique_order_count + 1}"
    except Exception:
        return "ORD1"


# --- TERMINAL UI FUNCTIONS ---

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def draw_header(title):
    """Draws a frame for section titles."""
    border = "=" * 50
    print(border)
    print(f" {title.upper().center(48)} ")
    print(border)


def display_menu_public():
    """Displays the menu in a table using Pandas grouping."""
    if not os.path.exists(MENU_FILE):
        print("\n[!] The cafe menu is currently empty.")
        return
    
    menu_df = pd.read_csv(MENU_FILE)
    if menu_df.empty:
        print("\n[!] The cafe menu is currently empty.")
        return
    
    print("\n" + "-" * 50)
    print(f"{'ID':<4} | {'Name':<25} | {'Price':<10}")
    print("-" * 50)
    
    categories = menu_df['category'].unique()
    
    for category in categories:
        print(f"\n--- {str(category).upper()} ---")
        category_rows = menu_df[menu_df['category'] == category]
        
        for _, item in category_rows.iterrows():
            print(f"[{int(item['id']):<2}] | {item['name']:<25} | ${float(item['price']):>6.2f}")
            
    print("-" * 50 + "\n")


# --- AUTHENTICATION ---

def login_screen():
    """Asks for credentials, checking users.csv for match"""
    draw_header("Account Login")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    
    if not os.path.exists(USERS_FILE):
        print("\n[!] Database file not found.")
        input()
        return None
    
    users_df = pd.read_csv(USERS_FILE)
    
    users_list = users_df.to_dict('records')
    
    for user in users_list:
        if user['username'] == username and user['password'] == password:
            return user
    
    print("\n[!] Invalid username or password. Press Enter to try again.")
    input()
    return None


# --- EMPLOYEE DASHBOARD & ORDER LOGGING ---

def log_customer_order(employee_user):
    """To select items, calculate sub-total and total, write receipt, and log to file."""
    if not os.path.exists(MENU_FILE):
        print("\n[!] Cafe menu database not found.")
        input("\nPress Enter to return.")
        return
    
    menu_df = pd.read_csv(MENU_FILE)
    if menu_df.empty:
        print("\n[!] Cannot place order. The cafe menu is empty.")
        input("\nPress Enter to return.")
        return
    
    order_cart = {}
    
    while True:
        clear_screen()
        draw_header("Create Customer Order")
        display_menu_public()
        
        if order_cart:
            print("--- CURRENT CART ---")
            temp_total = 0.0
            for item_id, qty in order_cart.items():
                match = menu_df[menu_df['id'] == item_id]
                if not match.empty:
                    item_row = match.iloc[0]
                    subtotal = float(item_row['price']) * qty
                    temp_total += subtotal
                    print(f" * {item_row['name']} x{qty} = ${subtotal:.2f}")
            print(f"Current Total: ${temp_total:.2f}")
            print("-" * 50)
        
        print("\nCommands: Enter 'done' to complete order, or 'cancel' to exit.")
        choice = input("Enter Item ID to add: ").strip().lower()
        
        if choice == 'cancel':
            print("\n[-] Order discarded.")
            input("Press Enter to return.")
            return
        
        if choice == 'done':
            if not order_cart:
                print("\n[!] Cart is empty. Cannot complete order.")
                input("Press Enter to continue.")
                continue
            break
        
        try:
            item_id = int(choice)
        except ValueError:
            print("\n[!] Please enter a valid numerical ID, 'done', or 'cancel'.")
            input("Press Enter to try again.")
            continue
        
        match = menu_df[menu_df['id'] == item_id]
        if match.empty:
            print("\n[!] Item ID not found in menu.")
            input("Press Enter to try again.")
            continue
        
        selected_item = match.iloc[0]
        
        qty_input = input(f"Enter quantity for {selected_item['name']}: ").strip()
        try:
            qty = int(qty_input)
            if qty <= 0:
                print("\n[!] Quantity must be greater than zero.")
                input("Press Enter to try again.")
                continue
        except ValueError:
            print("\n[!] Quantity must be a valid number.")
            input("Press Enter to try again.")
            continue
        
        order_cart[item_id] = order_cart.get(item_id, 0) + qty
        print(f"\n[+] Added {qty}x {selected_item['name']} to cart.")
    
    order_id = get_next_order_id()
    total_price = 0.0
    
    clear_screen()
    draw_header("Order Receipt")
    print(f"Order ID: {order_id}")
    print(f"Server: {employee_user['name']}")
    print(f"Date/Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    print(f"{'Item Name':<25} | {'Qty':<5} | {'Price':<8} | {'Total':<8}")
    print("-" * 50)
    
    for item_id, qty in order_cart.items():
        item_row = menu_df[menu_df['id'] == item_id].iloc[0]
        price = float(item_row['price'])
        subtotal = price * qty
        total_price += subtotal
        print(f"{item_row['name']:<25} | {qty:<5} | ${price:>6.2f} | ${subtotal:>6.2f}")
            
    print("-" * 50)
    print(f"{'GRAND TOTAL:':<40} ${total_price:>7.2f}")
    print("-" * 50)
    
    save_order(order_id, order_cart, menu_df)
    
    print("\n[+] Order successfully logged and saved to database.")
    input("\nPress Enter to return to Employee Menu.")


def employee_dashboard(employee_user):
    """Menu displayed only to authenticated Employee users."""
    while True:
        clear_screen()
        draw_header(f"Employee Dashboard: {employee_user['name']}")
        print("1. Log New Customer Order")
        print("2. Logout")
        print("-" * 50)
        
        choice = input("Select an option (1-2): ").strip()
        
        if choice == "1":
            log_customer_order(employee_user)
        elif choice == "2":
            print("\nLogging out...")
            break
        else:
            print("\n[!] Invalid input. Press Enter to retry.")
            input()


# --- ADMIN DASHBOARD & MANAGEMENT ---


def _read_menu():
    if not os.path.exists(MENU_FILE):
        return pd.DataFrame(columns=['id', 'name', 'price', 'category'])
    try:
        return pd.read_csv(MENU_FILE)
    except Exception:
        return pd.DataFrame(columns=['id', 'name', 'price', 'category'])


def _save_menu(menu_df):
    menu_df.to_csv(MENU_FILE, index=False)


def _read_users():
    if not os.path.exists(USERS_FILE):
        return pd.DataFrame(columns=['username', 'password', 'role', 'name', 'hourly_wage', 'contact_number'])
    try:
        return pd.read_csv(USERS_FILE)
    except Exception:
        return pd.DataFrame(columns=['username', 'password', 'role', 'name', 'hourly_wage', 'contact_number'])


def _save_users(users_df):
    users_df.to_csv(USERS_FILE, index=False)


def add_menu_item():
    clear_screen()
    draw_header("Add Menu Item")
    name = input("Item name: ").strip()
    if not name:
        print("\n[!] Name cannot be empty.")
        input("Press Enter to return.")
        return
    price_input = input("Price: ").strip()
    try:
        price = float(price_input)
        if price <= 0:
            raise ValueError
    except ValueError:
        print("\n[!] Price must be a positive number.")
        input("Press Enter to return.")
        return
    category = input("Category: ").strip()
    if not category:
        print("\n[!] Category cannot be empty.")
        input("Press Enter to return.")
        return

    menu_df = _read_menu()
    if menu_df.empty:
        new_id = 1
    else:
        new_id = int(menu_df['id'].max()) + 1

    new_row = pd.DataFrame([[new_id, name, round(price, 2), category]],
                           columns=['id', 'name', 'price', 'category'])
    menu_df = pd.concat([menu_df, new_row], ignore_index=True)
    _save_menu(menu_df)
    print(f"\n[+] Added item '{name}' with ID {new_id}.")
    input("Press Enter to return.")


def edit_menu_item():
    clear_screen()
    draw_header("Edit Menu Item")
    menu_df = _read_menu()
    if menu_df.empty:
        print("\n[!] Menu is empty.")
        input("Press Enter to return.")
        return
    display_menu_public()
    id_input = input("Enter Item ID to edit: ").strip()
    try:
        item_id = int(id_input)
    except ValueError:
        print("\n[!] Invalid ID.")
        input("Press Enter to return.")
        return
    mask = menu_df['id'] == item_id
    if not mask.any():
        print("\n[!] Item ID not found.")
        input("Press Enter to return.")
        return

    idx = menu_df[mask].index[0]
    current = menu_df.loc[idx]
    print(f"\nCurrent: {current['name']} | ${float(current['price']):.2f} | {current['category']}")
    print("Leave a field blank to keep its current value.")

    new_name = input(f"New name [{current['name']}]: ").strip()
    new_price_input = input(f"New price [{float(current['price']):.2f}]: ").strip()
    new_category = input(f"New category [{current['category']}]: ").strip()

    if new_name:
        menu_df.at[idx, 'name'] = new_name
    if new_price_input:
        try:
            new_price = float(new_price_input)
            if new_price <= 0:
                raise ValueError
            menu_df.at[idx, 'price'] = round(new_price, 2)
        except ValueError:
            print("\n[!] Invalid price. Edit cancelled.")
            input("Press Enter to return.")
            return
    if new_category:
        menu_df.at[idx, 'category'] = new_category

    _save_menu(menu_df)
    print("\n[+] Item updated.")
    input("Press Enter to return.")


def delete_menu_item():
    clear_screen()
    draw_header("Delete Menu Item")
    menu_df = _read_menu()
    if menu_df.empty:
        print("\n[!] Menu is empty.")
        input("Press Enter to return.")
        return
    display_menu_public()
    id_input = input("Enter Item ID to delete: ").strip()
    try:
        item_id = int(id_input)
    except ValueError:
        print("\n[!] Invalid ID.")
        input("Press Enter to return.")
        return
    mask = menu_df['id'] == item_id
    if not mask.any():
        print("\n[!] Item ID not found.")
        input("Press Enter to return.")
        return

    item_name = menu_df.loc[mask, 'name'].iloc[0]
    confirm = input(f"Delete '{item_name}'? (y/n): ").strip().lower()
    if confirm != 'y':
        print("\n[-] Cancelled.")
        input("Press Enter to return.")
        return

    menu_df = menu_df[~mask].reset_index(drop=True)
    _save_menu(menu_df)
    print("\n[+] Item deleted.")
    input("Press Enter to return.")


def add_user():
    clear_screen()
    draw_header("Add User")
    users_df = _read_users()
    username = input("Username: ").strip()
    if not username:
        print("\n[!] Username cannot be empty.")
        input("Press Enter to return.")
        return
    if (not users_df.empty) and (username in users_df['username'].astype(str).values):
        print("\n[!] Username already exists.")
        input("Press Enter to return.")
        return
    password = input("Password: ").strip()
    if not password:
        print("\n[!] Password cannot be empty.")
        input("Press Enter to return.")
        return
    name = input("Name: ").strip()
    if not name:
        print("\n[!] Name cannot be empty.")
        input("Press Enter to return.")
        return
    print("Role: 1. Admin  2. Employee")
    role_choice = input("Select role (1-2): ").strip()
    if role_choice == "1":
        role = "admin"
    elif role_choice == "2":
        role = "employee"
    else:
        print("\n[!] Invalid role.")
        input("Press Enter to return.")
        return

    new_row = pd.DataFrame([[username, password, role, name, 0.0, "N/A"]],
                           columns=['username', 'password', 'role', 'name', 'hourly_wage', 'contact_number'])
    users_df = pd.concat([users_df, new_row], ignore_index=True)
    _save_users(users_df)
    print(f"\n[+] User '{username}' added as {role}.")
    input("Press Enter to return.")


def view_users():
    clear_screen()
    draw_header("All Users")
    users_df = _read_users()
    if users_df.empty:
        print("\n[!] No users found.")
        input("Press Enter to return.")
        return
    print(f"{'Username':<15} | {'Name':<20} | {'Role':<10}")
    print("-" * 50)
    for _, u in users_df.iterrows():
        print(f"{str(u['username']):<15} | {str(u['name']):<20} | {str(u['role']):<10}")
    print("-" * 50)
    input("Press Enter to return.")


def remove_user():
    clear_screen()
    draw_header("Remove User")
    users_df = _read_users()
    if users_df.empty:
        print("\n[!] No users found.")
        input("Press Enter to return.")
        return
    view_users_inline(users_df)
    username = input("Enter username to remove: ").strip()
    if (users_df.empty) or (username not in users_df['username'].astype(str).values):
        print("\n[!] User not found.")
        input("Press Enter to return.")
        return
    confirm = input(f"Remove user '{username}'? (y/n): ").strip().lower()
    if confirm != 'y':
        print("\n[-] Cancelled.")
        input("Press Enter to return.")
        return
    users_df = users_df[users_df['username'].astype(str) != username].reset_index(drop=True)
    _save_users(users_df)
    print("\n[+] User removed.")
    input("Press Enter to return.")


def view_users_inline(users_df):
    print(f"{'Username':<15} | {'Name':<20} | {'Role':<10}")
    print("-" * 50)
    for _, u in users_df.iterrows():
        print(f"{str(u['username']):<15} | {str(u['name']):<20} | {str(u['role']):<10}")
    print("-" * 50)


def change_user_role():
    clear_screen()
    draw_header("Change User Role")
    users_df = _read_users()
    if users_df.empty:
        print("\n[!] No users found.")
        input("Press Enter to return.")
        return
    view_users_inline(users_df)
    username = input("Enter username: ").strip()
    if username not in users_df['username'].astype(str).values:
        print("\n[!] User not found.")
        input("Press Enter to return.")
        return
    print("New role: 1. Admin  2. Employee")
    role_choice = input("Select role (1-2): ").strip()
    if role_choice == "1":
        new_role = "admin"
    elif role_choice == "2":
        new_role = "employee"
    else:
        print("\n[!] Invalid role.")
        input("Press Enter to return.")
        return
    idx = users_df[users_df['username'].astype(str) == username].index[0]
    users_df.at[idx, 'role'] = new_role
    _save_users(users_df)
    print(f"\n[+] Role updated to {new_role}.")
    input("Press Enter to return.")


def view_all_orders():
    clear_screen()
    draw_header("All Orders")
    if not os.path.exists(ORDERS_FILE):
        print("\n[!] No orders found.")
        input("Press Enter to return.")
        return
    try:
        orders_df = pd.read_csv(ORDERS_FILE)
    except Exception:
        print("\n[!] Could not read orders file.")
        input("Press Enter to return.")
        return
    if orders_df.empty:
        print("\n[!] No orders found.")
        input("Press Enter to return.")
        return
    print(orders_df.to_string(index=False))
    print("-" * 50)
    try:
        total = orders_df['price'].astype(float).sum()
        print(f"Total revenue (sum of line prices): ${total:.2f}")
    except Exception:
        pass
    input("\nPress Enter to return.")


def view_sales_charts():
    clear_screen()
    draw_header("Sales Charts")
    if not os.path.exists(ORDERS_FILE):
        print("\n[!] No orders found.")
        input("Press Enter to return.")
        return
    try:
        orders_df = pd.read_csv(ORDERS_FILE)
    except Exception:
        print("\n[!] Could not read orders file.")
        input("Press Enter to return.")
        return
    if orders_df.empty:
        print("\n[!] No orders found.")
        input("Press Enter to return.")
        return

    try:
        import matplotlib.pyplot as plt
    except Exception as e:
        print(f"\n[!] matplotlib not available: {e}")
        input("Press Enter to return.")
        return

    # Top-selling items by quantity
    item_qty = orders_df.groupby('item_name')['quantity'].sum().sort_values(ascending=True)
    # Revenue over time by day
    orders_df['timestamp'] = pd.to_datetime(orders_df['timestamp'], errors='coerce')
    revenue_by_day = orders_df.dropna(subset=['timestamp']).groupby(orders_df['timestamp'].dt.date)['price'].sum()

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Bar chart: top-selling items
    axes[0].barh(item_qty.index, item_qty.values, color='steelblue')
    axes[0].set_title('Top-Selling Items (by quantity)')
    axes[0].set_xlabel('Quantity sold')
    axes[0].set_ylabel('Item')

    # Line chart: revenue over time
    if not revenue_by_day.empty:
        axes[1].plot(list(revenue_by_day.index), list(revenue_by_day.values), marker='o', color='darkorange')
        axes[1].set_title('Revenue Over Time')
        axes[1].set_xlabel('Date')
        axes[1].set_ylabel('Revenue ($)')
        axes[1].tick_params(axis='x', rotation=45)
    else:
        axes[1].text(0.5, 0.5, 'No dated orders', ha='center', va='center')
        axes[1].set_title('Revenue Over Time')

    fig.tight_layout()
    chart_path = os.path.join(BASE_DIR, "sales_charts.png")
    fig.savefig(chart_path, dpi=100)
    plt.close(fig)
    print(f"\n[+] Chart saved to {chart_path}")
    try:
        import sys
        import subprocess
        if sys.platform.startswith("win"):
            os.startfile(chart_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", chart_path])
        else:
            subprocess.Popen(["xdg-open", chart_path])
        print("[+] Opening chart in your image viewer...")
    except Exception as e:
        print(f"[!] Could not open viewer: {e}")
    input("Press Enter to return.")


def admin_dashboard(admin_user):
    """Menu displayed only to authenticated Admin users."""
    while True:
        clear_screen()
        draw_header(f"Admin Dashboard: {admin_user['name']}")
        print("1. Add Menu Item")
        print("2. Edit Menu Item")
        print("3. Delete Menu Item")
        print("4. View Full Menu")
        print("5. Add User")
        print("6. View All Users")
        print("7. Remove User")
        print("8. Change User Role")
        print("9. View All Orders")
        print("10. View Sales Charts")
        print("11. Logout")
        print("-" * 50)

        choice = input("Select an option (1-11): ").strip()

        if choice == "1":
            add_menu_item()
        elif choice == "2":
            edit_menu_item()
        elif choice == "3":
            delete_menu_item()
        elif choice == "4":
            clear_screen()
            draw_header("Cafe Menu Items")
            display_menu_public()
            input("Press Enter to return.")
        elif choice == "5":
            add_user()
        elif choice == "6":
            view_users()
        elif choice == "7":
            remove_user()
        elif choice == "8":
            change_user_role()
        elif choice == "9":
            view_all_orders()
        elif choice == "10":
            view_sales_charts()
        elif choice == "11":
            print("\nLogging out...")
            break
        else:
            print("\n[!] Invalid input. Press Enter to retry.")
            input()


# --- MAIN ENTRY POINT ---

def main():
    """Main loop for the Cafe Management System."""
    while True:
        clear_screen()
        draw_header("Welcome to the Cafe Management System")
        print("1. View Current Menu")
        print("2. User Login (Employee / Admin)")
        print("3. Exit System")
        print("-" * 50)
        
        choice = input("Select an option (1-3): ").strip()
        
        if choice == "1":
            clear_screen()
            draw_header("Cafe Menu Items")
            display_menu_public()
            input("Press Enter to return to main menu.")
            
        elif choice == "2":
            clear_screen()
            user_session = login_screen()
            if user_session:
                if user_session['role'] == 'admin':
                    admin_dashboard(user_session)
                elif user_session['role'] == 'employee':
                    employee_dashboard(user_session)
                    
        elif choice == "3":
            clear_screen()
            print("\nShutting down system. Have a great day!\n")
            break
        else:
            print("\n[!] Invalid option. Press Enter to try again.")
            input()


if __name__ == "__main__":
    main()
