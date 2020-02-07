import pandas as pd
import requests
from bs4 import BeautifulSoup

print("Scraping Data...\n")

url = 'https://results.thecaucuses.org/'
r = requests.get(url)

print("Parsing Data...\n")

soup = BeautifulSoup(r.text,'html.parser')

precinct_county = soup.find_all("div", class_="precinct-county") # the names of each county
precinct_data = soup.find_all("div", class_="precinct-data") # all the precinct data for 104 precincts

# Make function that creates a table for each precinct
def precinct_scraper(precinct_county, precinct_data):
    """
    Takes ONE county from the table portion of results.thecaucuses.org and turns it into a pandas dataframe

    Inputs:
    -------
    precinct_county: County information in the left side margin of the page (<div class = "precinct-county">);
    precinct_data: Precinct information in the table (<div class = "precinct-data">)

    Output:
    -------
    df: DataFrame containing the precinct results from the caucus in ONE county.

    """
    precinct_listed = precinct_data.find_all("li") ## the length is determined by the number of precincts
    county_name = precinct_county.find('div', class_="wrap").text
    precincts = []
    precinct_data = []
    precinct_series = []
    counter = 0 ## used to make sure we only store results from one precinct at a time instead of the whole table
    for list_element in precinct_listed:
        element_string = list_element.contents[0] # it's either the precinct name or a value in the table
        ## Capture precinct info by finding elements with any lettters
        if any(c.isalpha() for c in element_string):  # if its a precinct name:
            precincts.append(element_string) ## append the name of the precinct
            counter = 0
        else:
            precinct_data.append(element_string)
            counter += 1
        if counter == 42:
            precinct_series.append(precinct_data)
            precinct_data = []
    precinct_dict = {precincts[i]: precinct_series[i] for i in range(len(precincts))} ## precinct match to values#
    precinct_df = pd.DataFrame(precinct_dict).T ## Result of precinct
    precinct_df['Precinct'] = precinct_df.index
    precinct_df['County'] = county_name
    precinct_df = precinct_df.reset_index(drop=True)
    cols = precinct_df.columns.tolist()
    cols.insert(0, cols.pop(cols.index('County')))
    cols.insert(1, cols.pop(cols.index('Precinct')))
    precinct_df = precinct_df.loc[:,cols]
    return precinct_df

##
assert len(precinct_data) == len(precinct_county), "Dimension Mismatch"

n_counties = len(precinct_county)

for i in range(n_counties):
    if i == 0: ## initialize the dataframe
        df = precinct_scraper(precinct_county[i], precinct_data[i])
    df = df.append(precinct_scraper(precinct_county[i], precinct_data[i])) ## add on to it

## Print Results
print("Saving results...\n")
df.to_csv('precinct_results.csv', index=False)
print("Done!")
