import flask
from flask import Flask, jsonify, request, render_template
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
import bz2
import pickle
import _pickle as cPickle

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    url = next(request.form.values())#get the url from the web form
    
    car = scrape_url(url)#scrape the data from the webpage
    car = clean(car) #clean the data
    car.drop('price', axis=1, inplace=True)#drop the price column
    
    #locating categorical and numeric columns
    cat_cols = car.columns[car.dtypes.values=='O']#categorical columns
    for col in cat_cols:
        car[col] = car[col].astype('category')#change data type so it can be handled directly by lightgbm
    
    #load in model and make a prediction
    model = decompress_pickle('model_file.pbz2')['model']
    #model = pickle.load(open('model_file.p', 'rb'))['model']
    #model = load_models()
    prediction = model.predict(car)[0]
    #response = json.dumps({'response': prediction})
    
    yr = car['year'][0]
    make = car['make_'][0]
    model = car['model'][0]
    output = prediction
    return render_template('index.html', 
                           prediction_text='Estimated market value for this {} {} {}: ${:,.0f}'.format(yr, make, model, output))


#Compressed pickle functions from: https://betterprogramming.pub/load-fast-load-big-with-compressed-pickles-5f311584507e
#Load any compressed pickle file
def decompress_pickle(file):
    data = bz2.BZ2File(file, 'rb')
    data = cPickle.load(data)
    return data

def scrape_url(url):
    #load parameters found in initial cleaning (we need the columns here)
    file_name = "clean_data.p"
    with open(file_name, 'rb') as pickled:
        data = pickle.load(pickled)
        clean_params = data['clean_data']
        
        
    car_df = pd.DataFrame(columns = clean_params['columns']) #create an empty dataframe to hold the all the car data
    try: #in case an error is thrown on some vehicle, this will stop the whole process from failing
        #price = entry.find('span', class_='result-price').text #price of the car
        #title = entry.find('a', class_='result-title hdrlnk') #get the title/link for the entry

        car = requests.get(url) #get the web page for the car 
        car_soup = BeautifulSoup(car.text, 'lxml') #convert the webpage to a soup object

        price = car_soup.find('span', class_='price').text
        if 'cto' in url: own_deal = 'owner'
        else: own_deal = 'dealer'
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
        car_lib['sale type'] = own_deal #type of sale (owner or dealer)
        car_lib['location'] = location
        car_lib['latlong'] = latlong
        car_lib['body text'] = body 
        car_df = car_df.append(car_lib, ignore_index=True) #append the car data to the dataframe
    except:#for any other interupt move to the next vehicle
        print('missed entry!')
        pass
    
    try: 
        car_df.drop('VIN', axis=1, inplace=True) #drop the VIN column (if it is there) to keep the data anonynmous
    except: pass

    return(car_df)

def clean(df):
    #load parameters found in initial cleaning
    file_name = "clean_data.p"
    with open(file_name, 'rb') as pickled:
        data = pickle.load(pickled)
        clean_params = data['clean_data']
    
    cars = df#the dataframe is a single row containing our vehicle
    #filling missing data
    fill_lib = { #this library specifies how to fill missing values based on column
        'condition':'unknown',
        'odometer':clean_params['od_mean'],#fill the odometer with the mean value we got when cleaning the full dataset
        'paint color':'unknown',
        ' ':'unknown'
    }
    cars.fillna(fill_lib, inplace=True) #fill the missing values
    cars = cars.replace(' ', 'unknown') #replace blank space with 'unknown'
    
    #### type ####
    #combing 'pickup' and 'truck' types
    cars['type'] = cars['type'].replace(' pickup', ' truck')
    
    #### price #####
    #convert price column to number
    cars['price'] = cars['price'].str.replace('$', '').str.replace(',', '').astype('int')
    
    #### latlong ####
    #split latlong
    cars['latitude'] = cars['latlong'].map(lambda x: x.split(';')[0]).astype('float32')
    cars['longitude'] = cars['latlong'].map(lambda x: x.split(';')[1]).astype('float32')
    
    ####location#####
    #clean up location column - we will just take the first word to clean up data
    #make the location column all lower case avoid separating the same place into different categories
    cars['location'] = cars['location'].str.lower()
    
    #make the reaplcements below so when we take the first word the town names still make sense
    loc_lib = {
        'port ':'port-',
        'new ':'new-',
        'north ':'north-',
        'maple ':'maple-',
        'campbell ':'campbell-', 
        'fraser ':'fraser-',
        'langley city':'langley-city',
        'langley township':'langley-township',
        'pitt ':'pitt-',
        'white ':'white-',
        ',':'',
        'powell ':'powell-'
        }
    
    location_cleaned = cars['location'].map(lambda x: x.lower())
    for a, b in loc_lib.items(): #make the replacements in the library above
        location_cleaned = location_cleaned.map(lambda x: x.replace(a, b))
    
    #take the first word of the location column only as it is too specific
    cars['location_simple'] = location_cleaned.map(lambda x: x.split(' ')[0])
    
    #### year, make, model####
    #get year, make, and model from make column
    #clean up common variations or makes
    make_lib = {
        'mercedes-benz':'mercedes','mercedes benz':'mercedes',
        'smart car':'smart-car',
        'land ':'land-','range ':'range-',
        'vw':'volkswagen',
        'grand ':'grand-',
        'chevy':'chevrolet',
        'model ':'model-',
        'f150':'f-150', 'f250':'f-250', 'f350':'f-350',
        'cx9':'cx-9', 'cx5':'cx-5','cx3':'cx-3',
        'mazda3':'3',
        'santa fe':'santa-fe'
        }
    
    make_cleaned = cars['make'].map(lambda x: x.lower())
    for a, b in make_lib.items(): #make the replacements in the library above
        make_cleaned = make_cleaned.map(lambda x: x.replace(a, b))
    
    cars['year'] = make_cleaned.map(lambda x: x.split(' ', 2)[0]).astype('int')
    cars['age'] = 2021 - cars['year']
    cars['make_'] = make_cleaned.map(lambda x: x.split(' ', 2)[1])
    
    def get_third(x):
        try:
            return(x.split(' ', 2)[2])
        except:
            return('unknown') #if there is no more text then the model must be missing
    cars['model'] = make_cleaned.map(get_third)
    
    ##### text body #####
    #get a column from the body text
    pos_words = ['lady', 'off road', 'winter', 'lift', 'vintage']
    neg_words = ['crack', 'torn', 'damage', 'leak', 'missing']
    
    cars['pos_words'] = cars['body text'].map(lambda x: 1 if any(txt in x for txt in pos_words) else 0).astype(bool)
    cars['neg_words'] = cars['body text'].map(lambda x: 1 if any(txt in x for txt in neg_words) else 0).astype(bool)
    cars['low_text'] = cars['body text'].map(lambda x: 1 if len(x.split()) < 30 else 0).astype(bool) #text has less than 30 words
    
    #convert the odometer reading to an integer to save space
    cars['odometer'] = cars['odometer'].astype('int')
    
    #drop extraneous columns
    cars = cars.drop(['body text', 'latlong', 'make'], axis=1)
    
    #many of the model values ended up as a year because people put the year in twice. Deal with that here.
    years = [str(y) for y in range(1900, 2020)]#check for these years in make column
    make = cars[cars.make_.isin(years)]['model'].map(lambda x: x.split(' ')[0]) #get the actual make as the first word of the next column
    
    def get_second(x): #function to get the second word of text when it might be missing
        try:
            return(x.split(' ', 1)[1])
        except:
            return('None') #if there is no more text then the model must be missing
    
    cars.loc[make.index, 'make_'] = make.values #replace the years make with the actual make
    cars.loc[make.index, 'model'] = cars.loc[make.index, 'model'].map(get_second) #remove the year from the model column
    
    def get_second_3_parts(x): #function to get the second word of text when it might be missing
        try:
            return(x.split(' ', 2)[1])
        except:
            return('None') #if there is no more text then the model must be missing
        
    def get_third_3_parts(x): #function to get the second word of text when it might be missing
        try:
            return(x.split(' ', 2)[2])
        except:
            return('None') #if there is no more text then the model must be missing
    
    
    #split the model out into one column for each word
    cars['model0'] = cars['model'].map(lambda x: x.split(' ')[0])
    cars['model1'] = cars['model'].map(get_second_3_parts)
    cars['model2'] = cars['model'].map(get_third_3_parts)
    
    #fill unknown values in some columns by the mode of the model
    fill_mode_cols = ['type', 'size', 'drive', 'cylinders'] #for these columns we, will replace 'unknown' with the mode of that make of vehicle
    
    def fill_func(x, m):
        try:
            fill_val = m.loc[x['model0']].values[0]
            if type(fill_val) != str: return(x[col])
            elif pd.isnull(x[col]):return(fill_val)
            else: return(x[col])
        except:
            return(x[col])
    
    for col in fill_mode_cols:
        modes = clean_params[col]
        cars[col] = cars.apply(fill_func, args=(modes,), axis=1)
        
    #filling remaining missing data
    fill_lib = { #this library specifies how to fill missing values based on column
        'drive':'unknown',
        'type':'unknown',
        'cylinders':'unknown',
        'size':'unknown',
    }
    
    cars.fillna(fill_lib, inplace=True) #fill the missing values
    return(cars)

if __name__ == '__main__':
    app.run(debug=True)
