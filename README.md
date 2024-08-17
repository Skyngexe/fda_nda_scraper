# Automated FDA NDA Scraping Pipeline

## This Python project is a specialized web scraper that extracts information on novel drug approvals from the [FDA website](https://www.accessdata.fda.gov/scripts/cder/daf/). Novel drug approvals ([NDA](https://www.fda.gov/drugs/development-approval-process-drugs/novel-drug-approvals-fda#:~:text=Novel%20Drug%20Approvals%20at%20FDA%201%20Helping%20Guide,...%205%20Drug%20Approval%20Information%20%28CDER%20only%29%20)) refer to medications that have not been previously authorized, distinguishing this scraper from general drug approval data collectors. The scraper can retrieve both historical data and continuously update with new approvals using gcloud cloud run service. All gathered data is stored in a MongoDB database, ensuring easy access and facilitating further analysis.

### Key Features:
- Web Scraping: Automates the extraction of novel drug approval data from the FDA website.
- Data Processing: Parses and structures the scraped data into a pandas DataFrame.
- Database Integration: Saves the collected data into a MongoDB database for persistent storage and easy access.
- Historical Data Retrieval: Allows users to specify a target year and month to scrape historical novel drug approval data.
- Containerization and Automation: The scraping program for the latest data is automated using a Docker image, which has been pushed to Google Cloud and deployed on Cloud Run for seamless operation.
### Technologies Used:
- Python
- Selenium
- BeautifulSoup
- Pandas
- MongoDB
- Docker
- Google cloud 
## Getting Started (scraping only historical data) 
1. Clone this repository 
`git clone git@github.com:Skyngexe/fda_nda_scraper.git`
3. Install the required dependencies listed in requirements.txt.
4. Set up a [MongoDB database](https://www.mongodb.com/) and update the connection URI in the os.env file.
5. Click add IP address in your cluster 
6. Run the scraper.py script to start scraping and saving data  (uncomment `#scraper.scrape_historical_data('2000', 'January')` and comment `scraper.scrape_latest_data()`)
   
### Automating Data Scraping on Google Cloud Using Docker: 
1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and [glcoud CLI](https://cloud.google.com/sdk/docs/install)
2. Within scraper.py, comment `scraper.scrape_historical_data('2000', 'January')` and uncomment `scraper.scrape_latest_data()` 
3. Run the following command in the terminal within the repository's directory to build the Docker image:  
`docker build . -f dockerfile.txt`
4. Set up a repository in google cloud's Artifact Repository with a $${\color{lightgreen} PROJECT-ID}$$
5. Push the Docker Image to Google Container Registry 
6. [Create a Cloud Run job wth the Docker Image and schedule trigger](https://cloud.google.com/artifact-registry/docs/docker/pushing-and-pulling#cred-helper) (e.g. daily at 00:00 UTC) 

Contributors:
Sky Ng 
