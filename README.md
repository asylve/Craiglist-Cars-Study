# Craiglist Cars in British Columbia

- Scraped and cleaned ~37,000 Craiglist vehicle listings from southern British Columbia
- Trained a gradient boosting model to predict the market price of a listing (MAE $2,300), which can be used to help determine if an asking price is reasonable.
- Trained a linear model (MAE $6,500) to predict a dollar value for important vehicle features (ie. size, fuel type, manufacturer, odometer, etc.)
- Graphics:
  - Used an interpolation/smoothing teqnique to create contours of price vs odometer reading and age averaged over the entire region
  - Produced price distributions and depretiation time constants for the most common vehicle models and manuacturers (ie. found vehicle values and which vehicles 'hold their value' the best)
  - Produced a geographic distribution of vehicle types in the region (found trucks are more prevalent in the suburbs but SUVs are not)

# Resources

Craigslist Web Scraping: https://towardsdatascience.com/web-scraping-craigslist-a-complete-tutorial-c41cea4f4981

https://www.youtube.com/watch?v=fhi4dOhmW-g&list=PL2zq7klxX5ASFejJj80ob9ZAnBHdz5O1t&index=3&t=2269s

https://scikit-learn.org/stable/auto_examples/inspection/plot_linear_model_coefficient_interpretation.html

# 1. Web Scraping

I used the tutorial above as a basis to scrape vehicle listings from Craigslist. I needed to expand on the code a fair bit in order to scrape data from each individual vehicle listing page (as apposed to the search page which displays 120 listings at a time). In the end I was able to extract 16 features from each listing:

- body text (the main text of the listing)
- condition (eg. new, salvage)
- drive (front, rear, or 4wd)
- fuel (type of fuel)
- latlong (latitude and longitude associated with the posting)
- location (location associated with the posting, ie. 'Vancouver')
- make (year make and model of the vehicle in a string, ie. '2020 Toyota Corolla')
- odometer (odometer reading in km)
- paint color
- price (in $ CAD)
- sale type (owner or dealer)
- title status (ie. clean, rebuilt)
- transmission (manual or automatic)
- type (ie. sedan, minivan)
- cylinders (number of cylinders in the vehicles engine)
- size (ie. full-size, compact)

# 2. Data Cleaning

About 11% of the scaped data was missing values. The columns with missing values were:

- condition:  21.3%	
- drive:      24.5%
- odometer:   0.3%
- paint color:29.8%
- type:       30.7%
- cylinders:  37.4%
- size:       57.8%

I opted to fill most of this missing data before going forward.  'type', 'size', 'drive', and 'cylinders' were filled with the mode of the data, 'odometer' was filled by the mean, and 'paint color' and 'condition' were replaced with 'unknown.

Additional cleaning steps were:

- Combine 'pickup' and 'truck' into one category
- Convert the 'price' from a string to a number
- Split the latitude/longitde into distinct numerical columns
- Clean up the location column by taking only the first word of the location with some exceptions
- Split out the year, make and model of the vehicle into separate columns
- Split out the newly created model column into a base model and modifiers (many models have modifiers at the end such as 'lxt')
- Create an 'age' column by subtracting the current year from the 'year' column
- Create new columns based on if the text body contained words I selected as 'positive' (ie. 'vintage') or 'negative' (ie. 'torn'). Also created a column to indicate if the text had few (less than 30) words 

# 3. Exploratory Data Analysis (EDA)

I will include the major graphics and findings from the EDA here. Please see the 'EDA' notebook for all the details.

## 3.1 Price Histogram and Density Functions
