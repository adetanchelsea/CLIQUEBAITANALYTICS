# Clique Bait Marketing Analysis with Snowflake 

This project was inspired by the 8 Week SQL Challenge, specifically Case Study 6 — Clique Bait. Clique Bait is an online seafood store that runs digital marketing campaigns to attract customers. The goal of this case study was to analyze user behavior on the website, track the effectiveness of campaigns, and understand the product purchase funnel.

I carried out this analysis using Snowflake, a cloud-based data warehouse that made it easy to store and query large datasets efficiently. Snowflake’s scalability and strong SQL support were perfect for handling the analytical queries required for this case study.

## Dataset Description

The dataset for this project was provided in the Clique Bait case study from the 8 Week SQL Challenge. It consists of five key tables that capture user activity, campaigns, and product details:

- Users: Contains information about customers who visited the website.
- Events: Tracks user activity on the website.
- Event Identifier: Maps the event type code to descriptive event names such as Page View, Add to Cart, Purchase, etc.
- Campaign Identifier: Provides details of marketing campaigns, associated products, and campaign start and end dates.
- Page Hierarchy: Contains information about each website page, its page id, name, product category, and product id.

## Data Modelling in Snowflake

To structure the data for analysis, I created a schema named clique_bait in Snowflake and defined tables based on the provided dataset. Below is the ERD (Entity Relationship Diagram) used to visualize the relationships between the tables:

![ERD](../images/erd.webp)

## EXPLORATORY ANALYSIS IN SNOWFLAKE

1. How many users are there?


```python
SELECT DISTINCT COUNT(*) FROM USERS;
```

![ERD](../Downloads/one.jpg)

2. How many cookies does each user have on average?


```python
SELECT 
    AVG(cookie_count) AS avg_cookies_per_user
FROM (
    SELECT USERS.USER_ID, COUNT(DISTINCT EVENTS.COOKIE_ID) AS cookie_count
    FROM users
    INNER JOIN EVENTS ON USERS.COOKIE_ID = EVENTS.COOKIE_ID
    GROUP BY USERS.USER_ID
);
```

![ERD](../Downloads/two.jpg)

3. What is the unique number of visits by all users per month?


```python
SELECT 
    TO_VARCHAR(DATE_TRUNC('month', EVENT_TIME), 'MMMM') AS month_name,
    COUNT(DISTINCT VISIT_ID) AS unique_visits
FROM EVENTS
GROUP BY DATE_TRUNC('month', EVENT_TIME)
ORDER BY unique_visits DESC
```

![ERD](../Downloads/three.jpg)

4. What is the number of events for each event type?


```python
SELECT DISTINCT (EVENTS.EVENT_TYPE) AS event_type, COUNT(EVENTS.EVENT_TYPE) AS count
FROM EVENTS
INNER JOIN EVENT_IDENTIFIER ON EVENTS.EVENT_TYPE = EVENT_IDENTIFIER.EVENT_TYPE
GROUP BY EVENTS.EVENT_TYPE
```

![ERD](../Downloads/four.jpg)

5.  What is the percentage of visits which have a purchase event?


```python
WITH visit_purchase AS (
    SELECT
        VISIT_ID,
        COUNT_IF(EVENT_TYPE = 3) > 0 AS has_purchase
    FROM EVENTS
    GROUP BY VISIT_ID
)

SELECT
    ROUND((COUNT_IF(has_purchase) * 100.0) / COUNT(*),2) AS purchase_percentage
FROM visit_purchase;
```

![ERD](../Downloads/five.jpg)

6. What are the top 3 pages by number of views?


```python
SELECT
    PAGE_HIERARCHY.PAGE_NAME,
    COUNT(*) AS view_count
FROM EVENTS
INNER JOIN PAGE_HIERARCHY ON EVENTS.PAGE_ID = PAGE_HIERARCHY.PAGE_ID 
WHERE EVENTS.EVENT_TYPE = 1
GROUP BY PAGE_HIERARCHY.PAGE_NAME
ORDER BY view_count DESC
LIMIT 3;
```

![ERD](../Downloads/six.jpg)

7. What is the percentage of visits which view the checkout page but do not have a purchase event?


```python
WITH checkout_visits AS (
    SELECT DISTINCT VISIT_ID
    FROM EVENTS
    WHERE PAGE_ID = 12 -- Checkouts
),
purchase_visits AS (
    SELECT DISTINCT VISIT_ID
    FROM EVENTS
    WHERE EVENT_TYPE = 3
)
SELECT 
    COUNT(*) AS visits_no_purchase,
    (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM checkout_visits)) AS percentage_no_purchase
FROM checkout_visits
WHERE visit_id NOT IN (SELECT visit_id FROM purchase_visits);
```

![ERD](../Downloads/seven.jpg)

To go further in the analysis, I wrote a single SQL query that generates an output table summarizing key metrics for each product, including the number of views, times added to cart, instances of cart abandonment (added to cart but not purchased), and the total purchases. Additionally, I created another aggregated table that presents the same metrics at the product category level, providing a broader view of category performance across the platform.


```python
-- Creating the first product funnel table
CREATE OR REPLACE TABLE product_funnel_summary AS
SELECT 
    P.PAGE_NAME AS product_name,
    P.PRODUCT_CATEGORY AS product_category,
    COUNT(CASE WHEN E.EVENT_TYPE = 1 THEN 1 END) AS views,
    COUNT(CASE WHEN E.EVENT_TYPE = 2 THEN 1 END) AS added_to_cart,
    COUNT(CASE WHEN E.EVENT_TYPE = 2 AND E.COOKIE_ID NOT IN (
        SELECT COOKIE_ID 
        FROM EVENTS 
        WHERE EVENT_TYPE = 3 AND PAGE_ID = P.PAGE_ID
    ) THEN 1 END) AS abandoned_carts,
    COUNT(CASE WHEN E.EVENT_TYPE = 3 THEN 1 END) AS times_purchased
FROM EVENTS E
JOIN PAGE_HIERARCHY P
    ON E.PAGE_ID = P.PAGE_ID
WHERE P.PRODUCT_ID IS NOT NULL
GROUP BY P.PAGE_NAME, P.PRODUCT_CATEGORY
ORDER BY times_purchased DESC;

SELECT * FROM product_funnel_summary;
```

![ERD](../Downloads/funnel.jpg)


```python
-- Creating the second product funnel table
CREATE OR REPLACE TABLE CATEGORY_FUNNEL_SUMMARY AS
SELECT 
    P.PRODUCT_CATEGORY,
    COUNT(CASE WHEN E.EVENT_TYPE = 1 THEN 1 END) AS TIMES_VIEWED,
    COUNT(CASE WHEN E.EVENT_TYPE = 2 THEN 1 END) AS TIMES_ADDED_TO_CART,
    COUNT(CASE WHEN E.EVENT_TYPE = 2 AND E.COOKIE_ID NOT IN (
        SELECT E2.COOKIE_ID 
        FROM EVENTS E2
        JOIN PAGE_HIERARCHY P2 
            ON E2.PAGE_ID = P2.PAGE_ID
        WHERE E2.EVENT_TYPE = 3 
          AND P2.PRODUCT_CATEGORY = P.PRODUCT_CATEGORY
    ) THEN 1 END) AS ABANDONED_CARTS,
    COUNT(CASE WHEN E.EVENT_TYPE = 3 THEN 1 END) AS TIMES_PURCHASED
FROM EVENTS E
JOIN PAGE_HIERARCHY P
    ON E.PAGE_ID = P.PAGE_ID
WHERE P.PRODUCT_CATEGORY IS NOT NULL
GROUP BY P.PRODUCT_CATEGORY
ORDER BY TIMES_PURCHASED DESC;

SELECT * FROM CATEGORY_FUNNEL_SUMMARY;
```

![ERD](../Downloads/funnel2.jpg)

8. Which product was most likely to be abandoned?


```python
SELECT 
    PRODUCT_NAME,
    ADDED_TO_CART,
    ABANDONED_CARTS,
    (ABANDONED_CARTS * 100.0 / ADDED_TO_CART) AS ABANDONMENT_RATE
FROM PRODUCT_FUNNEL_SUMMARY
WHERE ADDED_TO_CART > 0
ORDER BY ABANDONMENT_RATE DESC
LIMIT 1;
```

![ERD](../Downloads/funnel3.jpg)

9. What is the average conversion rate from view to cart add?


```python
SELECT 
    ROUND(AVG(ADDED_TO_CART * 100.0 / VIEWS), 2) AS VIEW_TO_CART_CONVERSION
FROM PRODUCT_FUNNEL_SUMMARY
WHERE VIEWS > 0;
```

![ERD](../Downloads/funnel4.jpg)

## KEY INSIGHTS

- User and Visit Metrics: The platform had 1,782 users, with an average of 3.564 cookies per user, indicating moderate repeat engagement. Monthly unique visits varied significantly showing peaks in February and drops in April and May.

- Event Analysis: Among all event types, Event Type 1 occurred most frequently (20,928 times), while the least frequent event was Event Type 5 (702 times). Overall, 49.86% of visits resulted in a purchase, highlighting a strong conversion rate. However, 15.50% of visits that reached the checkout page did not convert, indicating friction in the purchase funnel.

- Page and Product Performance: The top three pages by views were: All Products — 3,174, Checkout — 2,103, and Homepage — 1,782, showing where users spend the most time. Analysis at the product level revealed that Kingfish had the highest abandonment rate at 100%, making it the most frequently abandoned product. The average conversion rate from view to cart add was 60.95%, suggesting that while users are engaged, a notable portion drops off before purchase.

## RECOMMENDATIONS

- Optimize Checkout Flow: With 15.50% of checkout visits not converting, simplifying the checkout process (fewer steps and clear pricing) could reduce abandonment and increase purchases.
- Retarget High-Abandonment Products: For Kingfish and other abandoned products, implement targeted campaigns such as reminders, discounts, or bundles to recover potential sales.
- Focus Marketing on High-Traffic Pages: Promote campaigns around the All Products page, Checkout, and Homepage, as these - attract the most engagement and are key touchpoints in the conversion funnel.
- Monitor Engagement Trends: Track monthly variations in visits and user engagement to identify periods of high and low activity. This can help schedule campaigns more effectively.
- Boost Conversion Rates: With a 60.95% view-to-cart conversion, there’s room to improve product page design, recommendations, and call-to-action placements to encourage more users to add items to the cart and complete purchases.


```python

```
