import os
from getpass import getpass

import pandas as pd
from openai import OpenAI
from sqlalchemy import create_engine


# Check the API key
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY is not set")

client = OpenAI()

# Connect to the project database
mysql_password = getpass("MySQL password: ")

engine = create_engine(
    f"mysql+pymysql://root:{mysql_password}@localhost/business_operations_analytics"
)


def load_management_data():
    executive = pd.read_sql(
        "SELECT * FROM vw_powerbi_executive_kpis",
        engine
    )

    monthly = pd.read_sql(
        """
        SELECT *
        FROM vw_powerbi_monthly_performance
        ORDER BY year_number, month_number
        """,
        engine
    )

    cancellations = pd.read_sql(
        """
        SELECT *
        FROM vw_powerbi_cancellation_trends
        ORDER BY year_number, month_number
        """,
        engine
    )

    return executive, monthly, cancellations


def prepare_kpis(executive, monthly, cancellations):
    kpi = executive.iloc[0]

    # December 2011 is incomplete in the source data
    complete_months = monthly[
        ~(
            (monthly["year_number"] == 2011)
            & (monthly["month_number"] == 12)
        )
    ]

    complete_cancellations = cancellations[
        ~(
            (cancellations["year_number"] == 2011)
            & (cancellations["month_number"] == 12)
        )
    ]

    latest = complete_months.iloc[-1]
    previous = complete_months.iloc[-2]
    cancellation = complete_cancellations.iloc[-1]

    return {
        "total_revenue": round(float(kpi["revenue"]), 2),
        "total_orders": int(kpi["orders"]),
        "total_customers": int(kpi["customers"]),
        "average_order_value": round(float(kpi["average_order_value"]), 2),
        "latest_month": f"{int(latest['year_number'])}-{int(latest['month_number']):02d}",
        "latest_revenue": round(float(latest["revenue"]), 2),
        "previous_revenue": round(float(previous["revenue"]), 2),
        "monthly_growth_percent": round(
            float(latest["monthly_growth_percent"]), 2
        ),
        "cancellation_rate_percent": round(
            float(cancellation["cancellation_rate_percent"]), 2
        )
    }


def generate_commentary(kpis):
    prompt = f"""
You are writing a short management commentary for a business performance report.

Use only the verified KPI values below. Do not calculate or invent any figures.

{kpis}

Write 3 concise bullet points covering:
1. Overall business performance
2. Latest monthly performance
3. The main operational concern

Use clear professional language for a non technical manager.
Mention that December 2011 is excluded because the source data ends on 9 December.
"""

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    return response.output_text


def main():
    executive, monthly, cancellations = load_management_data()

    kpis = prepare_kpis(
        executive,
        monthly,
        cancellations
    )

    print("\nVERIFIED SQL KPIS")
    for name, value in kpis.items():
        print(f"{name}: {value}")

    try:
        commentary = generate_commentary(kpis)

        print("\nAI MANAGEMENT COMMENTARY\n")
        print(commentary)

    except Exception as error:
        print("\nAI commentary could not be generated.")
        print(f"API error: {error}")


if __name__ == "__main__":
    main()