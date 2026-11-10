
from datetime import datetime

def generate_invoice(invoice_data):
    booking_id=invoice_data[0]
    filename=f"invoices_data/BK{booking_id:04d}.txt"

    with open(filename,"w",encoding="utf-8") as file:

        file.write("========== STAYEASY HOTEL ==========\n")
        file.write(f"Invoice Number: BK{booking_id:04d}\n")
        file.write(f"Invoice Date: {datetime.now().strftime('%d-%m-%Y')}\n\n")

        file.write("----- Guest Details -----\n")
        file.write(f"Guest Name: {invoice_data[1]}\n")
        file.write(f"Mobile Number: {invoice_data[2]}\n")
        file.write(f"Email: {invoice_data[3]}\n\n")

        file.write("----- Room Details -----\n")
        file.write(f"Room Number: {invoice_data[4]}\n")
        file.write(f"Room Type: {invoice_data[5]}\n")
        file.write(f"Check-in: {invoice_data[6]}\n")
        file.write(f"Check-out: {invoice_data[7]}\n")
        file.write(f"Number of Guests: {invoice_data[8]}\n\n")

        file.write("----- Payment Details -----\n")
        file.write(f"Room Revenue: Rs.{invoice_data[9]:.2f}\n")
        file.write(f"GST Amount: Rs.{invoice_data[10]:.2f}\n")
        file.write(f"Total Amount: Rs.{invoice_data[11]:.2f}\n\n")

        file.write("Thank you for choosing StayEasy Hotel!")

    print("Invoice generated successfully:",filename)
