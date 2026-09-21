from getpass import getpass

import pandas as pd
from sqlalchemy import create_engine


# Ask for the database password
mysql_password = getpass("MySQL password: ")

# Connect to the project database
engine = create_engine(
    f"mysql+pymysql://root:{mysql_password}@localhost/business_operations_analytics"
)


def load_management_data():
    # Load verified results from the SQL reporting layer
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


def create_summary(executive, monthly, cancellations):
    kpi = executive.iloc[0]

    # Exclude December 2011 because the source ends on 9 December
    complete_months = monthly[
        ~(
            (monthly["year_number"] == 2011)
            & (monthly["month_number"] == 12)
        )
    ]

    latest = complete_months.iloc[-1]
    previous = complete_months.iloc[-2]

    cancellation = cancellations[
        ~(
            (cancellations["year_number"] == 2011)
            & (cancellations["month_number"] == 12)
        )
    ].iloc[-1]

    summary = f"""
MANAGEMENT PERFORMANCE SUMMARY

The reporting dataset generated £{kpi['revenue']:,.2f} in revenue across
{kpi['orders']:,.0f} orders and {kpi['customers']:,.0f} customers, with an
average order value of £{kpi['average_order_value']:,.2f}.

The latest complete reporting month generated £{latest['revenue']:,.2f} in
revenue compared with £{previous['revenue']:,.2f} in the previous month.
Monthly growth was {latest['monthly_growth_percent']:.2f}%.

The latest complete month recorded a cancellation rate of
{cancellation['cancellation_rate_percent']:.2f}%.

December 2011 is excluded from month on month commentary because the source
dataset ends on 9 December 2011.

All figures are taken from the verified SQL reporting layer.
"""

    return summary.strip()


def main():
    executive, monthly, cancellations = load_management_data()
    summary = create_summary(executive, monthly, cancellations)

    print("\n" + summary)


if __name__ == "__main__":
    main()