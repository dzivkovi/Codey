# SQL Analyst Bot

This project leverages Google Cloud's BigQuery and the [Vertex AI Codey APIs](https://cloud.google.com/vertex-ai/docs/generative-ai/code/code-models-overview) to generate SQL queries that answer analytic questions.

## Getting Started

These instructions will guide you on how to get the project up and running on your local machine.

### Prerequisites

Ensure you have the following installed on your local machine:

- Python 3.x
- Google Cloud SDK

### Setup

1. Clone this repository to your local machine.

2. Install the necessary Python packages using the provided requirements.txt file:

    ```bash
    pip install -r requirements.txt
    ```

3. Authenticate with Google Cloud:

    ```bash
    gcloud auth login
    ```

4. Set your Google Cloud project:

    ```bash
    gcloud config set project your-project-id
    ```

5. Allow access to the Vertex AI APIs from your service account:

    ```bash
    gcloud projects add-iam-policy-binding your-project-id --member=serviceAccount:your-service-account-email --role=roles/aiplatform.user
    ```

    - Replace your-project-id with your Google Cloud Project ID.
    - Replace your-service-account-email with the email found in the client_email field of your GOOGLE_APPLICATION_CREDENTIALS file.

## Usage

Run the main script, providing your question as an argument.

### Examples

1. Finding the top 3 months with the most trips:

    ```bash
    python cli_analyst.py -v -q "Which 3 months are the most trips taken in?"
    ```

2. Identifying stations where the most trips started:

    ```bash
    python cli_analyst.py -v -q "Give me station IDs for the stations where the most trips started? Also print the number of trips"
    ```

3. Calculating the total number of female rides per year:

    ```bash
    python cli_analyst.py -v -q "please print total number of female rides per year, and print the year too"
    ```

## More Info

For more detailed information and understanding of the code, refer to the [original article](https://medium.com/google-cloud/build-your-own-sql-analyst-bot-88e06c1b80e8).
