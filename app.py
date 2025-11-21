from app import create_app
import csv, io
from flask import make_response
from app.storage import load_data, save_data

app = create_app()
app.secret_key = "super-secret-key-CHANGE-THIS"

@app.route("/download/csv")
def download_csv():
    expenses = load_data()

    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(["ID", "Date", "Category", "Amount", "Description"])

    for e in expenses:
        writer.writerow([e["id"], e["date"], e["category"], e["amount"], e["description"]])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=expenses.csv"
    output.headers["Content-type"] = "text/csv"
    return output

if __name__ == "__main__":
    app.run(debug=True)