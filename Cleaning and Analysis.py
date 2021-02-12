# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 17:26:51 2021

@author: a_sylvester
"""

import pandas as pd

cars = pd.read_csv('cars.csv', index_col=0)

#filling missing data
fill_lib = { #this library specifies how to fill missing values based on column
    'condition':'unknown',
    'odometer':cars['odometer'].mean(),
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
#positive = cars['body text'].str.find('lady').map(lambda x: 0 if x==-1 else 1)
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
    modes = cars.groupby('model0')[col].agg([pd.Series.mode])
    cars[col] = cars.apply(fill_func, args=(modes,), axis=1)

#filling remaining missing data
fill_lib = { #this library specifies how to fill missing values based on column
    'drive':'unknown',
    'type':'unknown',
    'cylinders':'unknown',
    'size':'unknown',
}

cars.fillna(fill_lib, inplace=True) #fill the missing values

#output data
cars.to_csv('cars_cleaned.csv', index=False)

