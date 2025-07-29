# USAA Transaction Summarizer

A Python command-line tool that analyzes USAA checking account CSV exports to provide insights into your spending habits. Generate monthly summaries, track spending by merchant, and export results to CSV for further analysis.

## Features

- 📊 **Monthly Summary Reports** - See deposits, spending, and net cash flow by month
- 💰 **Merchant Analysis** - Detailed breakdown of spending by merchant with transaction counts
- 📈 **Spending Trends** - Track average monthly spending and identify your top vendors  
- 🧹 **Smart Data Cleaning** - Automatically standardizes merchant names and handles pending transactions
- 📁 **CSV Export** - Export reports to CSV files for Excel/Google Sheets analysis
- 🎯 **Zero Dependencies** - Uses only pandas and Python standard library

## Usage

Basic usage:
```bash
python main.py path/to/usaa_transactions.csv
```

With verbose output:
```bash
python main.py path/to/usaa_transactions.csv --verbose
```

Export to CSV files:
```bash
python main.py path/to/usaa_transactions.csv --csv-prefix report_
```

This creates two files:
- `report_monthly_summary.csv` - Monthly totals
- `report_spending_details.csv` - Detailed spending by merchant

## USAA CSV Format

Your USAA export should have these columns:

```csv
Date,Description,Original Description,Category,Amount,Status
2025-01-15,"Grocery Store","KROGER #123     ATLANTA    GA",Food & Dining,-45.67,Posted
2025-01-14,"Electric Company","GEORGIA POWER   WEB PAYMENT",Utilities,-125.00,Posted
2025-01-14,"Paycheck Direct Deposit","EMPLOYER LLC    DIRECT DEP  ***********1234",Paycheck,2500.00,Posted
2025-01-13,"Coffee Shop","STARBUCKS       ATLANTA    GA",Food & Dining,-6.75,Posted
2025-01-12,"Rent Payment","APARTMENT MGMT  WEB PAYMENT",Housing,-1200.00,Posted
```

Note: 
- **Amount**: Negative for withdrawals, positive for deposits
- **Status**: "Posted" for completed transactions, "Pending" for processing
- **Date**: YYYY-MM-DD format

## Example Output

Monthly summary showing deposits, spending, and net cash flow:

```
Month               Deposits     Spending          Net  # Trans
------------------------------------------------------------
January 2025    $   X,XXX.XX $   X,XXX.XX $     XXX.XX      112
February 2025   $   X,XXX.XX $   X,XXX.XX $   X,XXX.XX      103
March 2025      $   X,XXX.XX $   X,XXX.XX $   X,XXX.XX       94
------------------------------------------------------------
AVERAGE/MONTH   $   X,XXX.XX $   X,XXX.XX $   X,XXX.XX     92.3
```

Detailed merchant breakdown for each month:

```
January 2025 - Total spent: $X,XXX.XX
--------------------------------------------------
  Rent Payment                   $ X,XXX.XX (1x)   38.5%
  Credit Card Payment            $   XXX.XX (2x)   22.3%
  Utilities                      $   XXX.XX (3x)    8.7%
  Grocery Store                  $   XXX.XX (12x)   7.2%
  ... and 15 others              $   XXX.XX         23.3%
```

Perfect for tracking spending habits, budgeting, and understanding where your money goes each month.
