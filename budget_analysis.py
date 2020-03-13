#!/anaconda3/bin/python
"""
Author: Shrikant Kshirsagar
Purpose: To tally monthly budget sheet
License: GPLv3+
"""

import os
import sys
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def read_tx_file(a_tx_file, a_skiprows=3, a_skipfooter=0, a_ord=True,
        a_cols=['Category', 'Amount'], a_currency_symbols='[\$,]'):
    """ Function to read in transactions file (in CSV format)
    Parameters:
        a_tx_file (str): Name of transactions CSV file
        a_skiprows (int): No. of lines to skip at the start of the file
        a_skipfooter (int): No. of lines to skip at the bottom
        a_ord (bool): True if expenses are listed before income, False
        otherwise
        a_cols (list of strings): Column names containing relevant
        transaction information in the order (Category, Amount)
        a_currency_symbols (str): regex to replace in strings when dealing with
        amounts listed in a specific currency specification.
    Returns:
        expenses (DataFrame): Dataframe containing only expense information
        income (DataFrame): Dataframe containing only income information
    """
    # Read in transactions file
    raw_df = pd.read_csv(a_tx_file, skiprows=a_skiprows,
            skipfooter=a_skipfooter)
    # duplicate column names are appended with ".1"
    dup_cols = [c + ".1" for c in a_cols]
    if a_ord:
    # expenses are listed before income
        expenses = raw_df[a_cols]
        income = raw_df[dup_cols]
        # rename the columns
        income.columns = a_cols
    else:
        # expenses are listed after income
        income = raw_df[a_cols]
        expenses = raw_df[dup_cols]
        # rename the columns
        expenses.columns = a_cols
    # endif #
    # drop extraneous rows, if required
    expenses = expenses.dropna()
    # replace currency format into float
    expenses[a_cols[1]] = pd.to_numeric(
            expenses[a_cols[1]].replace(a_currency_symbols, '',regex=True))
    income = income.dropna()
    income[a_cols[1]] = pd.to_numeric(
            income[a_cols[1]].replace(a_currency_symbols, '',regex=True))
    return expenses, income
# enddef read_tx_file() #

def categorize_tx(a_tx, a_title, a_plotfile,
        a_cols=['Category', 'Amount']):
    """ Function to categorize transactions in income or expenses and
    produce a pie chart showing the breakdown
    Parameters:
        a_tx (DataFrame): Dataframe containing transactions
        a_title (str): Title of pie plot
        a_plotfile (str): Filename to save pie plot in
        a_cols (list of strings): Column names containing relevant
        transaction information in the order (Category, Amount)
    Returns:
        grouped_tx (DataFrame): Total of transactions per category
    """
    # group transactions and add them
    grouped_tx =  a_tx.groupby(a_cols[0]).aggregate(np.sum)
    grouped_tx['Contribution [%]'] = 100 * grouped_tx[a_cols[1]]/np.abs(np.sum(
            a_tx[a_cols[1]]))
    # create pie plot
    plt.close('all')
    plt.pie(grouped_tx[a_cols[1]],
            labels=grouped_tx.index.values, autopct='%.2f%%')
    plt.axis('equal')
    plt.title(a_title)
    plt.savefig(a_plotfile)
    return grouped_tx
# enddef tally_tx() #

def main(a_tx_file, a_period, a_report_file, a_prev_bal=0.0,
        a_summary_file="MyBudget2019.csv", a_summary_plot="TallyTrend.png"):
    """ Main function.
    Parameters:
        a_tx_file (str): Name of transactions CSV file
        a_period (str): Time period for which transactions are processed
        a_report_file (str): Filename of where to store reports for
        a_prev_bal (float): Previous balance
        a_summary_file (str): Filename where summaries of previous runs
            are stored
        a_summary_plot (str): Filename where trendline summaries are to be
            plotted
    Returns:
        None
    """
    assert isinstance(a_prev_bal, (float, int)), "Previous balance must be numeric."
    exp, inc = read_tx_file(a_tx_file)
    # compute total expenses, income
    tot_exp = np.sum(exp['Amount'])
    tot_inc = np.sum(inc['Amount'])
    # compute savings, savings-% and net worth
    savings = tot_inc - tot_exp
    sav_pct = 100.0 * savings / tot_inc
    net_worth = a_prev_bal + savings
    # compute grouped expenses and income
    grp_exp = categorize_tx(exp, "Expenses", "PiePlot_Expenses_" +
        a_period + ".png")
    grp_inc = categorize_tx(inc, "Income", "PiePlot_Income_" +
        a_period + ".png")
    with open(a_report_file,'w') as rf:
        rf.write("Budget Report for {}\n".format(a_period))
        rf.write("Starting balance = $ {:.2f}\n".format(a_prev_bal))
        rf.write("Total income = $ {:.2f}\n".format(tot_inc))
        rf.write("Total expenses = $ {:.2f}\n".format(tot_exp))
        rf.write("Net savings = $ {:.2f}\n".format(savings))
        rf.write("Net worth = $ {:.2f}\n".format(net_worth))
        rf.write("Savings as a % of income = {:.2f}%\n".format(sav_pct))
        rf.write("\nCategory-wise income [$]:\n")
        rf.write(grp_inc.to_string())
        rf.write("\n\nCategory-wise expenses [$]:\n")
        rf.write(grp_exp.to_string())
    # endwith #
    if not os.path.exists(a_summary_file):
        with  open(a_summary_file,'w') as sf:
            sf.write("Time Period,Income [$],Expenses [$],Savings [$],"+
                    "Net Worth [$],pct-savings [%]\n")
        # endwith #
    # endif #
    with open(a_summary_file,'a') as sf:
        sf.write("{},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}\n".format(a_period,
            tot_inc, tot_exp, savings, net_worth, sav_pct))
    # endwith #
    summary_df = pd.read_csv(a_summary_file)
    plt.close('all')
    fig, ax1 = plt.subplots()
    ax1.plot(summary_df.iloc[:,0],summary_df.iloc[:,1:5])
    ax1.set_ylabel('$')
    ax1.legend(['Income', 'Expenses', 'Savings', 'Net worth'], loc='upper left')
    ax2 = ax1.twinx()
    ax2.plot(summary_df.iloc[:,0], summary_df.iloc[:,5],'k--')
    ax2.set_ylabel('%')
    ax2.legend(['%-savings'], loc='upper right')
    plt.tight_layout()
    plt.savefig(a_summary_plot)
# enddef main() #

if __name__ == "__main__":
    passed_args = sys.argv[1:]
    if len(passed_args) > 3:
        # convert string to float
        passed_args[3] = float(passed_args[3])
        # endif #
    main(*passed_args)
    # endif #
# endif #
