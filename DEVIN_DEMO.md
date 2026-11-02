# Devin demo: Analyze a CSV and get charts

**What it shows:** You ask Devin questions about a sales CSV in plain English. Devin works out the answers with Python, makes charts, and opens a pull request with the charts and a short findings note in `reports/`.

**Needs:** GitHub only

More demos: [devin-advanced-demos](https://github.com/thequantexplorer/devin-advanced-demos)

## Set it up

1. Click **Use this template → Create a new repository**, choose your GitHub account or org as the owner, and keep the name `devin-demo-csv-analysis`. The prompt below assumes that name. Use the template rather than a fork: pull requests on a fork go to the original repo by default.
2. In Devin, open [**Settings → Connections → GitHub**](https://app.devin.ai/settings/connections/github) and make sure Devin can access the new repository.

## Prompt

Go to [app.devin.ai](https://app.devin.ai), start a new session with the normal agent, and paste this. Replace `<you>` with your GitHub user or org.

The **Data Analyst** agent is built for connected databases, so it needs a database connection and isn't on free or trial plans. This data is a CSV file in a repo, so the normal agent is the right choice.

```text
I run a small online coffee-gear shop. Our orders from January to June 2026 are in https://github.com/<you>/devin-demo-csv-analysis (data/orders.csv; the README explains each column). I'm not a data person. Start by running python3 scripts/check_reports.py to see what's missing. Then answer these questions in plain English:

1. How many orders and how much revenue did we have, and what share of orders was refunded? Is that changing from month to month?
2. Which products get refunded the most, and what reasons do customers give?
3. Does the day of the week make a difference to refunds?
4. If anything looks unusual, dig in: which product, which days, which reason, and how much money it cost us.

Use Python with pandas and matplotlib. Make at least 3 simple charts (PNG files with a title and labeled axes) and save them in reports/. Write reports/findings.md: a short note (under 400 words) that answers each question, shows the charts, gives the key numbers, and ends with one or two things I should do next. Save the script that makes the charts as reports/analysis.py so I can rerun it.

Before you finish, run python3 scripts/check_reports.py and the tests, and make sure both pass. Then open a pull request with everything in reports/, and put the main finding in the PR description.
```

## What to watch

- Devin runs `python3 scripts/check_reports.py` first and sees it fail because `reports/` is empty.
- It checks the numbers before it draws conclusions, for example by comparing one product against the rest.

## Done when

- The pull request adds `reports/findings.md`, `reports/analysis.py` and at least 3 charts, and the **Report check** Action is green.
- The note names the product, the days and the main refund reason behind the spike, with numbers.
