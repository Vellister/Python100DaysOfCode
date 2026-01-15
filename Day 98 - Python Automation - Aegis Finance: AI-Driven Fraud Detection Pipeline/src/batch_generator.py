import os
from fpdf import FPDF
import random
from datetime import datetime, timedelta


class BatchInvoiceGenerator:
    def __init__(self):
        self.categories_map = {
            "Amazon": "shopping_net",
            "Netflix": "entertainment",
            "Shell Station": "gas_transport",
            "Walmart": "grocery_pos",
            "McDonalds": "food_dining",
            "Apple Store": "shopping_pos",
            "Pharmacy": "health_fitness",
            "Uber": "misc_pos"
        }

    def generate_random_invoice(self, filename, invoice_id):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(190, 10, f"STARK BANK - STATEMENT #{invoice_id}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(10)

        pdf.set_fill_color(220, 220, 220)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(45, 10, "Date", 1, 0, "C", True)
        pdf.cell(65, 10, "Description", 1, 0, "C", True)
        pdf.cell(45, 10, "Category", 1, 0, "C", True)
        pdf.cell(35, 10, "Amount ($)", 1, 1, "C", True)

        pdf.set_font("helvetica", "", 9)

        # generating 15 transactions per invoice
        base_date = datetime(2025, 12, 1) + timedelta(days=random.randint(0, 30))

        for i in range(15):
            merchant = random.choice(list(self.categories_map.keys()))
            category = self.categories_map[merchant]

            # normal transactions
            hour = random.randint(8, 22)
            amount = round(random.uniform(10, 200), 2)


            if i == 5 and random.random() > 0.5:
                hour = random.randint(1, 4)
                amount = round(random.uniform(1000, 3000), 2)
                merchant = "Unusual Online Store"
                category = "shopping_net"

            trans_date = base_date + timedelta(hours=hour, minutes=random.randint(0, 59))

            pdf.cell(45, 8, trans_date.strftime("%Y-%m-%d %H:%M"), 1)
            pdf.cell(65, 8, merchant, 1)
            pdf.cell(45, 8, category, 1)
            pdf.cell(35, 8, f"{amount:.2f}", 1, 1, "R")

        pdf.output(filename)


# execution
output_dir = r"C:\Users\User\Desktop\dashboard-financeiro\reports"
gen = BatchInvoiceGenerator()

for i in range(1, 11):
    path = os.path.join(output_dir, f"invoice_batch_{i}.pdf")
    gen.generate_random_invoice(path, i)
    print(f"generated: {path}")
