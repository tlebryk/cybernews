An flask web app to automate compilation of cyber security related news. 
# Directory navigation:
"cybernews/spiders/" has web scrapers for websites. Within in the "cybernews/" folder there are also some documents to parse previous news clippings and scrap "noise" articles that are irrelevant to help train the learning-to-rank model. 
"notebooks/" contains code to train learning-to-rank models to rank articles by relevancy (as determined by past news clippings). 
app.py: flask app which can handle take articles as manual inputs (form entries for metadata), urls (scrapes the url and autopopulates metadata), or simply runs the daily scraper. 
app.py exports the documents in a desired format as defined in exportword.py
