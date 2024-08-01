# Develop a billing software application using Python that includes a user-friendly graphical user interface (GUI) for managing customer transactions,generating invoices, and tracking sales. The application should handle product details, pricing, customer information, and generate printable bills or invoices.


from tkinter import *
from tkinter import messagebox
import mysql.connector as ms
from tkcalendar import DateEntry
from tkinter import ttk
from tkinter import filedialog
from random import randint
import datetime

# There are 3 tables in the database
# 1. product_table
# 2. customer_table
# 3. Invoice_table


# First we need to sign in to the database


sign = Tk()
sign.title("Sign In")
sign.geometry("500x500")
sign_label = Label(sign, text="Sign In", font=("times new roman", 20, "bold"))
sign_label.pack(fill=X)
host_label = Label(sign, text="Host", font=("times new roman", 15, "bold"))
host_label.pack()
host_var = StringVar()
host_entry = Entry(sign, textvariable=host_var)
host_entry.pack()
user_label = Label(sign, text="User", font=("times new roman", 15, "bold"))
user_label.pack()
user_var = StringVar()
user_entry = Entry(sign, textvariable=user_var)
user_entry.pack()
password_label = Label(sign, text="Password", font=("times new roman", 15, "bold"))
password_label.pack()
password_var = StringVar()
password_entry = Entry(sign, textvariable=password_var)
password_entry.pack()



def sign_in():
    global con, cur
    host = host_var.get()
    user = user_var.get()
    password = password_var.get()
    con = ms.connect(host=host, user=user, password=password, database="billing")
    cur = con.cursor()
    sign.destroy()

sign_button = Button(sign, text="Sign In", font=("times new roman", 15, "bold"), command=sign_in)
sign_button.pack()

sign.mainloop()


# Create the product_table
cur.execute(
    "create table if not exists product_table(product_id int primary key, product_name varchar(100), price float, stock int)")
# Create the customer_table
cur.execute(
    "create table if not exists customer_table(customer_id int primary key, customer_name varchar(100), phone_no varchar(10), email varchar(100))")
# Create the Invoice_table
cur.execute(
    "create table if not exists invoice_table(invoice_id varchar(50) primary key, customer_id int, product_id int, quantity int, total float, date date, foreign key(customer_id) references customer_table(customer_id), foreign key(product_id) references product_table(product_id))")



# Insertion in customer table will be done by the user when he/she adds a new customer
# Insertion in invoice table will be done when the user generates
# an invoice for a customer

# make a drop down menu for selecting the product from the product_table
def make_dropdown():
    cur.execute("select product_name from product_table")
    products = cur.fetchall()
    product_list = []
    for i in products:
        product_list.append(i[0])
    return product_list

# if the user selects a product from the drop down menu, then the price of the product will be displayed in the price entry box automatically
def show_price(event):
    product_name = product_var.get()
    cur.execute("select price from product_table where product_name = %s", (product_name,))
    price = cur.fetchone()
    price_var.set(price[0])

# if the user clicks on the add button, then the product will be added to the cart
def add_to_cart():
    product_name = product_var.get()
    quantity = quantity_var.get()
    price = price_var.get()
    total = price * quantity
    cart_tree.insert("", "end", values=(product_name, quantity, price, total))
    total_var.set(total_var.get() + total)

# Now checking if the customer is already present in the customer_table or not
def check_customer():
    #check by phone number
    phone_no = phone_var.get()
    cur.execute("select customer_id from customer_table where phone_no = %s", (phone_no,))
    customer_id = cur.fetchone()
    if customer_id:
        return customer_id[0]
    #check by email
    email = email_var.get()
    cur.execute("select customer_id from customer_table where email = %s", (email,))
    customer_id = cur.fetchone()
    if customer_id:
        return customer_id[0]
    return None

# if customer is present in the customer_table, then show the customer details in the customer details entry boxes automatically
def show_customer_details():
    customer_id = check_customer()
    if customer_id:
        cur.execute("select * from customer_table where customer_id = %s", (customer_id,))
        customer = cur.fetchone()
        name_var.set(customer[1])
        phone_var.set(customer[2])
        email_var.set(customer[3])

# if the customer is not present in the customer_table, then add the customer to the customer_table manually
def add_customer():
    customer_name = name_var.get()
    phone_no = phone_var.get()
    email = email_var.get()
    cur.execute("select max(customer_id) from customer_table")
    customer_id = cur.fetchone()[0]
    if customer_id == None:
        customer_id = 1
    else:
        customer_id += 1
    cur.execute("insert into customer_table values(%s, %s, %s, %s)", (customer_id, customer_name, phone_no, email))
    con.commit()
    return customer_id

# Now generating the invoice
def generate_invoice():
    customer_id = check_customer()
    if customer_id == None:
        customer_id = add_customer()
    for i in cart_tree.get_children():
        product_name = cart_tree.item(i)['values'][0]
        quantity = cart_tree.item(i)['values'][1]
        cur.execute("select product_id from product_table where product_name = %s", (product_name,))
        product_id = cur.fetchone()[0]
        Invoice_ID = "INV" + str(randint(1000, 9999))
        # date is not according to mysql first we need to convert it to the mysql date format
        # dont use date from billing software use datetime module to get the current date
        date = datetime.datetime.now().date() # this will give the current date ex: 2021-08-25
        cur.execute("insert into invoice_table values(%s, %s, %s, %s, %s, %s)", (Invoice_ID, customer_id, product_id, quantity, cart_tree.item(i)['values'][3], date))
        con.commit()
    messagebox.showinfo("Success", "Invoice Generated Successfully")

# Now generating the bill
def generate_bill():
    customer_id = check_customer()
    if customer_id == None:
        customer_id = add_customer()
    bill = open(filedialog.asksaveasfilename(defaultextension=".txt"), "w")
    bill.write("Customer ID : " + str(customer_id) + "\n")
    bill.write("Customer Name : " + name_var.get() + "\n")
    bill.write("Phone Number : " + phone_var.get() + "\n")
    bill.write("Email : " + email_var.get() + "\n")
    bill.write("Date : " + date_var.get() + "\n")
    bill.write("\n\n")
    bill.write("Product Name\tQuantity\tPrice\tTotal\n")
    for i in cart_tree.get_children():
        product_name = cart_tree.item(i)['values'][0]
        quantity = cart_tree.item(i)['values'][1]
        price = cart_tree.item(i)['values'][2]
        total = cart_tree.item(i)['values'][3]
        bill.write(product_name + "\t" + str(quantity) + "\t" + str(price) + "\t" + str(total) + "\n")
    bill.write("\n\n")
    bill.write("Total : " + str(total_var.get()))
    bill.close()
    messagebox.showinfo("Success", "Bill Generated Successfully")

def show_sales():
    #Show sales in new window when button is clicked
    sales = Tk()
    sales.title("Sales")
    sales.geometry("500x500")
    sales_label = Label(sales, text="Sales", font=("times new roman", 20, "bold"))
    sales_label.pack(fill=X)
    cur.execute("select * from invoice_table")
    sales_data = cur.fetchall()
    sales_tree = ttk.Treeview(sales, columns=("Invoice ID", "Customer ID", "Product ID", "Quantity", "Total", "Date"))
    sales_tree.heading("Invoice ID", text="Invoice ID")
    sales_tree.heading("Customer ID", text="Customer ID")
    sales_tree.heading("Product ID", text="Product ID")
    sales_tree.heading("Quantity", text="Quantity")
    sales_tree.heading("Total", text="Total")
    sales_tree.heading("Date", text="Date")
    sales_tree['show'] = 'headings'
    sales_tree.pack(fill=BOTH, expand=1)
    for i in sales_data:
        sales_tree.insert("", "end", values=i)
    sales.mainloop()





# Now creating the GUI
root = Tk()
root.title("Billing Software")
root.geometry("1920x1080")
root.config(bg="green")


# Creating the product details frame
product_frame = Frame(root, bd=5, relief=GROOVE)
product_frame.place(x=10, y=10, width=500, height=580)
product_label = Label(product_frame, text="Product Details", font=("times new roman", 20, "bold"))
product_label.pack(fill=X)
product_name_label = Label(product_frame, text="Product Name", font=("times new roman", 15, "bold"))
product_name_label.pack()
product_var = StringVar()
product_var.set("Select Product")
product_dropdown = ttk.Combobox(product_frame, textvariable=product_var, values=make_dropdown())
product_dropdown.bind("<<ComboboxSelected>>", show_price)
product_dropdown.pack()
price_label = Label(product_frame, text="Price", font=("times new roman", 15, "bold"))
price_label.pack()
price_var = DoubleVar()
price_var.set(0)
price_entry = Entry(product_frame, textvariable=price_var, state="readonly")
price_entry.pack()
quantity_label = Label(product_frame, text="Quantity", font=("times new roman", 15, "bold"))
quantity_label.pack()
quantity_var = IntVar()
quantity_var.set(1)
quantity_entry = Entry(product_frame, textvariable=quantity_var)
quantity_entry.pack()
add_button = Button(product_frame, text="Add", font=("times new roman", 15, "bold"), command=add_to_cart)
add_button.pack()

# Creating the cart frame
cart_frame = Frame(root, bd=5, relief=GROOVE)
cart_frame.place(x=520, y=10, width=600, height=400)
cart_label = Label(cart_frame, text="Cart", font=("times new roman", 20, "bold"))
cart_label.pack(fill=X)
cart_tree = ttk.Treeview(cart_frame, columns=("Product Name", "Quantity", "Price", "Total"))
cart_tree.heading("Product Name", text="Product Name")
cart_tree.heading("Quantity", text="Quantity")
cart_tree.heading("Price", text="Price")
cart_tree.heading("Total", text="Total")
cart_tree['show'] = 'headings'
cart_tree.pack(fill=BOTH, expand=1)
scroll = Scrollbar(cart_tree, orient="vertical", command=cart_tree.yview)
scroll.pack(side=RIGHT, fill=Y)
cart_tree.configure(yscrollcommand=scroll.set)
total_label = Label(cart_frame, text="Total", font=("times new roman", 15, "bold"))
total_label.pack()
total_var = DoubleVar()
total_var.set(0)
total_entry = Entry(cart_frame, textvariable=total_var, state="readonly")
total_entry.pack()



# Creating the customer details frame beside the cart frame
customer_frame = Frame(root, bd=5, relief=GROOVE)
customer_frame.place(x=520, y=420, width=600, height=250)
customer_label = Label(customer_frame, text="Customer Details", font=("times new roman", 20, "bold"))
customer_label.pack(fill=X)
name_label = Label(customer_frame, text="Name", font=("times new roman", 15, "bold"))
name_label.pack()
name_var = StringVar()
name_entry = Entry(customer_frame, textvariable=name_var)
name_entry.pack()
phone_label = Label(customer_frame, text="Phone Number", font=("times new roman", 15, "bold"))
phone_label.pack()
phone_var = StringVar()
phone_entry = Entry(customer_frame, textvariable=phone_var)
phone_entry.pack()
email_label = Label(customer_frame, text="Email", font=("times new roman", 15, "bold"))
email_label.pack()
email_var = StringVar()
email_entry = Entry(customer_frame, textvariable=email_var)
email_entry.pack()
show_button = Button(customer_frame, text="Show", font=("times new roman", 15, "bold"), command=show_customer_details)
show_button.pack()

# Creating the sales button
sales_button = Button(root, text="Show Sales", font=("times new roman", 15, "bold"), command=show_sales)
sales_button.place(x=1100, y=720)




# Creating the date entry box
date_label = Label(root, text="Date", font=("times new roman", 15, "bold"))
date_label.place(x=550, y=720)
date_var = StringVar()
date_entry = DateEntry(root, textvariable=date_var, width=12, background='darkblue', foreground='white', borderwidth=2)
date_entry.place(x=600, y=720)

# Creating the buttons
generate_invoice_button = Button(root, text="Generate Invoice", font=("times new roman", 15, "bold"), command=generate_invoice)
generate_invoice_button.place(x=700, y=720)
generate_bill_button = Button(root, text="Generate Bill", font=("times new roman", 15, "bold"), command=generate_bill)
generate_bill_button.place(x=900, y=720)




root.mainloop()
con.close()
