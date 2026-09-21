from pathlib import Path
from getpass import getpass

import pandas as pd
from sqlalchemy import create_engine


# Set project paths
project_root = Path(__file__).resolve().parents[1]
output_dir = project_root / "excel"
output_file = output_dir / "business_performance_report.xlsx"

# Ask for the database password
mysql_password = getpass("MySQL password: ")

# Connect to MySQL
engine = create_engine(
    f"mysql+pymysql://root:{mysql_password}@localhost/business_operations_analytics"
)

# Reporting views and Excel sheet names
reports = {
    "vw_powerbi_executive_kpis": "Executive KPIs",
    "vw_powerbi_monthly_performance": "Monthly Performance",
    "vw_powerbi_customer_segments": "Customer Segments",
    "vw_powerbi_product_performance": "Product Performance",
    "vw_powerbi_country_performance": "Country Performance",
    "vw_powerbi_cancellation_trends": "Cancellation Trends",
    "vw_powerbi_exceptions": "Exceptions"
}


def export_excel_report():
    output_dir.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for view, sheet_name in reports.items():
            df = pd.read_sql(f"SELECT * FROM {view}", engine)
            df.to_excel(writer, sheet_name=sheet_name, index=False)

            worksheet = writer.sheets[sheet_name]

            # Freeze the header row
            worksheet.freeze_panes = "A2"

            # Add filters
            worksheet.auto_filter.ref = worksheet.dimensions

            # Set readable column widths
            for column_cells in worksheet.columns:
                max_length = max(
                    len(str(cell.value)) if cell.value is not None else 0
                    for cell in column_cells
                )
                width = min(max(max_length + 2, 12), 35)
                worksheet.column_dimensions[column_cells[0].column_letter].width = width

            print(f"{sheet_name}: {len(df):,} rows")

    print("\nExcel report complete")
    print(f"Saved to: {output_file}")


def main():
    export_excel_report()


if __name__ == "__main__":
    main()