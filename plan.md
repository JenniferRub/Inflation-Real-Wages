# Question: How has inflation affected real wage growth in the United States over the last 20 years?

I expect to find that periods of higher inflation are associated with lower real wage growth. When prices increase faster than wages, workers lose purchasing power, so real wages may grow more slowly or even decrease.

# Data sources:

I will use data from the Federal Reserve Economic Data (FRED)

I plan to use:

- Consumer Price Index (CPI) to measure inflation.
- Average Hourly Earnings to measure wages.

# Cleaning and Chart:

I plan to create:

- A line chart showing inflation and real wage growth over time.
- A scatter plot comparing inflation with real wage growth.

I will also run a simple linear regression to examine the relationship between inflation and real wage growth.

# Expected results:

My expectation would be supported if higher inflation is associated with lower real wage growth and the regression shows a negative relationship between the two variables.

My expectation would be contradicted if higher inflation is associated with higher real wage growth or if there is little or no relationship between the variables.

# Revised plan (after feedback)

The original plan did not list series IDs, dates, or cleaning steps, and its test was partly built in by definition. This section fills those gaps. The question and data sources are unchanged.

## Data

| FRED ID | Series | Frequency | Units |
|---|---|---|---|
| `CPIAUCSL` | Consumer Price Index for All Urban Consumers: All Items, seasonally adjusted | Monthly | Index, 1982–84 = 100 |
| `CES0500000003` | Average Hourly Earnings of All Employees, Total Private, seasonally adjusted | Monthly | Dollars per hour |

- Pulled from the FRED API with `fredapi`. The key is stored in `.env` as `FRED_API_KEY`.
- **Dates:** the 20 years ending with the latest month both series have. Average Hourly Earnings starts in March 2006 and each growth rate needs 12 earlier months, so the sample runs from March 2007 to the latest month (August 2026 at the time of the analysis, 233 months).

## Cleaning steps

1. Join the two series by month and drop months where either is missing.
2. Build the real wage: hourly earnings × (latest CPI ÷ CPI that month), in dollars at the latest month's prices.
3. Compute year-over-year percent changes (each month vs. the same month a year earlier) for CPI (inflation), nominal earnings, and real earnings.
4. Drop the first 12 months, which have no growth rate, and keep the last 20 years.
5. Flag 2020–2021 for a robustness check, because pandemic job losses among low-wage workers pushed average hourly earnings up artificially.

## Analysis

1. Line chart of inflation and real wage growth over time.
2. Scatter plot and regression of real wage growth on inflation.
3. **Regression of nominal wage growth on inflation.** Real wage growth is roughly nominal wage growth minus inflation, so a negative slope in step 2 is partly built in. The nominal regression tests whether wages keep up with prices.
4. Repeat both regressions without 2020–2021.

## Revised test

- **Supported** if the nominal wage growth slope is below 1, meaning wages rise less than prices, so real wages fall when inflation rises.
- **Contradicted** if the slope is 1 or higher, meaning wages keep up with or beat inflation.
