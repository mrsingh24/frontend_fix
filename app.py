from flask import Flask, render_template, request
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

# 🔹 HOME PAGE (FORM)
@app.route("/")
def home():
    conn = get_db_connection()
    cur = conn.cursor()

    # ✅ unique services
    cur.execute("""
        SELECT DISTINCT service_name
        FROM customer_service.customerservicerequest
        WHERE service_name IS NOT NULL
        ORDER BY service_name
    """)
    services = [row[0] for row in cur.fetchall()]

    # ✅ unique areas (locality + city)
    cur.execute("""
        SELECT DISTINCT
        TRIM(
            SPLIT_PART(address, ',', array_length(string_to_array(address, ','), 1) - 2)
            || ', ' ||
            SPLIT_PART(address, ',', array_length(string_to_array(address, ','), 1) - 1)
        ) AS area
        FROM customer_service.customerservicerequest
        WHERE address IS NOT NULL
        ORDER BY area
    """)
    areas = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return render_template(
        "form.html",
        services=services,
        areas=areas
    )

# 🔹 SEARCH RESULT
@app.route("/search", methods=["POST"])
def search():
    service = request.form.get("service")
    area = request.form.get("area")

    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        SELECT
            id,
            customer_id,
            first_name,
            last_name,
            mobile_no,
            email,
            service_name
        FROM customer_service.customerservicerequest
        WHERE service_name = %s
        AND TRIM(
            SPLIT_PART(address, ',', array_length(string_to_array(address, ','), 1) - 2)
            || ', ' ||
            SPLIT_PART(address, ',', array_length(string_to_array(address, ','), 1) - 1)
        ) = %s
    """

    cur.execute(query, (service, area))
    results = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "index.html",
        data=results,
        service=service,
        area=area
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

