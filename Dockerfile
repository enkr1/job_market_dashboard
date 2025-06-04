# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Add a healthcheck to ensure the container is running and responsive
# This example checks if the Scrapy process is running
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD pgrep scrapy > /dev/null || exit 1

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container at /usr/src/app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /usr/src/app
COPY . .

# Set the entrypoint for the container
# This assumes your Scrapy project is in a directory named 'scraper'
# and your spider is named 'sg_jobs'
ENTRYPOINT ["scrapy", "crawl", "sg_jobs"]
