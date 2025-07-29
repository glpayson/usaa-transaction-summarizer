#!/usr/bin/env python3
"""
USAA Transaction Summarizer

Parses USAA checking account CSV files and generates monthly spending reports.
"""
import argparse
from pathlib import Path
import sys
import pandas as pd


def export_to_csv(monthly_stats, spending_report, csv_prefix):
    """Export reports to CSV files."""
    # Export monthly summary
    monthly_summary_path = f"{csv_prefix}monthly_summary.csv"

    # Convert monthly_stats to DataFrame
    summary_data = []
    for month, stats in monthly_stats.items():
        # Convert month name to date for better sorting
        month_date = pd.to_datetime(month, format='%B %Y')
        summary_data.append({
            'Month': month_date.strftime('%Y-%m'),  # YYYY-MM format
            'Deposits': stats['deposits'],
            'Spending': stats['spending'],
            'Net': stats['net'],
            'Transaction_Count': stats['transaction_count']
        })

    summary_df = pd.DataFrame(summary_data)
    # Sort by Month (which is now YYYY-MM format)
    summary_df = summary_df.sort_values('Month')

    summary_df.to_csv(monthly_summary_path, index=False)
    print(f"\nExported monthly summary to: {monthly_summary_path}")

    # Export spending details
    spending_details_path = f"{csv_prefix}spending_details.csv"

    # Convert spending_report to DataFrame
    details_data = []
    for month, merchants in spending_report.items():
        # Convert month name to date for better sorting
        month_date = pd.to_datetime(month, format='%B %Y')
        month_total = merchants['total'].sum()
        for merchant, row in merchants.iterrows():
            details_data.append({
                'Month': month_date.strftime('%Y-%m'),  # YYYY-MM format
                'Merchant': merchant,
                'Amount': row['total'],
                'Transaction_Count': row['count'],
                'Percentage_of_Month': round((row['total'] / month_total) * 100, 1)
            })

    details_df = pd.DataFrame(details_data)
    # Sort by Month and Amount
    details_df = details_df.sort_values(['Month', 'Amount'], ascending=[True, False])

    details_df.to_csv(spending_details_path, index=False)
    print(f"Exported spending details to: {spending_details_path}")


def print_spending_details(spending_report):
    """Print detailed spending by merchant for each month."""
    print("\n" + "=" * 60)
    print("DETAILED SPENDING BY MERCHANT")
    print("=" * 60)

    # Sort months chronologically
    sorted_months = sorted(spending_report.keys(),
                           key=lambda x: pd.to_datetime(x, format='%B %Y'))

    for month in sorted_months:
        merchant_data = spending_report[month]
        month_total = merchant_data['total'].sum()

        print(f"\n{month} - Total spent: ${month_total:,.2f}")
        print("-" * 50)

        # Show top 10 merchants
        num_to_show = min(10, len(merchant_data))

        for merchant, row in merchant_data.head(num_to_show).iterrows():
            percentage = (row['total'] / month_total) * 100
            print(f"  {merchant:<30} ${row['total']:>9,.2f} ({row['count']:>2}x) {percentage:>5.1f}%")

        # If there are more merchants, show summary
        if len(merchant_data) > 10:
            remaining = len(merchant_data) - 10
            remaining_total = merchant_data.iloc[10:]['total'].sum()
            remaining_percentage = (remaining_total / month_total) * 100
            print(
                f"  {'... and ' + str(remaining) + ' others':<30} ${remaining_total:>9,.2f}        {remaining_percentage:>5.1f}%")


def create_spending_report(df_posted):
    """Create detailed spending report by merchant for each month."""
    spending_report = {}

    # Group by month
    for month, month_df in df_posted.groupby('MonthName'):
        # Get only spending transactions (negative amounts)
        spending_df = month_df[month_df['Amount'] < 0].copy()

        if len(spending_df) == 0:
            continue

        # Group by merchant and sum amounts
        merchant_spending = spending_df.groupby('CleanMerchant').agg({
            'Amount': ['sum', 'count']
        }).round(2)

        # Flatten column names
        merchant_spending.columns = ['total', 'count']

        # Convert to positive amounts for display
        merchant_spending['total'] = abs(merchant_spending['total'])

        # Sort by total spending descending
        merchant_spending = merchant_spending.sort_values('total', ascending=False)

        spending_report[month] = merchant_spending

    return spending_report


def print_monthly_summary(monthly_stats, df_posted):
    """Print monthly summary table with totals and averages."""
    print("\n" + "=" * 60)
    print("MONTHLY TOTALS")
    print("=" * 60)

    # Sort months chronologically
    sorted_months = sorted(monthly_stats.keys(),
                           key=lambda x: pd.to_datetime(x, format='%B %Y'))

    print("\nMonth-by-month summary:")
    print(f"{'Month':<15} {'Deposits':>12} {'Spending':>12} {'Net':>12} {'# Trans':>8}")
    print("-" * 60)

    total_deposits = 0
    total_spending = 0

    for month in sorted_months:
        stats = monthly_stats[month]
        total_deposits += stats['deposits']
        total_spending += stats['spending']

        print(f"{month:<15} ${stats['deposits']:>11,.2f} ${stats['spending']:>11,.2f} "
              f"${stats['net']:>11,.2f} {stats['transaction_count']:>8}")

    print("-" * 60)
    print(f"{'TOTAL':<15} ${total_deposits:>11,.2f} ${total_spending:>11,.2f} "
          f"${total_deposits - total_spending:>11,.2f} {len(df_posted):>8}")

    # Calculate and display averages
    num_months = len(monthly_stats)
    avg_deposits = total_deposits / num_months
    avg_spending = total_spending / num_months
    avg_net = (total_deposits - total_spending) / num_months
    avg_transactions = len(df_posted) / num_months

    print("-" * 60)
    print(f"{'AVERAGE/MONTH':<15} ${avg_deposits:>11,.2f} ${avg_spending:>11,.2f} "
          f"${avg_net:>11,.2f} {avg_transactions:>8.1f}")


def calculate_monthly_totals(df_posted):
    """Calculate monthly deposits and spending totals."""
    monthly_stats = {}

    # Group by month
    for month, month_df in df_posted.groupby('MonthName'):
        deposits = month_df[month_df['Amount'] > 0]['Amount'].sum()
        spending = abs(month_df[month_df['Amount'] < 0]['Amount'].sum())
        net = deposits - spending

        monthly_stats[month] = {
            'deposits': deposits,
            'spending': spending,
            'net': net,
            'transaction_count': len(month_df)
        }

    return monthly_stats


def clean_merchant_name(desc):
    """Extract clean merchant name from description."""
    # Remove trailing transaction IDs (e.g., ***********F3A3)
    desc = desc.strip()

    # Common patterns to clean
    if 'UBER EATS' in desc:
        return 'Uber Eats'
    elif 'PAYPAL' in desc:
        # Try to extract what was purchased via PayPal
        if 'INST XFER' in desc:
            return 'PayPal Transfer'
        else:
            return 'PayPal'
    elif 'CAREERBUILDER' in desc:
        return 'CareerBuilder Paycheck'
    elif 'INTEREST PAID' in desc:
        return 'Interest Income'
    elif 'Georgia Departme' in desc:
        return 'Georgia State Tax Refund'
    elif 'IRS  TREAS' in desc and 'TAX REF' in desc:
        return 'Federal Tax Refund'
    else:
        # For other transactions, take the first meaningful part
        cleaned = desc.split('***')[0].strip()
        if len(cleaned) > 50:
            cleaned = cleaned[:50].strip()
        return cleaned


def clean_data(df, verbose=False):
    """Clean and categorize transaction data."""
    print("\n" + "=" * 60)
    print("DATA CLEANING & CATEGORIZATION")
    print("=" * 60)

    df['Date'] = pd.to_datetime(df['Date'])

    # Add month column for grouping
    df['Month'] = df['Date'].dt.to_period('M')
    df['Year'] = df['Date'].dt.year
    df['MonthName'] = df['Date'].dt.strftime('%B %Y')

    # Clean merchant names
    df['CleanMerchant'] = df['Description'].apply(clean_merchant_name)

    # Categorize deposits vs withdrawals
    df['TransactionType'] = df['Amount'].apply(lambda x: 'Deposit' if x > 0 else 'Withdrawal')

    # Filter out pending transactions for financial calculations
    df_posted = df[df['Status'] == 'Posted'].copy()

    print(f"\nCleaning results:")
    print(f"  Unique months: {df['Month'].nunique()}")
    print(f"  Posted transactions: {len(df_posted)} (excluding {len(df) - len(df_posted)} pending)")
    print(f"  Unique clean merchants: {df['CleanMerchant'].nunique()} (was {df['Description'].nunique()})")

    if verbose:
        print("\nTop 10 merchants by transaction count:")
        for merchant, count in df_posted['CleanMerchant'].value_counts().head(10).items():
            print(f"  {merchant}: {count} transactions")

    return df_posted


def explore_data(df, verbose=False):
    """Print data exploration statistics."""
    print("\n" + "=" * 60)
    print("DATA EXPLORATION")
    print("=" * 60)

    # Basic info
    print(f"\nDataFrame shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"\nColumn names: {', '.join(df.columns.tolist())}")

    # Data types
    print("\nColumn data types:")
    for col, dtype in df.dtypes.items():
        print(f"  {col}: {dtype}")

    # Check for missing values
    print("\nMissing values per column:")
    missing = df.isnull().sum()
    for col, count in missing.items():
        if count > 0:
            print(f"  {col}: {count}")
    if missing.sum() == 0:
        print("  No missing values found!")

    # Date range
    df['Date'] = pd.to_datetime(df['Date'])
    print(f"\nDate range: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")
    print(f"Span: {(df['Date'].max() - df['Date'].min()).days} days")

    # Transaction status breakdown
    print("\nTransaction status:")
    for status, count in df['Status'].value_counts().items():
        print(f"  {status}: {count}")

    # Amount statistics
    print("\nAmount statistics:")
    print(f"  Total transactions: {len(df)}")
    print(f"  Deposits: {(df['Amount'] > 0).sum()} transactions")
    print(f"  Withdrawals: {(df['Amount'] < 0).sum()} transactions")
    print(f"  Zero amount: {(df['Amount'] == 0).sum()} transactions")

    # Categories
    print(f"\nUnique categories: {df['Category'].nunique()}")
    print("\nTop 10 categories by frequency:")
    for cat, count in df['Category'].value_counts().head(10).items():
        print(f"  {cat}: {count} transactions")

    # Sample data
    if verbose:
        print("\nFirst 5 transactions:")
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', 40)
        print(df.head().to_string(index=False))

    return df


def read_csv(args, csv_path):
    print("\nReading CSV file...")
    try:
        df = pd.read_csv(csv_path)
        print(f"Successfully loaded {len(df)} transactions")
        if args.verbose:
            print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)
    return df


def main():
    parser = argparse.ArgumentParser(
        description="Analyze USAA checking account transactions and generate monthly reports"
    )
    parser.add_argument(
        "csv_file",
        type=str,
        help="Path to the USAA transactions CSV file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--csv-prefix",
        type=str,
        help="Prefix for CSV output files (e.g., 'report_' creates report_monthly_summary.csv and report_spending_details.csv)"
    )

    args = parser.parse_args()

    csv_path = Path(args.csv_file)
    if not csv_path.exists():
        print(f"Error: File '{csv_path}' does not exist")
        sys.exit(1)

    if not csv_path.suffix.lower() == '.csv':
        print(f"Warning: File '{csv_path}' does not have .csv extension")

    print(f"Processing transactions from: {csv_path}")
    if args.verbose:
        print(f"File size: {csv_path.stat().st_size:,} bytes")

    df = read_csv(args, csv_path)
    df = explore_data(df, args.verbose)
    df_posted = clean_data(df, args.verbose)
    monthly_stats = calculate_monthly_totals(df_posted)
    print_monthly_summary(monthly_stats, df_posted)
    spending_report = create_spending_report(df_posted)
    print_spending_details(spending_report)

    if args.csv_prefix:
        export_to_csv(monthly_stats, spending_report, args.csv_prefix)

    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()