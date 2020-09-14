#!/anaconda3/bin/python
"""
Author: Shrikant Kshirsagar
Purpose: To summarize year-to-date budget from tallied monthly budget sheets
License: GPLv3+
"""

import sys
import warnings
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def summarize_all_periods(a_initial_net_worth, a_summary_file,
        a_inc_colname="Income [$]", a_exp_colname="Expenses [$]",
        a_sav_colname="Utilized savings [$]"):
    """ Summarize YTD results from monthly summary file
    Parameters:
        a_initial_net_worth (float): Net worth at beginning of year
        a_summary_file (str): Filename containing period summary for
            different periods
        a_inc_colname (str): Column name of income column
        a_exp_colname (str): Column name of expenses column
        a_sav_colname (str): Column name of savings column
    Returns:
        summary_df (DataFrame): DataFrame of summary file with "Net worth [$]"
            column appended
    """
    # read summary file
    summary_df = pd.read_csv(a_summary_file)
    # compute total income, expenses and savings for all periods
    total_income = summary_df[a_inc_colname].sum()
    total_expenses = summary_df[a_exp_colname].sum()
    total_savings = summary_df[a_sav_colname].sum()
    net_savings = total_income - total_expenses
    extra_savings = net_savings - total_savings
    # if total income < 0, %-savings is undefined
    if total_income < 0:
        warning_msg = "Total income is negative (-${:.2f})!"
        warning_msg = warning_msg.format(-total_income)
        warnings.warn(warning_msg)
        net_sav_pct = -np.inf
    else:
        net_sav_pct = 100.0 * net_savings / total_income
    # endif #
    # net savings utilization ratio
    if net_savings < 0:
        warning_msg = "Net savings is negative (-${:.2f})!"
        warning_msg = warning_msg.format(-net_savings)
        warnings.warn(warning_msg)
        sav_util = -np.inf
    else:
        sav_util = 100.0 * total_savings / net_savings
    # endif #
    with open(a_summary_file,'a') as sf:
        sf.write("\nTotal,{:.2f},{:.2f},{:.2f},{:.2f},{:.2f},{:.2f}\n".format(
            total_income, total_expenses, total_savings, extra_savings,
            net_sav_pct, sav_util))
    # endwith #
    # compute every month's net worth
    summary_df["Net worth [$]"] = (a_initial_net_worth +
            summary_df[a_inc_colname].cumsum() -
            summary_df[a_exp_colname].cumsum())
    return summary_df
# enddef summarize_all_periods() #

def plot_summary_same_axes(a_summary_df, a_summary_plot, a_period_colname,
        a_plot_cols):
    """
    Function to plot overall summary as lineplot with same axes
    Parameters:
        a_summary_df (DataFrame): DataFrame containing summary file + net worth
        a_summary_plot (str): Filename where trendline summaries are to be
            plotted
        a_period_colname (str): Column name containing name of period
        a_plot_cols (list(str)) : List of strings of column names containing
            quantities to be plotted
    Returns:
        None
    """
    plt.close('all')
    fig, ax = plt.subplots()
    ax.plot(a_summary_df[a_period_colname],a_summary_df[a_plot_cols])
    ax.set_ylabel('$')
    ax.legend(a_plot_cols)
    ax.minorticks_on()
    ax.grid(b=True, which='both', axis='both')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(a_summary_plot)
# enddef plot_summary_same_axes() #

def plot_summary_diff_axes(a_summary_df, a_summary_plot, a_period_colname,
        a_plot_cols):
    """
    Function to plot overall summary as lineplot with different axes
    Parameters:
        a_summary_df (DataFrame): DataFrame containing summary file + net worth
        a_summary_plot (str): Filename where trendline summaries are to be
            plotted
        a_period_colname (str): Column name containing name of period
        a_plot_cols (tuple(str)) : 2-tuple of strings of column names containing
            net-worth and %-savings in that order
    Returns:
        None
    """
    plt.close('all')
    fig, ax1 = plt.subplots()
    ax1.plot(a_summary_df[a_period_colname],a_summary_df[a_plot_cols[0]],
            color='r')
    ax1.set_ylabel('$')
    ax1.legend([a_plot_cols[0]], loc='upper left')
    ax1.minorticks_on()
    ax1.grid(b=True, which='both', axis='both', color='r', linestyle='-',
            linewidth=0.2)
    ax2 = ax1.twinx()
    ax2.plot(a_summary_df[a_period_colname], a_summary_df[a_plot_cols[1]],
            color='b')
    ax2.set_ylabel('%')
    ax2.legend([a_plot_cols[1]], loc='lower right')
    ax2.minorticks_on()
    ax2.grid(b=True, which='both', axis='both', color='b', linestyle='--',
            linewidth=0.3)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(a_summary_plot)
# enddef plot_summary_diff_axes() #

def write_summary_report(a_initial_net_worth, a_summary_df, a_report_file,
        a_period_colname, a_networth_colname):
    """ Write report of total net worth with time.
    Parameters:
        a_initial_net_worth (float): Initial net worth at the beginning of all
            periods
        a_summary_df (DataFrame): DataFrame containing summary file + net worth
        a_report_file (str): Filename of report file to write
        a_period_colname (str): Column name containing name of period
        a_networth_colname (str): Column name containing net worth
    Returns:
        None
    """
    df = pd.DataFrame(data={a_period_colname:["Start"], a_networth_colname:
        [a_initial_net_worth]})
    df = df.append(a_summary_df[[a_period_colname, a_networth_colname]])
    pct_change = 100.0 * (df[a_networth_colname].iloc[-1] /
            df[a_networth_colname].iloc[0] - 1.0)
    with open(a_report_file,'w') as rf:
        rf.write(df.to_string(index=False))
        rf.write("\n\n%-change in net worth: {:.2f}%".format(pct_change))
    # endwith #
# enddef write_summary_report() #

def main(a_initial_net_worth, a_summary_file,
        a_inc_exp_plotfile="Plot_incexp_summary.png",
        a_networth_savingspct_plotfile="Plot_networth_savingspct.png",
        a_summary_reportfile="Summary_report.txt"):
    """ Main function
    Parameters:
        a_initial_net_worth (float): Initial net worth at the beginning of all
            periods
        a_summary_file (str): Filename containing period summary for different
            periods
        a_inc_exp_plotfile (str): Filename in which to store plot of income and
            expenses with time period
        a_networth_savingspct_plotfile (str): Filename in which to store plot of
            net worth and savings percent with time period
        Returns:
            None
    """
    assert isinstance(a_initial_net_worth, (float, int)),\
        "Previous balance must be numeric."
    summary_df = summarize_all_periods(a_initial_net_worth, a_summary_file)
    plot_summary_same_axes(summary_df, a_inc_exp_plotfile, "Time period",
            ["Income [$]", "Expenses [$]"])
    plot_summary_diff_axes(summary_df, a_networth_savingspct_plotfile,
            "Time period", ("Net worth [$]", "pct-savings [%]"))
    write_summary_report(a_initial_net_worth, summary_df,
    a_summary_reportfile, "Time period", "Net worth [$]")
# enddef main() #

if __name__ == "__main__":
    passed_args = sys.argv[1:]
    passed_args[0] = float(passed_args[0])
    main(*passed_args)
    # endif #
# endif #
