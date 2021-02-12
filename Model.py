# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 11:42:38 2021

@author: a_sylvester
"""

import pandas as pd
from sklearn.model_selection import train_test_split

data = pd.read_csv('cars_cleaned.csv')

#### missing values #####
data.dropna(inplace=True)#there are only a few dozen missing values so drop those rows

#### create training and validation data ####
y = data.pop('price')
X = data

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.33, random_state=42)

#### pipeline ###
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

numeric_cols = [#'odometer', 
                'age'
                ]
categorical_cols = [
#    'condition', 
#    'drive', 
#    'fuel', 
#    'location', 
#    'paint color',
#    'sale type', 
#    'title status', 
#    'transmission', 
#    'type',
#    'cylinders', 
#    'size', 
#    'latitude', 
#    'longitude', 
#    'location_simple', 
#    'make_', 
#    'model', 
#    'pos_words', 
#    'neg_words', 
#    'low_text', 
   'model0',
#    'model1', 
#    'model2'
    ]

# Preprocessing for categorical data
categorical_transformer = Pipeline(steps=[
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# Bundle preprocessing for numerical and categorical data
preprocessor = ColumnTransformer(
    transformers=[
        ('num', 'passthrough', numeric_cols),
        ('cat', categorical_transformer, categorical_cols)
    ])

from sklearn.linear_model import LinearRegression
from lightgbm import LGBMRegressor
model = LGBMRegressor()
#model = LinearRegression()

from sklearn.metrics import mean_absolute_error

# Bundle preprocessing and modeling code in a pipeline
my_pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                              ('model', model)
                             ])

# Preprocessing of training data, fit model 
my_pipeline.fit(X_train, y_train)

# Preprocessing of validation data, get predictions
preds = my_pipeline.predict(X_test)

# Evaluate the model
score = mean_absolute_error(y_test, preds)
print('MAE:', score)