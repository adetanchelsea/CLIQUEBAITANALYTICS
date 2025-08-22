-- CLIQUE BAIT ANALYTICS PROJECT
-- Importing the datasets and creating a database

CREATE DATABASE IF NOT EXISTS CLIQUE_BAIT;
USE DATABASE CLIQUE_BAIT;

-- Creating a CSV file format
CREATE OR REPLACE FILE FORMAT CSVFF
  TYPE = 'CSV'
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  SKIP_HEADER = 1
  NULL_IF = ('\\N', 'NULL', '')
  EMPTY_FIELD_AS_NULL = TRUE
  TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS.FF';


-- Creating the five tables to be imported
CREATE OR REPLACE TABLE users (
  user_id  INTEGER,
  cookie_id STRING,
  start_date TIMESTAMP_NTZ
);

CREATE OR REPLACE TABLE events (
  visit_id  STRING,
  cookie_id STRING,
  page_id  INTEGER,
  event_type INTEGER,
  sequence_number INTEGER,
  event_time  TIMESTAMP_NTZ
);

CREATE OR REPLACE TABLE event_identifier (
  event_type  INTEGER,
  event_name  STRING
);

CREATE OR REPLACE TABLE campaign_identifier (
  campaign_id INTEGER,
  products STRING,         
  campaign_name STRING,
  start_date TIMESTAMP_NTZ,
  end_date  TIMESTAMP_NTZ
);

CREATE OR REPLACE TABLE page_hierarchy (
  page_id   INTEGER,
  page_name STRING,
  product_category STRING,
  product_id  INTEGER
);

-- After creating the tables, the five datasets were imported and matched with the existing tables.