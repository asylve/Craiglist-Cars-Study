import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from datetime import date

#This header will be added to requests to identify the user to the web admin
headers = {'user-agent': 'Alex Sylvester/Vancouver, alexander.d.sylvester@gmail.com'}

urls = [
    'https://vancouver.craigslist.org/search/van/ct', #vancouver 
    'https://vancouver.craigslist.org/search/pml/ct', #tricities
    'https://vancouver.craigslist.org/search/rch/ct', #richmond
    'https://vancouver.craigslist.org/search/nvn/ct', #north shore
    'https://vancouver.craigslist.org/search/rds/ct', #delta surrey langley
    'https://vancouver.craigslist.org/search/bnc/ct', #burnaby/newwest
    'https://comoxvalley.craigslist.org/search/ct', #comox valley
    'https://abbotsford.craigslist.org/search/ct', #fraser valley
    'https://kamloops.craigslist.org/search/ct', #kamloops
    'https://kelowna.craigslist.org/search/ct', #kelowna
    'https://nanaimo.craigslist.org/search/ct', #nanaimo
    'https://sunshine.craigslist.org/search/ct', #sunshine coast
    'https://victoria.craigslist.org/search/ct', #victoria
]

own_deal = {'o?':'owner', 'd?':'dealer'} #add this at the end of the url to specify owner or dealer sale

car_df = pd.DataFrame({}) #create an empty dataframe to hold the all the car data

stop=False
for url in urls: #loop though base urls
    if stop:#end the loop if keyboard interupt has been pressed
        break
    for od in own_deal: #loop though owner or dealer sales
        if stop:#end the loop if keyboard interupt has been pressed
            break
        #get the first craigslist page for the url (with price above 100)
        response = requests.get(url + od + 'min_price=100', headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')#covert to beutiful soup object

        #the following few lines are from this tutorial: https://towardsdatascience.com/web-scraping-craigslist-a-complete-tutorial-c41cea4f4981
        #find the total number of posts to find the limit of the pagination
        results_num = soup.find('div', class_= 'search-legend')
        results_total = int(results_num.find('span', class_='totalcount').text) #pulled the total count of posts as the upper bound of the pages array

        #each page has 119 posts so each new page is defined as follows: s=120, s=240, s=360, and so on. So we need to step in size 120 in the np.arange function
        pages = np.arange(0, results_total+1, 120)
        
        for page in pages:
            if stop:#end the loop if keyboard interupt has been pressed
                break
            print('page:', page)
            #get request
            response = requests.get(url
                           + od
                           + "s=" #the parameter for defining the page number 
                           + str(page) #the page number in the pages array from earlier
                           + "&min_price=100") #only get entries with price above $100

            #sleep(1) #wait one second between reqests
            soup = BeautifulSoup(response.text, 'lxml')#covert to beutiful soup object
            entries = soup.find_all('li', class_='result-row') #get a list of entries on the page

            for entry in entries: #loop over the cars on the page
                try: #in case an error is thrown on some vehicle, this will stop the whole process from failing
                    price = entry.find('span', class_='result-price').text #price of the car
                    title = entry.find('a', class_='result-title hdrlnk') #get the title/link for the entry
                    car_url = title['href'] #get the url from the title

                    #sleep(1) #wait one second between reqests
                    car = requests.get(car_url) #get the web page for the car 
                    car_soup = BeautifulSoup(car.text, 'lxml') #convert the webpage to a soup object

                    location = car_soup.find(attrs={'name': 'geo.placename'})['content'] #location (eg. city)
                    latlong = car_soup.find(attrs={'name': 'geo.position'})['content'] #latitude and longitude in the post
                    body = car_soup.find('section', id = 'postingbody').text #body test of posting

                    all_attrs = car_soup.find_all('p', class_='attrgroup') #all of the vehicle attribute groups
                    make = all_attrs[0].b.text #first attribute group is the title
                    print(make)
                    attrs = all_attrs[1].find_all('span') #the rest of the attributes are grouped together
                    attrs = [attr.text for attr in attrs] #convert attributes to a list

                    car_lib = {attr.split(':')[0]: attr.split(':')[1] for attr in attrs if ':' in attr} #library to hold the attributes
                    car_lib['make'] = make #add the title to the library
                    car_lib['price'] = price #add the price to the library
                    car_lib['sale type'] = own_deal[od] #type of sale (owner or dealer)
                    car_lib['location'] = location
                    car_lib['latlong'] = latlong
                    car_lib['body text'] = body 
                    car_df = car_df.append(car_lib, ignore_index=True) #append the car data to the dataframe
                except KeyboardInterrupt:#end loop for keyboard interupt
                    stop = True
                    break
                except:#for any other interupt move to the next vehicle
                    print('missed entry!')
                    pass

car_df.drop('VIN', axis=1, inplace=True) #drop the VIN column to keep the data anonynmous

#store car data in a csv file
car_df.to_csv('cars-{}.csv'.format(date.today()))