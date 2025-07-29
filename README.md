# USAA Transaction Summarizer

A Python command-line tool that analyzes USAA checking account CSV exports to provide insights into your spending habits. Generate monthly summaries, track spending by merchant, and export results to CSV for further analysis.

## Features

- 📊 **Monthly Summary Reports** - See deposits, spending, and net cash flow by month
- 💰 **Merchant Analysis** - Detailed breakdown of spending by merchant with transaction counts
- 📈 **Spending Trends** - Track average monthly spending and identify your top vendors  
- 🧹 **Smart Data Cleaning** - Automatically standardizes merchant names and handles pending transactions
- 📁 **CSV Export** - Export reports to CSV files for Excel/Google Sheets analysis
- 🎯 **Zero Dependencies** - Uses only pandas and Python standard library

## Example Output

Monthly summary showing deposits, spending, and net cash flow:

    Month               Deposits     Spending          Net  # Trans
    ------------------------------------------------------------
    January 2025    $   X,XXX.XX $   X,XXX.XX $     XXX.XX      112
    February 2025   $   X,XXX.XX $   X,XXX.XX $   X,XXX.XX      103
    March 2025      $   X,XXX.XX $   X,XXX.XX $   X,XXX.XX       94
    ------------------------------------------------------------
    AVERAGE/MONTH   $   X,XXX.XX $   X,XXX.XX $   X,XXX.XX     92.3

Detailed merchant breakdown for each month:

    January 2025 - Total spent: $X,XXX.XX
    --------------------------------------------------
      Uber Eats                      $   XXX.XX (56x)  35.2%
      Rent Payment                   $ X,XXX.XX (1x)   24.0%
      Credit Card Payment            $   XXX.XX (2x)   15.7%
      ... and 15 others              $   XXX.XX         25.1%

Perfect for tracking spending habits, budgeting, and understanding where your money goes each month.