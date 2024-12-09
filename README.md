# About
Returns a dictionary containing the following 3 items for a user-defined list of company tickers.

1) 'weight_df': gives a dataframe containing the list of tickers and their respective weights based on market cap
2) 'overview_df': gives a dataframe containing the list of tickers and high level stats and information
3) "is_wad": gives a dataframe which is the weighted average income statement for the list of companies provided

The idea is that you can enter a list of comparable companies, and come up with a combined income statement weighted by market cap, and compare any individual company to the weighted average to determine relative performance. 
