# News Headline Scrapper

Scrapes news headlines and information attached to said headlines

Applies sentiment analysis on said headlines and determine whether they indicate positive or negative news

Scope may expand in future versions

### API

Found in src/controller/scrapper_controller.py

#### News Scrapper API <br/>

`/api/scrape/<news_source>/<ticker_symbol>?getDate=0&getSentiment=0`

Input: 

```
news_source: known news source (cnbc, seekingalpha, benzinga)
ticker_symbol: (eg: AAPL for Apple Inc.)
getDate, getSentiment: optional parameters on date and headline sentiment where 0 is False and 1 is True
withinHours: optional parameters to scrape only news with publish times no larger than the value of withinHours, defaults to 24
```

Using the URL:

`http://localhost:9005/api/scrape/benzinga/amzn?getDate=1&getSentiment=1&withinHours=40`

With JSON body:

```
{
    "walkingPattern": "//div[@id=\"stories-headlines\"][0]/ul[0]/li[@class=\"story\"]",
    "headlinePattern": "//a",
    "datePattern": "//span[@class=\"date\"]"
}
```

Will return the following result:

```
{
    "source": "BENZINGA",
    "resultSet": [
        {
            "date": 1554927023,
            "directHeadline": false,
            "headline": "Jumia Technologies IPO: What You Need To Know",
            "polarity": 0,
            "subjectivity": 0,
            "url": "https://www.benzinga.com/news/19/04/13493499/jumia-technologies-ipo-what-you-need-to-know"
        },
        {
            "date": 1554924214,
            "directHeadline": false,
            "headline": "Startups In Seattle: Where Are The Amazon Spin-Out Companies?",
            "polarity": 0,
            "subjectivity": 0,
            "url": "https://www.benzinga.com/news/19/04/13517836/start-ups-in-seattle-where-are-the-amazon-spin-out-companies"
        },
        {
            "date": 1554922287,
            "directHeadline": false,
            "headline": "Oracle And IBM Are Officially Out Of The Race For A Key $10B Defense Cloud Contract As Amazon And Microsoft Move Ahead",
            "polarity": 1,
            "subjectivity": 0,
            "url": "https://www.benzinga.com/news/19/04/13517832/oracle-and-ibm-are-officially-out-of-the-race-for-a-key-10b-defense-cloud-contract-as-amazon-and-mic"
        },
        ...
    ]
}
```

Where using the URL:

`http://localhost:9005/api/scrape/unknown_source/AAPL?getDate=1&getSentiment=1`

With any JSON body will return the following result:

```
{
    "error": "Bad request with exception: Unknown new source, list of known news source includes ['cnbc', 'seekingalpha']"
}
```

Date is formatted using the utils.date\_time class <br/>

Uses optional `NEWS_DATE_FORMAT` parameters in conf/config.ini <br/>

`Eg: 4 hrs ago - CNBC.com` 

Requires:

```
[NEWS_DATE_FORMAT]
CNBC_DAY_FORMAT = days
CNBC_HOUR_FORMAT = hrs
CNBC_MINUTE_FORMAT = mins
CNBC_OPTIONAL_SPLIT = -
CNBC_DATE_INDEX = 0
```

Where `_DAY_FORMAT`, `_HOUR_FORMAT` and `_MINUTE_FORMAT` let the program know the letters prior to such strings are their relative day/hour/minute

Where `_OPTIONAL_SPLIT` is to deal with cases where the date data comes with values that do not have any significance to the date itself and `_DATE_INDEX` is the location of the data after the split 
#### Find company name by ticker symbol

`/api/get_company_name/<ticker_symbol>`

Using the URL:

`http://localhost:9005/api/get_company_name/AAPL`

Will return the following result:

```
{
    "name": "Apple Inc."
}
```

#### Find list of company suggestions by ticker symbol

`/api/get_company_suggestion/<ticker_symbol>`

Return a list of suggestion based on input ticker_symbol (To later support type-ahead)

Using the URL:

`http://localhost:9005/api/get_company_suggestion/AAPL`

Will return the following result:

```
{
    "ResultSet": [
        {
            "name": "Apple Inc.",
            "symbol": "AAPL"
        },
        {
            "name": "NYSE Leveraged 2x AAPL Index",
            "symbol": "^NY2LAAPL"
        },
        {
            "name": "Apple Inc.",
            "symbol": "AAPL.MX"
        },
        ...
    ]
}
```

### Requirements

Python 3

### Build Project

```
py setup.py install
py setup.py build
py src\main.py
```