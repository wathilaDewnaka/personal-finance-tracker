import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, END

transactions = {}
count = len(transactions)

def load_transactions():
    global transactions
    try:
        with open("transactions.json", "r") as file:
            transactions = json.load(file)
            if not isinstance(transactions, dict):
                transactions = {}
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        pass

def save_transactions():
    with open("transactions.json", "w") as file:
        json.dump(transactions, file, indent=4)

def read_bulk_transactions_from_file():
    global transactions
    while True:
        try:
            file_name = input('Enter the file name without extension : ')
            with open(f'{file_name}.txt', 'r') as file:
                for line in file:
                    line = line.strip().split(',')
                    if len(line) == 4:
                        category = line[0].capitalize()
                        amount = int(line[1])
                        date = line[3]
                        transactions.setdefault(category, []).append({"amount": amount, "date": date})
                save_transactions()
                print('Bulk reading success!\n')
                break
        except FileNotFoundError:
            print('Invalid text file!')

def input_error_handling(message, data_type):
    while True:
        try:
            value = data_type(input(message))
            if data_type == int and value <= 0:
                raise ValueError
            return value
        except ValueError:
            print("Invalid Input!!!")

def add_transactions():
    global transactions
    category = input_error_handling("Enter the category:", str).capitalize()
    amount = input_error_handling("Enter the amount:", int)
    date = input_error_handling("Enter the date (YYYY-MM-DD):", str)
    transactions.setdefault(category, []).append({"amount": amount, "date": date})
    save_transactions()
    print("\nTransaction successfully saved!!\n")

def view_transactions():
    global transactions
    if not transactions:
        print("No transactions found.")
        return
    for category, category_transactions in transactions.items():
        print('\nTransaction category:', category)
        for idx, transaction in enumerate(category_transactions, start=1):
            print('\tTransaction number:', idx)
            print('\t\t', transaction)

def update_transactions():
    global transactions
    view_transactions()
    if not transactions:
        return
    category = input_error_handling("Enter the category:", str).capitalize()
    while category not in transactions:
        print("Please enter a category that already exists!!")
        category = input_error_handling("Enter the category:", str).capitalize()
    update_index = input_error_handling("Enter which transaction to update:", int)
    amount = input_error_handling("Enter the new amount:", int)
    date = input_error_handling("Enter the new date (YYYY-MM-DD):", str)
    transactions[category][update_index - 1] = {"amount": amount, "date": date}
    save_transactions()
    print("\nTransaction successfully updated!!\n")

def delete_transactions():
    global transactions
    view_transactions()
    if not transactions:
        return
    category = input_error_handling("Enter the category:", str).capitalize()
    while category not in transactions:
        print("Please enter a category that already exists!!")
        category = input_error_handling("Enter the category:", str).capitalize()
    update_index = input_error_handling("Enter which transaction to delete:", int)
    del transactions[category][update_index - 1]
    if len(transactions[category]) == 0:
        del transactions[category]
    save_transactions()
    print("\nTransaction successfully deleted!!\n")

def display_summary():
    global transactions
    total_income = sum(transaction["amount"] for category_transactions in transactions.values() for transaction in category_transactions)
    print(f"\nTotal Income: {total_income}\n")

class FinanceTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.create_widgets()
        self.root.geometry('1000x400')
        self.transactions = self.load_transactions("transactions.json")

    def create_widgets(self):
        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=1)
        self.treeview = ttk.Treeview(self.frame, columns=('Category','Amount','Date'), show="headings")
        self.treeview.heading("Category", text="Category")
        self.treeview.column('Category', anchor='w')
        self.treeview.heading("Amount", text="Amount")
        self.treeview.column('Amount', anchor='w')
        self.treeview.heading("Date", text="Date")
        self.treeview.column('Date', anchor='w')
        scrollbar = ttk.Scrollbar(self.treeview, orient="vertical", command=self.treeview.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.treeview.configure(yscrollcommand=scrollbar.set)
        for col in ['Category', 'Amount', 'Date']:
            self.treeview.heading(col, command=lambda c=col: self.sorting_(c))
        self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.search = ttk.Entry(self.root)
        self.search.pack(padx=5, pady=10)
        self.search_option = ttk.Button(self.root, text="SEARCH", command=self.search_transactions)
        self.search_option.pack(padx=5, pady=5)
        self.reset = ttk.Button(self.root, text="RESET", command=self.normalize)
        self.reset.pack(padx=5, pady=5)

    def sorting_(self, col):
        choice = messagebox.askquestion("Sorting Columns", "Is it in ascending order?")
        reverse = (choice == 'no')
        
        data = []
        for child in self.treeview.get_children(''):
            value = self.treeview.set(child, col)
            try:
                value = int(value)
            except ValueError:
                pass
            data.append((value, child))

        data.sort(reverse=reverse)

        for index, (value, child) in enumerate(data):
            
            self.treeview.move(child, '', index)
            self.treeview.set(child, col, value)

        self.treeview.heading(col, command=lambda _col=col: self.sorting_(_col)) 

    def load_transactions(self, filename):
        try:
            with open(filename, "r") as file:
                transactions = json.load(file)
                return transactions
        except FileNotFoundError:
            return {}

    def normalize(self):
        self.search.delete(0,END)
        self.display_transactions(self.transactions)

    def display_transactions(self, transactions):
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        for category, category_transactions in transactions.items():
            for transaction in category_transactions:
                self.treeview.insert("", "end", values=(category, transaction["amount"], transaction["date"]))

    def search_transactions(self):
        data = self.search.get().capitalize()
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        for category, values in self.transactions.items():
            for transaction in values: 
                if (data in str(category) or data in str(transaction["date"]) or data in str(transaction["amount"])):
                    self.treeview.insert('', index='end', values=(category, transaction["amount"], transaction["date"])) 

def GUI():
    root = tk.Tk()
    app = FinanceTrackerGUI(root)
    app.display_transactions(app.transactions)
    root.mainloop()

def main_menu():
    load_transactions()
    while True:
        print("\nPersonal Finance Tracker")
        print("1. Add Transaction")
        print("2. View Transactions")
        print("3. Update Transaction")
        print("4. Delete Transaction")
        print("5. Display Summary")
        print("6. Read data in bulk")
        print("7. GUI")
        print("8. Exit")
        choice = input_error_handling("Enter your choice:", int)
        if choice == 1:
            add_transactions()
        elif choice == 2:
            view_transactions()
        elif choice == 3:
            update_transactions()
        elif choice == 4:
            delete_transactions()
        elif choice == 5:
            display_summary()
        elif choice == 6:
            read_bulk_transactions_from_file()
        elif choice == 7:
            GUI()
        elif choice == 8:
            print("Exiting program.")
            break
        else:
            print("Invalid choice. please try again")

if __name__ == "__main__":
    main_menu()
