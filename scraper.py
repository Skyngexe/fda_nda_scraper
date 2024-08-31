import os
import time
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv


class Scraper:

    """
        A class for web scraping historical data and saving it to a MongoDB database.
    """

    def __init__(self):
        # Initialize Web Driver
        opts = webdriver.FirefoxOptions()
        opts.add_argument("--headless")
        self.driver = webdriver.Firefox(options=opts)

    def load_webpage(self, url):
        """
        Load a webpage in the web driver.

        Parameters:
        url (str): The URL of the webpage to load.
        """
        self.driver.get(url)
        toggle = self.driver.find_element(By.CLASS_NAME, 'toggle')
        toggle.click()

    def click_element(self, element):
        """
        Click on a specified web element.

        Parameters:
        element: The web element to click.
        """
        element.click()

    def scrape_table_columns(self):
        """
        Scrape and create a header row for column names.

        Returns:
        list: A list of column names.
        """
        wrapper = self.driver.find_element(By.ID, 'example_1_wrapper')
        table = wrapper.find_element(By.ID, 'example_1')
        table_col = table.find_element(By.TAG_NAME, 'thead').find_elements(By.TAG_NAME, 'th')
        columns = [e.text for e in table_col]
        return columns

    def get_curr_scraping_year_month(self):
        """
        Scrape and find the current scraping year and month.

        Returns:
        tuple: A tuple containing the current year and month.
        """
        date = self.driver.find_element(By.XPATH, '/html/body/div[2]/div/main/article/div/form/h4')
        html_code = date.get_attribute('outerHTML')
        soup = BeautifulSoup(html_code, 'html.parser')
        h4_tag = soup.find('h4')
        year_month = h4_tag.get_text(separator=' ').split('<br>')[0].split('\n')
        year_month = year_month[-3].strip().split(' ')
        return year_month[0], year_month[1]

    def scrape_historical_data(self, target_year, target_month):
        """
        Scrape historical data for a target year and month.

        Parameters:
        target_year (str): The target year for scraping.
        target_month (str): The target month for scraping.
        """

        try:
            print("Initiating web scraping...")
            self.load_webpage("https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm")
            checkbox = self.driver.find_element(By.ID, 'OriginalNewDrugApprovals')
            self.click_element(checkbox)

            search_button = self.driver.find_element(By.XPATH, '/html/body/div[2]/div/main/article/div/div[5]/div[2]/div/form')
            search_button.submit()

            old_url = self.driver.current_url
            WebDriverWait(self.driver, 10).until(lambda driver: old_url != driver.current_url)
            self.driver.implicitly_wait(5)

            dfs = []
            columns = self.scrape_table_columns()
            print("Webpage loaded successfully.")
            while True:
                month, year = self.get_curr_scraping_year_month()
                print(f"currently scraping {month, year}")
                if year == target_year and month == target_month:
                    dfs.append(self.scrapping_function(columns))
                    break
                dfs.append(self.scrapping_function(columns))
                self.click_previous_month_button()
                time.sleep(2)

            large_df = pd.concat(dfs, ignore_index=True)

            Scraper.save_data(large_df, "output.csv")

        except Exception as e:
            print(f"An error occurred during scraping: {e}")

        finally:
            self.driver.quit()

    def scrape_latest_data(self):
        """
        Scrape latest data
        """
        try:
            print("Initiating web scraping...")
            self.load_webpage("https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm")
            checkbox = self.driver.find_element(By.ID, 'OriginalNewDrugApprovals')
            self.click_element(checkbox)

            search_button = self.driver.find_element(By.XPATH, '/html/body/div[2]/div/main/article/div/div[5]/div[2]/div/form')
            search_button.submit()

            old_url = self.driver.current_url
            WebDriverWait(self.driver, 10).until(lambda driver: old_url != driver.current_url)
            self.driver.implicitly_wait(5)

            dfs = []
            columns = self.scrape_table_columns()
            print("Webpage loaded successfully.")
            month, year = self.get_curr_scraping_year_month()
            print(f"currently scraping {month, year}")
            dfs.append(self.scrapping_function(columns))

            large_df = pd.concat(dfs, ignore_index=True)
            #print(large_df)
            Scraper.save_data(large_df)

        except Exception as e:
            print(f"An error occurred during scraping: {e}")

        finally:
            self.driver.quit()

    def scrapping_function(self, columns):
        """
        Scrape data from a table on the webpage based on the provided columns.

        Parameters:
        columns (list): A list of column names to match the data against.

        Returns:
        pd.DataFrame: A pandas DataFrame containing the scraped data.
        """
        wrapper = self.driver.find_element(By.ID, 'example_1_wrapper')
        table = wrapper.find_element(By.ID, 'example_1')
        table_rows = table.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'td')
        row_data = []
        data = []

        for row in table_rows:
            row_data.append(row.text)
            if len(row_data) == len(columns):
                data.append(row_data)
                row_data = []

        df = pd.DataFrame(data, columns=columns)
        return df

    def click_previous_month_button(self):
        button = self.driver.find_element(By.ID, 'main-content')
        button = button.find_element(By.XPATH, '/html/body/div[2]/div/main/article/div/form/div[3]/strong/a')
        self.click_element(button)

    @staticmethod
    def save_data(dataframe):
        """
        Store data in a MongoDB database.

        Parameters:
        dataframe (pd.DataFrame): The pandas DataFrame containing the data to be saved.
        """
        DataBase.save_df_to_db(dataframe)


class Helper:
    @staticmethod
    def extract_ndc(drug_name):
        """
        Extract NDA number from the field Drug Name

        Parameters:
        drug_name(str): the drug name field of a record

        Returns:
        str: Extracted NDA number if found, else None
        """
        match = re.search(r'#(\d+)', drug_name)
        if match:
            return match.group(1)
        return None


class DataBase:
    """
        A class for interacting with a MongoDB database.
    """
    @staticmethod
    def save_df_to_db(data):
        """
        Save data in a MongoDB database.

        Parameters:
        dataframe (pd.DataFrame): The pandas DataFrame containing the data to be saved.
        """
        # Access the MongoDB connection URI
        load_dotenv(dotenv_path="os.env")
        mongo_url = os.getenv('MONGO_URI')
        client = MongoClient(mongo_url)
        db = client.fda
        fda_nda = db.novel_drugs_approvals

        for record in data.to_dict(orient='records'):
            # Check if a record with the same Approval Date and Drug Name already exists in the collection
            nda_number = Helper.extract_ndc(record["Drug Name"])
            query = {"Drug Name": {"$regex": nda_number},
                     "Approval Date": record["Approval Date"]
                     }

            results = fda_nda.find(query)

            if results:
                print(
                    f"Record with Approval Date '{record['Approval Date']}' and Drug Name '{record['Drug Name']}' already exists."
                )
                if results != record:
                    existing_fields = {k: v for k, v in results[0].items() if k != "_id"}
                    new_fields = {k: v for k, v in record.items() if k != "_id"}

                    if existing_fields != new_fields:
                        print(f"Differences found in record with NDA Number '{nda_number}':")
                        for key in new_fields.keys():
                            if existing_fields.get(key) != new_fields.get(key):
                                print(
                                    f"Field '{key}': Existing Value - {existing_fields.get(key)}, New Value - {new_fields.get(key)}")
                                fda_nda.update_one(query, {"$set": {key: new_fields.get(key)}})
                            print('record updated')

            else:
                result = fda_nda.insert_one(record)

        print("Data written to the database.")




scraper = Scraper()
#scraper.scrape_historical_data('2000', 'January')
scraper.scrape_latest_data()
