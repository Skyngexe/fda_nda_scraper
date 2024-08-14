import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv


class Scraper:

    def __init__(self):
        # Initialize Web Driver
        self.driver = webdriver.Firefox()

    def load_webpage(self, url):
        self.driver.get(url)
        toggle = self.driver.find_element(By.CLASS_NAME, 'toggle')
        toggle.click()

    def click_element(self, element):
        element.click()

    def scrape_table_columns(self):
        """
        scrape and create header row for column names
        :return: list
        """
        wrapper = self.driver.find_element(By.ID, 'example_1_wrapper')
        table = wrapper.find_element(By.ID, 'example_1')
        table_col = table.find_element(By.TAG_NAME, 'thead').find_elements(By.TAG_NAME, 'th')
        columns = [e.text for e in table_col]
        return columns

    def get_curr_scraping_year_month(self):
        """
        scrape and find current scrapping year and month
        :return: string, string
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
        :param target_year: string
        :param target_month:
        :return:
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

    def scrapping_function(self, columns):
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
    def save_data(dataframe, filename):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, filename)
        dataframe.to_csv(file_path, index=False)
        DataBase.create_db(dataframe)


class DataBase:

    @staticmethod
    def create_db(data):
        # Access the MongoDB connection URI
        load_dotenv(dotenv_path="os.env")
        mongo_url = os.getenv('MONGO_URI')
        client = MongoClient(mongo_url)
        db = client.fda
        fda_nda = db.novel_drugs_approvals

        for record in data.to_dict(orient='records'):
            # Check if the record already exists in the collection
            existing_record = fda_nda.find_one(record)

            if existing_record is None:
                result = fda_nda.insert_one(record)

        print("data written to db")


scraper = Scraper()
scraper.scrape_historical_data('2000', 'January')
