# scp-recommender
A simple recommender which aims to assist users of the SCP wiki in finding new articles to read.

# Issues
The scraper only checks pages tagged with one of the 4 most popular formats: goi-format, scp, tale, hub.
If something does not have one of these tags, it will not show up in the scraper

# The absolute state of this project
So, I started this project as a way to learn a little bit about data science and make a cool thing at the end. I have learned a few lessons about collaborative filtering and the like which have gotten me to this point, which generates the similarities between users. However, something else I learned is that I should have done this in a completely different way, after learning the theoretical basis for machine learning. 

I'm going to come back to this over the summer, and try to turn it into a fully functioning recommender with a web frontend. I might even host it somewhere. But it will probably have very few similarities to this project in terms of how it reccomends things. The webscraper will largely be the same, however (though it may support tag scraping and getting other information).
