# scp-recommender
A simple recommender which aims to assist users of the SCP wiki in finding new articles to read.

# Issues
The scraper only checks pages tagged with one of the 4 most popular formats: goi-format, scp, tale, hub.
If something does not have one of these tags, it will not show up in the scraper.

# To do
## Optimize
Consider saving certain dataframes to the disk, in case the server goes down (mostly for debug).

Profile for memory and CPU usage.

Look over basically every nontrivial pandas operation used.

## Features
Request recommendations with certain tags.

Add a list of "novoted" pages, which will not be suggested.

Add web components.

Add fuzzy username search.
