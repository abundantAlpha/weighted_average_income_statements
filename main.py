import pandas as pd
import requests
import json


def income_statement_group_weighted_average(group: list) -> dict:
    """
    Feed the function a list of ticker symbols and the function will return a dictionary with 3 items:

    1) 'weight_df': gives a dataframe containing the list of tickers and their respective weights based on market cap
    2) 'overview_df': gives a dataframe containing the list of tickers and high level stats and information
    3) "is_wad": gives a dataframe whose index is a list of 20 periods (quarters) and whose keys are income statement
    financial measures. The values are the weighted average values for all the companies in the group
    """

    with open("config.json", "r") as config_file:
        config = json.load(config_file)
        api_key = config["api_key"]
        config_file.close()

    # instantiate empty dictionaries
    income_statement_dataframes = {}
    company_overview_dataframes = {}

    # loop over tickers, download data, make dataframes for each endpoint: company overview and income statements
    for n, ticker in enumerate(group):
        # income statement
        income_statement_url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={ticker}&apikey={api_key}'
        response = requests.get(income_statement_url)
        json_response = response.json()['quarterlyReports']
        temp = pd.DataFrame(json_response)
        income_statement_dataframes[group[n]] = temp

        # company overview
        overview_url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}'
        response = requests.get(overview_url)
        json_response = response.json()
        temp = pd.DataFrame(json_response, index=[0])
        company_overview_dataframes[group[n]] = temp

    # create dataframe with overview data for each ticker
    overview_df = pd.DataFrame()
    for n, ticker in enumerate(group):
        overview_df[n] = company_overview_dataframes[ticker].iloc[0]
    overview_df = overview_df.transpose()

    # determine company weights for weighted averages:
    denominator = 0
    for index, (ticker, dataframe) in enumerate(company_overview_dataframes.items()):
        denom_basis = int(dataframe['MarketCapitalization'].iloc[0])
        denominator += denom_basis

    company_weights = []
    for index, (ticker, dataframe) in enumerate(company_overview_dataframes.items()):
        numerator = int(dataframe['MarketCapitalization'].iloc[0])
        company_weight = numerator / denominator
        company_weights.append(company_weight)

    # create separate dataframe for the weights:
    weights_df = pd.DataFrame(group, columns=['Ticker'])
    weights_df['Weight'] = company_weights

    # get list of valid numerical keys in the income statement dataframes
    valid_keys = []
    invalid_keys = []

    # check and sort each key:
    all_income_statement_keys = [_ for _ in income_statement_dataframes[group[0]].keys()]
    for key in all_income_statement_keys:
        try:
            x = int(income_statement_dataframes[group[0]][key][0])
            valid_keys.append(key)

        except ValueError:
            invalid_keys.append(key)

    # loop through each key, each date, and each ticker to determine weighted average values for each measure for each period for all tickers
    key_values = {}
    for key in valid_keys:
        total_weighted_values_for_key_per_year = []

        for date in range(20):
            year_key_total = 0

            for index, company in enumerate(group):
                dataframe = income_statement_dataframes[company]
                weight = company_weights[index]

                try:
                    measure_value = int(dataframe.iloc[date][key]) * weight
                    year_key_total += measure_value

                except IndexError as ind_error:
                    continue

                except TypeError as typ_error:
                    continue

                except ValueError as val_error:
                    continue

            total_weighted_values_for_key_per_year.append(year_key_total)
        key_values[key] = total_weighted_values_for_key_per_year

    # construct the income statement weighted average dataframe
    income_statement_weighted_averages_dataframe = pd.DataFrame(key_values)

    # fix the index
    income_statement_weighted_averages_dataframe.sort_index(ascending=True, inplace=True)
    income_statement_weighted_averages_dataframe.reset_index(drop=True, inplace=True)

    # return dictionary with weights df, overview df, and income statement df
    return {'weight_df': weights_df,
            'overview_df': overview_df,
            'is_wad': income_statement_weighted_averages_dataframe
            }


# Inputs
companies = ['AAL', 'DAL', 'JBLU', 'LUV', 'SAVE', 'UAL', 'ULCC']
group_dict = income_statement_group_weighted_average(companies)



