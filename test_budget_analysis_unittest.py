import unittest
import pandas as pd
import budget_analysis

class Test_read_tx_file(unittest.TestCase):

    def test_empty_file_read_tx_file(self):
        with self.assertRaises(FileNotFoundError):
            budget_analysis.read_tx_file("non_existent_file")
        # endwith #
    # enddef test_empty_file_read_tx_file() #

    def test_nonempty_file_read_tx_file(self):
        # get the dataframes from the sample transactions file
        exp, inc = budget_analysis.read_tx_file( "Transactions.csv")
        # Ideally, exp and inc should look like:
        # inc:
        #          Category  Amount
        #0       Utilities   100.0
        #1           Gifts  5007.0
        #2       Utilities   350.0
        #3  Transportation     3.0
        # exp:
        #   Category  Amount
        #0  Paycheck  1500.0

        # check shape of exp df
        self.assertEqual(exp.shape, (4,2), "Should be 4.")
        # check shape of inc df
        self.assertEqual(inc.shape, (1,2), "Should be 1.")
        # check categories of exp df
        self.assertEqual(exp['Category'].tolist(),
                ['Utilities', 'Gifts', 'Utilities', 'Transportation'],
                "Category names should be" +
                "['Utilities', 'Gifts', 'Utilities', 'Transportation']")
        # check categories of inc df
        self.assertEqual(inc['Category'].tolist(),
                ['Paycheck'], "Category names should be ['Paycheck']")
        # check amounts in exp df
        self.assertEqual(exp['Amount'].tolist(),
                [100.0, 5007.0, 350.0, 3.0],
                "Amounts names should be" +
                "[100.0, 5007.0, 350.0, 3.0]")
        # check amounts in inc df
        self.assertEqual(inc['Amount'].tolist(),
                [1500.0], "Amounts names should be [1500.0]")
    # enddef test_nonempty_file_read_tx_file() #
# endclass Test_read_tx_file #

class Test_categorize_tx(unittest.TestCase):

    def test_empty_tx_categorize_tx(self):
        with self.assertRaises(KeyError):
            budget_analysis.categorize_tx(pd.DataFrame(), "title", "tmp/plot")
        # endwith #
    # enddef test_empty_tx_categorize_tx() #

    def test_nonempty_tx_categorize_tx(self):
        exp, _ = budget_analysis.read_tx_file( "Transactions.csv")
        grouped_exp = budget_analysis.categorize_tx(exp, "title", "tmp/plot")
        # Ideally, grouped_exp would look like
        #                        Amount  Contribution [%]
        #Category
        #Gifts           5007.0         91.703297
        #Transportation     3.0          0.054945
        #Utilities        450.0          8.241758
        # check categories of grouped_exp df
        self.assertEqual(grouped_exp.index.tolist(),
                ['Gifts',  'Transportation', 'Utilities'],
                "Category names should be" +
                "[ 'Gifts',  'Transportation', 'Utilities']")
        # check amounts in grouped_exp df
        self.assertEqual(grouped_exp['Amount'].tolist(),
                [5007.0, 3.0, 450.0],
                "Amounts names should be [5007.0, 3.0, 450.0]")
        # check contribution [%] in grouped_exp df
        self.assertEqual(grouped_exp['Contribution [%]'].tolist(),
                [91.7032967032967, 0.054945054945054944, 8.241758241758241],
                "Amounts names should be [91.703297,0.054945,8.241758]")
    # enddef test_nonempty_tx_categorize_tx() #
# endclass Test_categorize_tx #

class Test_main(unittest.TestCase):

    def test_empty_file_main(self):
        with self.assertRaises(FileNotFoundError):
            budget_analysis.main("non_existent_file",
                    "TestPeriod", "ReportFile")
        # endwith #
    # enddef test_empty_file_main() #

    def test_nonnumeric_prev_bal_main(self):
        with self.assertRaises(AssertionError):
            budget_analysis.main("Transactions.csv", "TestPeriod",
                    "tmp/ReportFile", "t9djafo", "tmp/SummaryFile", "tmp/Trend")
    # enddef test_nonnumeric_prev_bal_main() #
# enclass Test_main() #

if __name__ == "__main__":
    unittest.main()
# endif #
