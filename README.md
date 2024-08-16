# FDA Novel Drugs Approvals Web Scraper

## This Python project is a specialized web scraper designed to extract data on novel drug approvals from the FDA website. Novel drug approvals signify medications that have not been approved previously, distinguishing this scraper from general drug approval data collectors. The extracted data is saved to a MongoDB database for further analysis and retrieval.

### Key Features:
- Web Scraping: Automates the extraction of novel drug approval data from the FDA website.
- Data Processing: Parses and structures the scraped data into a pandas DataFrame.
- Database Integration: Saves the collected data into a MongoDB database for persistent storage and easy access.
- Historical Data Retrieval: Allows users to specify a target year and month to scrape historical novel drug approval data.
### Technologies Used:
- Python
- Selenium
- BeautifulSoup
- Pandas
- MongoDB
## Getting Started
1. Clone this repository.
   `git clone git@github.com:Skyngexe/fda_nda_scraper.git`
3. Install the required dependencies listed in requirements.txt.
4. Set up a [MongoDB database](https://www.mongodb.com/) and update the connection URI in the os.env file.
5. Click add IP address in your cluster 
6. Run the main.py script to start scraping and saving data.

Contributors:
Sky Ng 
