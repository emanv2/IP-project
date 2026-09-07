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
    # Get current date and time in a readable format
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Check if orders.csv already exists
    if os.path.exists(ORDERS_FILE):
        # Load existing orders from the CSV file
        orders_df = pd.read_csv(ORDERS_FILE)
    else:
        # Create a new empty DataFrame with the required columns
        orders_df = pd.DataFrame(columns=['order_id', 'timestamp', 'item_name', 'quantity', 'price'])
    
    # Loop through each item in the shopping cart
    for item_id, qty in order_cart.items():
        # Filter the menu to find the row where id matches item_id, then get the first (and only) result
        item_row = menu_df[menu_df['id'] == item_id].iloc[0]
        # Calculate the total price for this item (price per item × quantity)
        item_price = float(item_row['price']) * qty
        # Add a new row to the orders DataFrame using .loc[len(orders_df)]
        # This appends to the end because len() gives us the next index position
        orders_df.loc[len(orders_df)] = [order_id, timestamp, item_row['name'], qty, round(item_price, 2)]
    
    # Write the complete DataFrame back to the CSV file
    orders_df.to_csv(ORDERS_FILE, index=False)


def get_next_order_id():
    """Calculates the next order number based on unique order IDs already logged."""
    # Check if the orders file exists yet
    if not os.path.exists(ORDERS_FILE):
        return "ORD1"  # First order ever
    
    try:
        # Read the orders CSV file into a DataFrame
        orders_df = pd.read_csv(ORDERS_FILE)
        # Check if there are no orders yet
        if orders_df.empty:
            return "ORD1"
        # Count how many unique order IDs exist, then add 1 for the next order
        unique_order_count = orders_df['order_id'].nunique()
        return f"ORD{unique_order_count + 1}"
    except Exception:
        # If anything goes wrong, start from ORD1
        return "ORD1"


# --- TERMINAL UI FORMATTING HELPERS ---

def clear_screen():
    """Clears the terminal screen for a clean, app-like user interface."""
    os.system('cls' if os.name == 'nt' else 'clear')


def draw_header(title):
    """Draws a beautiful decorative frame for section titles."""
    border = "=" * 50
    print(border)
    print(f" {title.upper().center(48)} ")
    print(border)


def display_menu_public():
    """Displays the menu in a clean, categorized table using Pandas grouping."""
    # Check if menu.csv file exists
    if not os.path.exists(MENU_FILE):
        print("\n[!] The cafe menu is currently empty.")
        return
    
    # Read the menu CSV file into a DataFrame
    menu_df = pd.read_csv(MENU_FILE)
    # Check if the DataFrame has any rows
    if menu_df.empty:
        print("\n[!] The cafe menu is currently empty.")
        return
    
    # Print table header
    print("\n" + "-" * 50)
    print(f"{'ID':<4} | {'Name':<25} | {'Price':<10}")
    print("-" * 50)
    
    # Get all unique category names from the 'category' column
    categories = menu_df['category'].unique()
    
    # Loop through each category
    for category in categories:
        print(f"\n--- {str(category).upper()} ---")
        # Filter the DataFrame to only include rows where category matches
        category_rows = menu_df[menu_df['category'] == category]
        
        # Loop through each row in the filtered category
        for _, item in category_rows.iterrows():
            # Print the item ID, name, and price in a formatted table row
            print(f"[{int(item['id']):<2}] | {item['name']:<25} | ${float(item['price']):>6.2f}")
            
    print("-" * 50 + "\n")


# --- AUTHENTICATION MODULE ---

def login_screen():
    """Asks for credentials, checking users.csv for match using standard Python iteration."""
    draw_header("Account Login")
    # Get username from user input and remove any extra spaces
    username = input("Username: ").strip()
    # Get password from user input and remove any extra spaces
    password = input("Password: ").strip()
    
    # Check if users.csv file exists
    if not os.path.exists(USERS_FILE):
        print("\n[!] Database file not found.")
        input()
        return None
    
    # Read the users CSV file into a pandas DataFrame
    users_df = pd.read_csv(USERS_FILE)
    
    # Convert the DataFrame to a list of dictionaries (one dict per user)
    users_list = users_df.to_dict('records')
    
    # Loop through each user record
    for user in users_list:
        # Check if both username and password match
        if user['username'] == username and user['password'] == password:
            return user  # Login successful, return the user's information
    
    # If we reach here, credentials didn't match any user
    print("\n[!] Invalid username or password. Press Enter to try again.")
    input()
    return None


# --- EMPLOYEE DASHBOARD & ORDER LOGGING ---

def log_customer_order(employee_user):
    """Workflow to select items, calculate sub-total and total, write receipt, and log to file."""
    # Check if menu file exists
    if not os.path.exists(MENU_FILE):
        print("\n[!] Cafe menu database not found.")
        input("\nPress Enter to return.")
        return
    
    # Read menu.csv into a DataFrame
    menu_df = pd.read_csv(MENU_FILE)
    # Check if menu has any items
    if menu_df.empty:
        print("\n[!] Cannot place order. The cafe menu is empty.")
        input("\nPress Enter to return.")
        return
    
    # Dictionary to store selected items: {item_id: quantity}
    order_cart = {}
    
    # Keep looping until order is completed or cancelled
    while True:
        clear_screen()
        draw_header("Create Customer Order")
        display_menu_public()
        
        # Show items currently in the cart
        if order_cart:
            print("--- CURRENT CART ---")
            temp_total = 0.0
            # Loop through each item in the cart
            for item_id, qty in order_cart.items():
                # Find the menu item with matching ID
                match = menu_df[menu_df['id'] == item_id]
                if not match.empty:
                    # Get the first (and only) matching row
                    item_row = match.iloc[0]
                    # Calculate subtotal for this item
                    subtotal = float(item_row['price']) * qty
                    temp_total += subtotal
                    print(f" * {item_row['name']} x{qty} = ${subtotal:.2f}")
            print(f"Current Total: ${temp_total:.2f}")
            print("-" * 50)
        
        print("\nCommands: Enter 'done' to complete order, or 'cancel' to exit.")
        choice = input("Enter Item ID to add: ").strip().lower()
        
        # Check if user wants to cancel
        if choice == 'cancel':
            print("\n[-] Order discarded.")
            input("Press Enter to return.")
            return
        
        # Check if user wants to finish the order
        if choice == 'done':
            if not order_cart:
                print("\n[!] Cart is empty. Cannot complete order.")
                input("Press Enter to continue.")
                continue
            break  # Exit the loop and proceed to generate receipt
        
        # Try to convert the input to an integer (item ID)
        try:
            item_id = int(choice)
        except ValueError:
            print("\n[!] Please enter a valid numerical ID, 'done', or 'cancel'.")
            input("Press Enter to try again.")
            continue
        
        # Check if the item ID exists in the menu
        match = menu_df[menu_df['id'] == item_id]
        if match.empty:
            print("\n[!] Item ID not found in menu.")
            input("Press Enter to try again.")
            continue
        
        # Get the selected item from the menu
        selected_item = match.iloc[0]
        
        # Ask for quantity
        qty_input = input(f"Enter quantity for {selected_item['name']}: ").strip()
        try:
            qty = int(qty_input)
            # Make sure quantity is positive
            if qty <= 0:
                print("\n[!] Quantity must be greater than zero.")
                input("Press Enter to try again.")
                continue
        except ValueError:
            print("\n[!] Quantity must be a valid number.")
            input("Press Enter to try again.")
            continue
        
        # Add the item to the cart (or update quantity if already in cart)
        order_cart[item_id] = order_cart.get(item_id, 0) + qty
        print(f"\n[+] Added {qty}x {selected_item['name']} to cart.")
    
    # Generate a unique order ID
    order_id = get_next_order_id()
    total_price = 0.0
    
    # Display the receipt
    clear_screen()
    draw_header("Order Receipt")
    print(f"Order ID: {order_id}")
    print(f"Server: {employee_user['name']}")
    print(f"Date/Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    print(f"{'Item Name':<25} | {'Qty':<5} | {'Price':<8} | {'Total':<8}")
    print("-" * 50)
    
    # Loop through cart and print each line item
    for item_id, qty in order_cart.items():
        # Find the item in the menu DataFrame
        item_row = menu_df[menu_df['id'] == item_id].iloc[0]
        price = float(item_row['price'])
        subtotal = price * qty
        total_price += subtotal
        print(f"{item_row['name']:<25} | {qty:<5} | ${price:>6.2f} | ${subtotal:>6.2f}")
            
    print("-" * 50)
    print(f"{'GRAND TOTAL:':<40} ${total_price:>7.2f}")
    print("-" * 50)
    
    # Save order to orders.csv — one row per item in the cart
    save_order(order_id, order_cart, menu_df)
    
    print("\n[+] Order successfully logged and saved to database.")
    input("\nPress Enter to return to Employee Menu.")


def employee_dashboard(employee_user):
    """Menu displayed only to authenticated Employee users."""
    # Keep showing employee menu until user chooses to logout
    while True:
        # Clear old text to make UI look clean
        clear_screen()
        # Show title banner with employee's name pulled from user profile dictionary
        draw_header(f"Employee Dashboard: {employee_user['name']}")
        # Display menu options available to employees
        print("1. Log New Customer Order")
        print("2. Logout")
        print("-" * 50)
        
        # Ask employee to choose an option, .strip() removes extra spaces
        choice = input("Select an option (1-2): ").strip()
        
        # If they choose 1, call the function to start taking a customer order
        if choice == "1":
            log_customer_order(employee_user)
        # If they choose 2, exit the loop which returns to main menu
        elif choice == "2":
            print("\nLogging out...")
            break  # Exit the while loop
        # If input doesn't match 1 or 2, show error and wait for Enter
        else:
            print("\n[!] Invalid input. Press Enter to retry.")
            input()  # Pause so user can read error message


# --- MAIN ENTRY POINT ---

def main():
    """Main loop for the Cafe Management System."""
    # Infinite loop keeps program running until user chooses exit
    while True:
        # Clear terminal screen for fresh, clean appearance
        clear_screen()
        # Display welcome header using the banner function
        draw_header("Welcome to the Cafe Management System")
        # Print the main menu options that users can choose from
        print("1. View Current Menu")
        print("2. User Login (Employee / Admin)")
        print("3. Exit System")
        print("-" * 50)
        
        # Get user's choice and remove any extra whitespace with .strip()
        choice = input("Select an option (1-3): ").strip()
        
        # OPTION 1: Display the menu to the user
        if choice == "1":
            clear_screen()  # Clean screen before showing menu
            draw_header("Cafe Menu Items")  # Title banner
            display_menu_public()  # Function that prints menu from CSV
            input("Press Enter to return to main menu.")  # Pause until user presses Enter
            
        # OPTION 2: Login process for employees and admins
        elif choice == "2":
            clear_screen()  # Clean screen for login page
            user_session = login_screen()  # Call login function, returns user dict or None
            # If login was successful (returned a user object instead of None)
            if user_session:
                # Check the 'role' field from the users.csv to determine access level
                if user_session['role'] == 'admin':
                    # Admin functionality is not built yet
                    print("\n[!] Admin dashboard coming soon...")
                    input("\nPress Enter to return to main menu.")
                # If user is an employee, show them the employee menu
                elif user_session['role'] == 'employee':
                    employee_dashboard(user_session)  # Takes user to employee menu
                    
        # OPTION 3: Exit the program completely
        elif choice == "3":
            clear_screen()
            print("\nShutting down system. Have a great day!\n")
            break  # Exit the while True loop, ending the program
        # Handle invalid input (anything other than 1, 2, or 3)
        else:
            print("\n[!] Invalid option. Press Enter to try again.")
            input()  # Wait for Enter key so user can read the error


if __name__ == "__main__":
    main()
