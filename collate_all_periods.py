#!/anaconda3/bin/python
"""
Author: Shrikant Kshirsagar
Purpose: To tally monthly budget sheet
License: GPLv3+
"""

import os
import sys
import warnings
import argparse
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def read_tx_file(a_tx_file, a_skiprows=3, a_skipfooter=0,
        a_cols=['Category', 'Amount'], a_currency_symbols='[\$,]'):
    """ Function to read in transactions file (in CSV format)
    Parameters:
        a_tx_file (str): Name of transactions CSV file
        a_skiprows (int): No. of lines to skip at the start of the file
        a_skipfooter (int): No. of lines to skip at the bottom
        a_cols (list of strings): Column names containing relevant
            transaction information in the order (Category, Amount)
        a_currency_symbols (str): regex to replace in strings when dealing with
            amounts listed in a specific currency specification.
    Returns:
        income (DataFrame): Dataframe containing only income information
        expenses (DataFrame): Dataframe containing only expense information
        savings (DataFrame): Dataframe containing only savings information
    """
    # Read in transactions file
    raw_df = pd.read_csv(a_tx_file, skiprows=a_skiprows,
            skipfooter=a_skipfooter)
    # read expenses
    expenses = raw_df[a_cols]
    # drop extraneous rows, if required
    expenses = expenses.dropna()
    # read income
    # duplicate column names are appended with ".1"
    dup_cols = [c + ".1" for c in a_cols]
    income = raw_df[dup_cols]
    # rename the columns
    income.columns = a_cols
    # drop extraneous rows, if required
    income = income.dropna()
    # read savings
    # duplicate column names are appended with ".2"
    dup_cols = [c + ".2" for c in a_cols]
    savings = raw_df[dup_cols].copy()
    # rename the columns
    savings.columns = a_cols
    # drop extraneous rows, if required
    savings = savings.dropna()
    # replace currency format into float
    expenses[a_cols[1]] = pd.to_numeric(
            expenses[a_cols[1]].replace(a_currency_symbols, '',regex=True))
    income = income.dropna()
    income[a_cols[1]] = pd.to_numeric(
            income[a_cols[1]].replace(a_currency_symbols, '',regex=True))
    savings[a_cols[1]] = pd.to_numeric(
            savings[a_cols[1]].replace(a_currency_symbols, '',regex=True))
    # rename columns to include unit
    expenses = expenses.rename(columns={a_cols[1]: a_cols[1]+" [$]"})
    income = income.rename(columns={a_cols[1]: a_cols[1]+" [$]"})
    savings = savings.rename(columns={a_cols[1]: a_cols[1]+" [$]"})
    return income, expenses, savings
# enddef read_tx_file() #

def categorize_tx(a_tx, a_cols=['Category', 'Amount [$]']):
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

def write_reports(a_report_file, a_period, a_grp_inc, a_grp_exp, a_grp_sav,
        a_summary_file, a_amt_colname='Amount [$]'):
    """ Function to create summary reports.
    Parameters:
        a_report_file (str): Filename of where to store reports for
        a_period (str): Time period for which transactions are processed
        a_grp_inc (Dataframe): Dataframe containing grouped income information
        a_grp_exp (Dataframe): Dataframe containing grouped expense information
        a_grp_sav (Dataframe): Dataframe containing grouped savings information
        a_summary_file (str): Filename where summaries of previous runs
            are stored
        a_amt_colname (str): Column name containing raw amount values
    Returns:
        None
    """
    # compute total income, expenses, savings
    tot_inc = np.sum(a_grp_inc[a_amt_colname])
    tot_exp = np.sum(a_grp_exp[a_amt_colname])
    tot_sav = np.sum(a_grp_sav[a_amt_colname])
    # compute net savings (i.e., excess of income over expenses),
    # net-savings-% (% of income)
    net_sav = tot_inc - tot_exp
    # unutilized savings
    xtra_sav = net_sav - tot_sav
    # %-savings
    if tot_inc < 0:
        warning_msg = "Total income for {:s} is negative (-${:.2f})!"
        warning_msg = warning_msg.format(a_period, -tot_inc)
        warnings.warn(warning_msg)
        sav_pct = -np.inf
    else:
        sav_pct = 100.0 * net_sav / tot_inc
    # endif #
    # net savings utilization ratio (total savings : net savings)
    if net_sav < 0:
        warning_msg = "Net savings for {:s} is negative (-${:.2f})!"
        warning_msg = warning_msg.format(a_period, -net_sav)
        warnings.warn(warning_msg)
        sav_util = -np.inf
    else:
        sav_util = 100.0 * tot_sav / net_sav
    # endif #
    # compute and plot grouped expenses and income
    with open(a_report_file,'w') as rf:
        rf.write("Budget Report for {}\n".format(a_period))
        rf.write("Total income = $ {:.2f}\n".format(tot_inc))
        rf.write("Total expenses = $ {:.2f}\n".format(tot_exp))
        rf.write("Net savings = $ {:.2f}\n".format(net_sav))
        rf.write("Utilized savings = $ {:.2f}\n".format(tot_sav))
        rf.write("Unutilized savings = $ {:.2f}\n".format(xtra_sav))
        rf.write("Net savings as a % of income = {:.2f}%\n".format(sav_pct))
        rf.write("Net savings utilization ratio = {:.2f}%\n".format(sav_util))
        rf.write("\nCategory-wise income:\n")
        rf.write(a_grp_inc.to_string())
        rf.write("\n\nCategory-wise expenses:\n")
        rf.write(a_grp_exp.to_string())
        rf.write("\n\nCategory-wise savings:\n")
        rf.write(a_grp_sav.to_string())
    # endwith #
    if not os.path.exists(a_summary_file):
        with  open(a_summary_file,'w') as sf:
            sf.write("Time period,Income [$],Expenses [$],"+
                    "Utilized savings [$],"+
                    "Unutilzed savings [$],pct-savings [%]," +
                    "Savings utilization ratio [%]\n")
        # endwith #
    # endif #
    with open(a_summary_file,'a') as sf:
        sf.write("{},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}\n".format(
            a_period, tot_inc, tot_exp, tot_sav, xtra_sav, sav_pct, sav_util))
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

def main(a_args):
    """ Main function.
    Parameters of a_args:
        a_args.period (str): Time period for which transactions are processed
        a_args.report_file (str): Filename of where to store reports for
        a_args.summary_file (str): Filename where summaries of previous runs
            are stored
        a_args.tx_files (str): Name of transactions CSV file
    Returns:
        None
    """
    inc = pd.DataFrame()
    exp = pd.DataFrame()
    sav = pd.DataFrame()
    for tx_file in a_args.tx_files:
        # read the transaction file
        i, e, s = read_tx_file(tx_file)
        inc = inc.append(i)
        exp = exp.append(e)
        sav = sav.append(s)
    # endfor #
    # categorize expenses and income
    grp_inc = categorize_tx(inc)
    grp_exp = categorize_tx(exp)
    grp_sav = categorize_tx(sav)
    # compute total expenses, income, savings, %-savings, and write reports
    write_reports(a_args.report_file, a_args.period, grp_inc, grp_exp, grp_sav,
            a_args.summary_file)
    # plot category breakdown for this period and overall summary
    plot_tallied_tx(grp_inc, "Income", "Plot_Income_" + a_args.period + ".png")
    plot_tallied_tx(grp_exp, "Expenses",
            "Plot_Expenses_" + a_args.period + ".png")
    plot_tallied_tx(grp_sav,
            "Savings", "Plot_Savings_" + a_args.period + ".png")
# enddef main() #

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("period", help="Time period including all transactions",
            default="Test period")
    parser.add_argument("report_file", help="Name of report file",
            default="TestPeriod_report.txt")
    parser.add_argument("summary_file", help="Name of summary file",
            default="TestPeriod_summary.csv")
    parser.add_argument("tx_files", nargs='+',
            help="Names of transaction files")
    args = parser.parse_args()
    main(args)
# endif #
