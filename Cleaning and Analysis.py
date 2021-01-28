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
    'drive':'unknown',
    'odometer':cars['odometer'].mean(),
    'paint color':'unknown',
    'type':'unknown',
    'cylinders':'unknown',
    'size':'unknown',
}

cars.fillna(fill_lib, inplace=True) #fill the missing values

#convert price column to number
cars['price'] = cars['price'].str.replace('$', '').str.replace(',', '').astype('int')

#split latlong
cars['latitude'] = cars['latlong'].map(lambda x: x.split(';')[0]).astype('float32')
cars['longitude'] = cars['latlong'].map(lambda x: x.split(';')[1]).astype('float32')

#get year, make, and model from make column
#clean up common variations or makes
make_lib = {
    'mercedes-benz':'mercedes',
    'mercedes benz':'mercedes',
    'smart car':'smart-car',
    'land rover':'land-rover',
    'vw':'volkswagen',
    }

make_cleaned = cars['make'].map(lambda x: x.lower())
for a, b in make_lib.items():
    make_cleaned = make_cleaned.map(lambda x: x.replace(a, b))

cars['year'] = make_cleaned.map(lambda x: x.split(' ', 2)[0]).astype('int')
cars['age'] = 2021 - cars['year']
cars['make_'] = make_cleaned.map(lambda x: x.split(' ', 2)[1])

def get_mod(x):
    try:
        return(x.split(' ', 2)[2])
    except:
        return('unknown') #if there is no more text then the model must be missing
cars['model'] = make_cleaned.map(get_mod)

#get a column from the body text
#positive = cars['body text'].str.find('lady').map(lambda x: 0 if x==-1 else 1)
pos_words = ['lady', 'off road', 'winter', 'lift', 'vintage']
neg_words = ['crack', 'torn', 'damage', 'leak', 'missing']

cars['pos_words'] = cars['body text'].map(lambda x: 1 if any(txt in x for txt in pos_words) else 0).astype(bool)
cars['neg_words'] = cars['body text'].map(lambda x: 1 if any(txt in x for txt in neg_words) else 0).astype(bool)
cars['low_text'] = cars['body text'].map(lambda x: 1 if len(x.split()) < 30 else 0).astype(bool) #text has less than 30 words

#replace blank space with 'unknown'
cars = cars.replace(' ', 'unknown')

#make the location column all lower case avoid separating the same place into different categories
cars['location'] = cars['location'].str.lower()

#convert the odometer reading to an integer to save space
cars['odometer'] = cars['odometer'].astype('int')

#drop extraneous columns
cars = cars.drop(['body text', 'latlong', 'make'], axis=1)

#output dat
cars.to_csv('cars_cleaned.csv', index=False)


