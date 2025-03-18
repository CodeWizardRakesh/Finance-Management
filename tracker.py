import os
import google.generativeai as genai
from dotenv import load_dotenv
import datetime

# Load API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

# File to store expense history
EXPENSE_FILE = "expense_history.txt"

# Initial loan details
LOAN_AMOUNT = 10000
INTEREST_RATE = 0.05 / 12  # Monthly rate (5% annual)
TENURE = 24
EMI = 439  # Pre-calculated EMI

def initialize_file():
    """Create expense file with headers if it doesn't exist."""
    if not os.path.exists(EXPENSE_FILE):
        with open(EXPENSE_FILE, "w") as f:
            f.write("Date,Income,Rent,Groceries,Entertainment,EMI,Prepayment,Principal,Interest\n")

def load_history():
    """Load expense history from file."""
    initialize_file()
    with open(EXPENSE_FILE, "r") as f:
        lines = f.readlines()
    if len(lines) > 1:  # Skip header
        return lines[1:]
    return []

def save_expense(income, rent, groceries, entertainment, emi, prepayment, principal, interest):
    """Save a new expense entry."""
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(EXPENSE_FILE, "a") as f:
        f.write(f"{date},{income},{rent},{groceries},{entertainment},{emi},{prepayment},{principal},{interest}\n")

def calculate_loan(principal, prepayment):
    """Update loan details after prepayment."""
    interest = principal * INTEREST_RATE
    principal_paid = EMI - interest
    new_principal = principal - principal_paid - prepayment
    return new_principal, interest

def get_gemini_response(query):
    """Query Gemini API with expense history and user input."""
    history = load_history()
    context = "Expense History:\n" + "".join(history) + "\nLoan Details: Initial $10,000, 5% interest, 24 months, EMI $439\nQuery: " + query
    response = model.generate_content(context)
    return response.text

def main():
    # Example: Add initial expense (customize as needed)
    history = load_history()
    if not history:
        save_expense(3000, 1000, 400, 300, EMI, 0, LOAN_AMOUNT, LOAN_AMOUNT * INTEREST_RATE)
    
    while True:
        print("\nExpense Tracker Menu:")
        print("1. Add Expense")
        print("2. Query System")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            income = float(input("Income: "))
            rent = float(input("Rent: "))
            groceries = float(input("Groceries: "))
            entertainment = float(input("Entertainment: "))
            prepayment = float(input("Prepayment (0 if none): "))
            last_entry = load_history()[-1].split(",") if load_history() else [0, 0, 0, 0, 0, EMI, 0, str(LOAN_AMOUNT)]
            principal = float(last_entry[7])
            new_principal, interest = calculate_loan(principal, prepayment)
            save_expense(income, rent, groceries, entertainment, EMI, prepayment, new_principal, interest)
            print("Expense saved.")

        elif choice == "2":
            query = input("Enter your query (e.g., 'Can I prepay $100 this month?'): ")
            response = get_gemini_response(query)
            print("System Response:", response)

        elif choice == "3":
            print("Exiting...")
            break

        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()