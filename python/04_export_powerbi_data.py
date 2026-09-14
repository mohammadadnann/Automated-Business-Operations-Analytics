from pathlib import Path
from getpass import getpass

import pandas as pd
from sqlalchemy import create_engine


# Set the project and output paths
project_root = Path(__file__).resolve().parents[1]
output_dir = project_root / "data" / "powerbi"


# Ask for the database password when the script runs
mysql_password = getpass("MySQL password: ")


# Connect to the project database
engine = create_engine(
    f"mysql+pymysql://root:{mysql_password}@localhost/business_operations_analytics"
)


# Power BI reporting views
views = [
    "vw_powerbi_executive_kpis",
    "vw_powerbi_monthly_performance",
    "vw_powerbi_customer_segments",
    "vw_powerbi_product_performance",
    "vw_powerbi_country_performance",
    "vw_powerbi_cancellation_trends",
    "vw_powerbi_exceptions"
]


def export_views():
    # Create the output folder if it does not exist
    output_dir.mkdir(parents=True, exist_ok=True)

    for view in views:
        # Read each reporting view
        df = pd.read_sql(f"SELECT * FROM {view}", engine)

        # Create a simple Power BI file name
        file_name = view.replace("vw_powerbi_", "") + ".csv"
        output_path = output_dir / file_name

        # Save the reporting data
        df.to_csv(output_path, index=False)

        print(f"{file_name}: {len(df):,} rows")


def main():
    export_views()

    print("\nPower BI exports complete")
    print(f"Saved to: {output_dir}")


if __name__ == "__main__":
    main()