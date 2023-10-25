"""
Module to respond to analytic questions with SQL context using BigQuery
and Vertex AI's Codey and TextGenerationModel.
Referenced from: https://medium.com/google-cloud/build-your-own-sql-analyst-bot-88e06c1b80e8
"""

import argparse
from google.cloud import bigquery
import pandas as pd
from vertexai.language_models import CodeGenerationModel
from vertexai.preview.language_models import TextGenerationModel

# Initialize models and BigQuery client
generation_model = TextGenerationModel.from_pretrained("text-bison@001")
codey = CodeGenerationModel.from_pretrained("code-bison@001")
client = bigquery.Client()

# Configure pandas display options
pd.options.display.max_columns = 500
pd.options.display.max_rows = 500

def get_data(tables):
    """
    Fetch data from specified tables and read from or write to a file.
    
    Args:
    tables (list): List of table names to fetch data from.

    Returns:
    str: Data retrieved from the tables.
    """
    try:
        with open("./data.txt", "r", encoding="utf-8") as d:
            data = d.read()
        return data
    except FileNotFoundError:
        data = ""
        for table in tables:
            if table == 'bigquery-public-data.new_york.citibike_trips':
                querystring = f"""
                SELECT
                *
                FROM
                `{table}`
                WHERE gender != ""
                LIMIT
                5
                """
            else: # 'bigquery-public-data.new_york.citibike_stations'
                querystring = f"""
                SELECT
                *
                FROM
                `{table}`
                WHERE station_id IS NOT NULL
                LIMIT
                5
                """
            data += f"\n\nData for table: {table}:\n\n"
            data += str(client.query(querystring).result().to_dataframe())

        with open("./data.txt", "w", encoding="utf-8") as d:
            d.write(data)

        return data

def get_schemas(tables):
    """
    Fetch schemas of specified tables and read from or write to a file.
    
    Args:
    tables (list): List of table names to fetch schemas from.

    Returns:
    str: Schemas retrieved from the tables.
    """
    try:
        with open("./schemas.txt", "r", encoding="utf-8") as s:
            schemas = s.read()
        return schemas
    except FileNotFoundError:
        schemas = ""
        for table in tables:
            querystring = f"""
            SELECT
            column_name,
            data_type
            FROM
            `bigquery-public-data.new_york`.INFORMATION_SCHEMA.COLUMNS
            WHERE
            table_name = "{table.split(".")[-1]}";
            """
            schemas += f"\n\nSchema for table: {table}:\n\n"
            schemas += str(client.query(querystring).result().to_dataframe())

        with open("./schemas.txt", "w", encoding="utf-8") as s:
            s.write(schemas)

        return schemas

def get_proposed_query(question, schemas, data):
    """
    Generate a proposed SQL query based on the provided question, schemas, and data.
    
    Args:
    question (str): User's question.
    schemas (str): Schemas of the data tables.
    data (str): Data from the tables.

    Returns:
    str: Proposed SQL query.
    """
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 1024
    }

    response = codey.predict(
        prefix = f"""

    {schemas}

    {data}

    As a senior analyst, given the above schemas and data of bicycle trips in New York City, write a BigQuery SQL query to answer the following question:

    {question}

    When constructing SQL statements, follow these rules:
    - There is no `MONTH` function; if you want the month, instead use `EXTRACT(month FROM starttime) AS month`
    - The `birth_year` field tells the birth year of when the rider was born. Older riders have smaller birth years, and younger riders have larger birth years.
   
    """,
        **parameters
    )

    return response.text.replace("```sql", "").replace("```", "")

def main():
    """
    Entry point of the script. Parses arguments and orchestrates data fetching,
    query generation, and answering user's question.
    """
    parser = argparse.ArgumentParser(
        description='A program to respond to analytic questions with SQL context')
    parser.add_argument('-q', '--question', help='The users question')
    parser.add_argument('-v', '--verbose', action='store_true', help='Whether to print more detail')
    args = parser.parse_args()

    if not args.question:
        print("You must enter a question")
        return

    user_question = args.question

    tables = ['bigquery-public-data.new_york.citibike_stations',
              'bigquery-public-data.new_york.citibike_trips']
    schemas = get_schemas(tables)
    data = get_data(tables)

    proposed_query = get_proposed_query(user_question, schemas, data)
    if args.verbose:
        print("\nProposed Query: \n", proposed_query)
    query_result = client.query(proposed_query).result().to_dataframe()
    if args.verbose:
        print("BQ Query Result: \n\n", query_result, "\n")

    prompt = f"""
    Context: You are a senior business intelligence analyst.
    Use the following query result to give a detailed answer to any questions you receive: {query_result}
    If the column header is something like: "f0_" that means that you have number for your answer.
    Do not use any other information to answer the question. Only use information from the query result. Do not make up information. If you don't have enough information, say "I don't have enough information."
    Question: {user_question}
    """

    print("Answer:", generation_model.predict(prompt, temperature = 0, max_output_tokens = 1024), "\n")

if __name__ == '__main__':
    main()
