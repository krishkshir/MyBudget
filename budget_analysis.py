#!/anaconda3/bin/python
"""
Author: Shrikant Kshirsagar
Purpose: To tally monthly budget sheet
License: GPLv3+
"""

import os
import sys
import warnings
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

def categorize_tx(a_tx, a_cols=['Category', 'Amount']):
    """ Function to categorize transactions in income or expenses
    Parameters:
        a_tx (DataFrame): Dataframe containing transactions
        a_cols (list of strings): Column names containing relevant
            transaction information in the order (Category, Amount)
    Returns:
        grouped_tx (DataFrame): Total of transactions per category
    """
    # group transactions and add them
    grouped_tx =  a_tx.groupby(a_cols[0]).aggregate(np.sum)
    grouped_tx['Contribution [%]'] = 100 * grouped_tx[a_cols[1]]/np.abs(np.sum(
            a_tx[a_cols[1]]))
    return grouped_tx
# enddef categorize_tx() #

def write_reports(a_report_file, a_period, a_grp_inc, a_grp_exp, a_summary_file):
    """ Function to create summary reports.
    Parameters:
        a_report_file (str): Filename of where to store reports for
        a_period (str): Time period for which transactions are processed
        a_grp_inc (Dataframe): Dataframe containing grouped income information
        a_grp_exp (Dataframe): Dataframe containing grouped expense information
        a_summary_file (str): Filename where summaries of previous runs
            are stored
    Returns:
        None
    """
    # compute total income and expenses
    tot_inc = np.sum(a_grp_inc['Amount'])
    tot_exp = np.sum(a_grp_exp['Amount'])
    # compute savings, savings-% and net worth
    savings = tot_inc - tot_exp
    # NOTE: We implicitly assume total income > 0, otherwise the computation of
    # percentage savings below gives a meaningless result!
    if tot_inc < 0:
        warning_msg = "Total income for {:s} is negative (-${:.2f})!"
        warning_msg = warning_msg.format(a_period, -tot_inc)
        warnings.warn(warning_msg)
        sav_pct = -np.inf
    else:
        sav_pct = 100.0 * savings / tot_inc
    # endif #
    # compute and plot grouped expenses and income
    with open(a_report_file,'w') as rf:
        rf.write("Budget Report for {}\n".format(a_period))
        rf.write("Total income = $ {:.2f}\n".format(tot_inc))
        rf.write("Total expenses = $ {:.2f}\n".format(tot_exp))
        rf.write("Net savings = $ {:.2f}\n".format(savings))
        rf.write("Savings as a % of income = {:.2f}%\n".format(sav_pct))
        rf.write("\nCategory-wise income [$]:\n")
        rf.write(a_grp_inc.to_string())
        rf.write("\n\nCategory-wise expenses [$]:\n")
        rf.write(a_grp_exp.to_string())
    # endwith #
    if not os.path.exists(a_summary_file):
        with  open(a_summary_file,'w') as sf:
            sf.write("Time period,Income [$],Expenses [$],Savings [$],"+
                    "pct-savings [%]\n")
        # endwith #
    # endif #
    with open(a_summary_file,'a') as sf:
        sf.write("{},{:.2f},{:.2f},{:.2f},{:.2f}\n".format(a_period,
            tot_inc, tot_exp, savings, sav_pct))
    # endwith #
# enddef write_reports() #

def plot_tallied_tx(a_grouped_tx, a_title, a_plotfile, a_col='Contribution [%]'):
    """
    Function to plot tallied transactions
    Paramaters:
        a_grouped_tx(DataFrame): Total of transactions per category
        a_plotfile (str): Filename to save pie plot in
        a_title (str): Title of pie plot
        a_col (str): Column name containing contribution of each category
    Returns:
        None
    """
    plt.close('all')
    fig, ax = plt.subplots()
    ax.bar(np.arange(a_grouped_tx.shape[0]), a_grouped_tx[a_col],
            tick_label=a_grouped_tx.index.values)
    ax.set_title(a_title)
    ax.minorticks_on()
    ax.grid(b=True, which='both', axis='both')
    plt.xticks(rotation=90)
    ax.set_ylabel('%')
    plt.tight_layout()
    plt.savefig(a_plotfile)
# enddef plot_tallied_tx() #

def main(a_tx_file, a_period="Test period", a_report_file="Test_report.txt",
        a_summary_file="MyBudget_summary.csv",
        a_summary_plot="MyBudgetSummaryPlot.png"):
    """ Main function.
    Parameters:
        a_tx_file (str): Name of transactions CSV file
        a_period (str): Time period for which transactions are processed
        a_report_file (str): Filename of where to store reports for
        a_summary_file (str): Filename where summaries of previous runs
            are stored
        a_summary_plot (str): Filename where trendline summaries are to be
            plotted
    Returns:
        None
    """
    # read the transaction file
    exp, inc = read_tx_file(a_tx_file)
    # categorize expenses and income
    grp_inc = categorize_tx(inc)
    grp_exp = categorize_tx(exp)
    # compute total expenses, income, savings, %-savings, and write reports
    write_reports(a_report_file, a_period, grp_inc, grp_exp, a_summary_file)
    # plot category breakdown for this period and overall summary
    plot_tallied_tx(grp_inc, "Income", "Plot_Income_" + a_period + ".png")
    plot_tallied_tx(grp_exp, "Expenses", "Plot_Expenses_" + a_period + ".png")
# enddef main() #

if __name__ == "__main__":
    passed_args = sys.argv[1:]
    main(*passed_args)
    # endif #
# endif #
