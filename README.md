# Craiglist Cars Study

- Scraped and cleaned ~37,000 Craiglist vehicle listings from southern British Columbia
- Trained a gradient boosting model to predict the market price of a listing (MAE $2,300), which can be used to help determine if an asking price is reasonable.
- Trained a linear model (MAE $6,500) to predict a dollar value for important vehicle features (ie. size, fuel type, manufacturer, odometer, etc.)
- Graphics:
  - Used an interpolation/smoothing teqnique to create contours of price vs odometer reading and age averaged over the entire region
  - Produced price distributions and depretiation time constants for the most common vehicle models and manuacturers (ie. found vehicle values and which vehicles 'hold their value' the best)
  - Produced a geographic distribution of vehicle types in the region (found trucks are more prevalent in the suburbs but SUVs are not)

# Resources

https://towardsdatascience.com/web-scraping-craigslist-a-complete-tutorial-c41cea4f4981

https://www.youtube.com/watch?v=fhi4dOhmW-g&list=PL2zq7klxX5ASFejJj80ob9ZAnBHdz5O1t&index=3&t=2269s

https://scikit-learn.org/stable/auto_examples/inspection/plot_linear_model_coefficient_interpretation.html
