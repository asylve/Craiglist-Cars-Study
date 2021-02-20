# Craiglist Cars in British Columbia

- Scraped and cleaned ~37,000 Craiglist vehicle listings from southern British Columbia
- Trained a gradient boosting model to predict the market price of a listing (MAE $2,300), which can be used to help determine if an asking price is reasonable.
- Trained a linear model (MAE $6,500) to predict a dollar value for important vehicle features (ie. size, fuel type, manufacturer, odometer, etc.)
- Graphics:
  - Used an interpolation/smoothing teqnique to create contours of price vs odometer reading and age averaged over the entire region
  - Produced price distributions for most common vehicle models. Found that sellers tend to price vehicles just under round multiples of $10,000, likely as a psychological pricing strategy
  - Found depretiation time constants for the most common vehicle models and manuacturers (ie. which vehicles 'hold their value' the best: Toyota )
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

![Price Histogram](/images/price_hist.png)

Price distribution for all of the vehichles. The overall distribution is skewed right, with the most common price being between $3,000-$8,000. Note the dips in price at multiples of $10,000. This indicates a psychological pricing strategy (eg. asking $19,000 instead of $20,000 in hopes that the price will seem lower than it actually is).

![Price Density](/images/price_density.png)

Probability density of price for sedans, SUVs, and Trucks. The curves have been noramlized so the area under each curve is 1. Sedans are the most skewed to the low price end. SUVs and trucks have lower end options (under $10,000) but are also commonly found in the $30,000-$40,000 range. The psychological strategy of pricing just under multiples of $10,000 is more apparent here. This might be a good selling strategy if buyers use the pricing filter on their search with a bands at a round numbers.

Another interesting feature is the dip in trucks between $15,000 and $30,000, this may indicate there is less turnover in trucks for this price. Perhaps this means people are happy with their trucks in this range, so if you find one it could be a good buy. The mean year and odometer reading for trucks in this price range is 2010 and 170,000km, so if you find something this this it might be a good buy.

# 3.2 Price Distribution by Odometer and Year

A contourplot of price vs odometer and year can give a birds-eye view of how vehicles depreciate over their lifetime. However generating such as plot is complicated by the noise and sparsity of the pricing data. That is, for a given year and odometer reading, there can be many different prices in the dataset, and the data is not filled in in a nice grid-like fashion. To get around this, the pricing data was first interpolated, then smoothed with a moving average filter.

The plots below and to the left show the raw scattered datapoints and three different methods for interpolating into a uniform grid. The 'nearest' was chosen and smoothed using a moving average with a window of 30,000km and 3 years. The result is shown on the contour plot below and to the right.

Odometer reading is much more important than year to determine price. According to this data, a newer vehicle would only loose ~20% ($8,000) of its value after 40 years with no driving. On the other hand, the same vehicle driven 50,000km in one year would lose 20-30% of its value.

Solarized dark                                                          |  Solarized Ocean
:----------------------------------------------------------------------:|:-----------------------------------------------:
!![Interpolation Contours](/images/pricing_contours_interpolation.png)  |  ![Price Contours](/images/price_contours.png)





# 3.3 Pricing of the Most Popular Vehicles

![pricing_popular](/images/pricing_popular.png)

# 3.4 Depreciation of the Most Popular Vehicles
![corolla_depreciation](/images/corolla_depreciation.png)
![deprecition_by_manufacturer](/images/deprecition_by_manufacturer.png)

# 3.5 Geographic Distribution of Vehicles

![geography_by_type](/images/geography_by_type.png)
