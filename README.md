There are simply too many variables involved with choosing a healthcare plan. About 80% of Americans get their health insurance through their employer, but the rest are left uninsured or must enroll through the national marketplace (Healthcare.gov) or their state's marketplace (if it exists). 

In the first case, individuals may only have a couple plans to choose from. In the second case, there are often hundreds of plans to choose from. But in both cases, making a data-driven decision based on your expected utilization of your healthcare plan can save you hundreds, or even thousands, of dollars in premiums, copays, and coinsurance per year. Choosing the most optimal healthcare plan may have the highest savings to effort ratio of any decision the average American makes each year (especially if they expect more than trivial usage of their insurance).

The decision in complex and simply cannot be done in one's head. For instance, say you know you're going to have 26 therapy appointments during the year. You'll probably want to choose a plan that offers a low copay or coinsurance for therapy, but what if one has a $400/month premium, a $500 deductible, and a $20 copay per session after the deductilbe and another has a $300/month premium, $2,000 deductible, and $40 copay per session (pre and post deductible)? Perhaps you could do the math out for a few plans, but as your the services you expect to use and the number of plans you're considering increases, the calculation can become unwiedly very quickly. 

Ultimately, you'll want to setup a spreadsheet, [like this (very imperfect) one](https://docs.google.com/spreadsheets/d/1Dj7ByXN1VB9tY30mQa4egjzMh-g8uSSSay7W6qGdRnU/edit?usp=sharing), which lists all of your expected visits/labs/procedures (e.g. 4 primary care visits, 2 specialist visits, 20 therapy appointments, 2 bloodworks), the pre and post-deductible cost for all of them, and calculate the expected cost to you accounting for all of these variables.

This repository can act as a starting point to precisely calculating the best insurance plan for you (or your company if you're an employer). Ideally, you could drop any Summary of Benefits and Coverage PDF and this script would parse it, but that's well beyond it's capabilities right now.
 
However, for individuals or employers in New York State who are considering enrolling through the marketplace or the Small Business Marketplace (SHOP) respectively, this scraper + parser should be pretty comprehensive and accurate. It's able to scrape all of the 130+ individual and 40+ SHOP plans (as of 2025) and pull the data you need from them for your calculations. 
