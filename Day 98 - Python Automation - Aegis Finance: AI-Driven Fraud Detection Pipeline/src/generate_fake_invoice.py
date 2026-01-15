import os
from fpdf import FPDF
import random
from datetime import datetime, timedelta


class InvoiceGenerator:
    def __init__(self):
        # Mapping for the model categories
        self.categories_map = {
            "Amazon": "shopping_net",
            "Netflix": "entertainment",
            "Shell Station": "gas_transport",
            "Walmart": "grocery_pos",
            "McDonalds": "food_dining",
            "Apple Store": "shopping_pos",
            "Local Pharmacy": "health_fitness",
            "Uber": "misc_pos"
        }

    def create_fake_transactions(self, num_transactions=20):
        """Generates dummy data including a 'fraudulent' pattern."""
        transactions = []
        base_date = datetime(2025, 12, 1)

        for i in range(num_transactions):
            merchant = random.choice(list(self.categories_map.keys()))
            category = self.categories_map[merchant]


            hour = random.randint(8, 22)
            amount = round(random.uniform(15.0, 200.0), 2)


            if i == 12:
                hour = 3
                amount = 2850.45
                merchant = "Electronics Store"
                category = "shopping_net"

            trans_date = base_date + timedelta(days=random.randint(0, 15), hours=hour)

            transactions.append({
                "date": trans_date.strftime("%Y-%m-%d %H:%M"),
                "merchant": merchant,
                "category": category,
                "amount": amount
            })

        return sorted(transactions, key=lambda x: x['date'])

    def generate_pdf(self, output_path, transactions):
        pdf = FPDF()
        pdf.add_page()


        pdf.set_font("helvetica", "B", 16)
        pdf.cell(190, 10, "STARK BANK - STATEMENT", ln=True, align="C")

        pdf.set_font("helvetica", "", 10)
        pdf.cell(190, 10, f"Issued on: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align="R")
        pdf.ln(10)


        pdf.set_fill_color(220, 220, 220)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(45, 10, "Date", 1, 0, "C", True)
        pdf.cell(65, 10, "Description", 1, 0, "C", True)
        pdf.cell(45, 10, "Category", 1, 0, "C", True)
        pdf.cell(35, 10, "Amount ($)", 1, 1, "C", True)


        pdf.set_font("helvetica", "", 9)
        for t in transactions:
            pdf.cell(45, 8, t['date'], 1)
            pdf.cell(65, 8, t['merchant'], 1)
            pdf.cell(45, 8, t['category'], 1)
            pdf.cell(35, 8, f"{t['amount']:.2f}", 1, 1, "R")

        pdf.output(output_path)
        print(f" Arquivo gerado com sucesso em:\n{output_path}")



target_path = r"C:\Users\User\Desktop\dashboard-financeiro\reports\fake_statement_01.pdf"

gen = InvoiceGenerator()
data = gen.create_fake_transactions(20)
gen.generate_pdf(target_path, data)
