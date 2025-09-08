# Clique Bait Analytics with SnowFlake and Streamlit 📊

In this repository, I documented the code and resources used in carrying out an exploratory analytics on SnowSQL and building a dashboard with Streamlit on Snowflake. 


## Table of Contents
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Project Setup](#project-setup)
  -  [Prerequisites](#prerequisites)
  -  [Installation](#installation)
  -  [Environment Variables](#environment-variables)
- [How It Works](#how-it-works)
- [Usage](#usage)
---
## Project Overview
This project was inspired by the **8-Week SQL Challenge (Case Study 6 – Clique Bait)**.  
Clique Bait is an online seafood store that runs digital marketing campaigns to attract customers.  
The goal of this project was to **analyze user behavior**, **track campaign effectiveness**, and **understand the product purchase funnel**.  
To make the insights interactive and accessible, I built a **Streamlit dashboard** that visualizes outputs directly from Snowflake.


## Key Features
- **Interactive Dashboard with Streamlit** – Explore user behavior, funnel analysis, campaign performance, and product-category insights.  
- **Real-time Snowflake Integration** – Pulls live data using Snowpark/Python connector for up-to-date analysis.  
- **KPI Highlights** – Total users, average cookies per user, conversion rates, abandoned products, top pages, and more.  
- **Visual Analytics** – Line charts, bar charts, pie charts, and detailed data tables.  
- **Downloadable Reports** – Export product funnel, campaign performance, and checkout/conversion data as CSV.

## Architecture

## Tools & Technologies Used
- **Snowflake** – Cloud-based data warehouse for storing and querying large datasets.  
- **SQL** – Extracting insights such as user engagement, conversions, and campaign performance.  
- **Python & Pandas** – Data manipulation and integration with Streamlit.  
- **Streamlit** – Interactive dashboard for visualization of metrics and trends.

## Project Setup
### Prerequisites
Before you begin, ensure you have the following:
- A **Snowflake account** (for running SQL queries and hosting data).
- SnowSQL or **Snowflake Web UI** access.
- Access to Streamlit Apps in Snowflake.

### Installation
Since this project is executed primarily in Snowflake, you mostly just need to open an account in Snowflake.  
However, if you want to clone this repository for reference or run any supporting scripts:

```bash
# Clone this repository
git clone https://github.com/adetanchelsea/CLIQUEBAITANALYTICS.git
cd CLIQUEBAITANALYTICS
```

### Environment Variables

To securely connect to Snowflake, you need to set up the following credentials in your environment:

```env
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=clique_bait
```

## How It Works

### 1. **Data Loading**
- Load all five datasets (**Users**, **Events**, **Event Identifier**, **Campaign Identifier**, **Page Hierarchy**) into a **Snowflake schema** named `clique_bait`.

### 2. **Data Modeling**
- Design the **Entity Relationship Diagram (ERD)** using dbdiagram.io.
- Define relationships between users, events, campaigns, and page hierarchy for seamless querying.

### 3. **SQL Analysis**
- Write and execute **SQL queries in Snowflake** to:
  - Analyze user behavior and event flows.
  - Calculate conversion rates and abandonment metrics.
  - Evaluate campaign and product-level performance.

### 4. **Insight Generation**
- Aggregate results into **summary tables** for easier reporting.
- Highlight key metrics such as:
  - Top-viewed pages and products.
  - Conversion funnel drop-off points.
  - Campaign effectiveness.

### 5. **Streamlit Dashboard**
- Build an **interactive dashboard** with:
  - KPI cards for quick stats.
  - Charts and tables for funnel visualization.
  - Filters for campaigns, dates, and product categories.

## Usage

### 1. Access the Snowflake SQL Queries
- Navigate to the `dbcreation.sql/` & `analysis.sql` files in this repository to create your database, load data and generate insights.

### 2. View the Streamlit Dashboard
- The interactive dashboard can be launched from **Streamlit** (if running locally):
```bash
streamlit run cliquebaitdashboard.py
```
### 3. Interact with the Streamlit Dashboard.
