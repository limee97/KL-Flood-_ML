import pandas as pd
import datetime
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import warnings
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
#warnings.filterwarnings("ignore")
from geopy.distance import great_circle

#set working directory:
#import os
#os.chdir("C:/Users/Lim Ee/OneDrive/Desktop/WQD7003/Project/Final")

df1 =pd.read_csv('3114005.csv')
df2 =pd.read_csv('3114113.csv')
df3 =pd.read_csv('3114114.csv')
df4 =pd.read_csv('3116003.csv')
df5 =pd.read_csv('3116006.csv')
df6 =pd.read_csv('3117006.csv')
df7 =pd.read_csv('3117070.csv')
df8 =pd.read_csv('3216007.csv')

## Drop the NA values in the daily rows since it does not bring any meaning if it is NA in that column
df1=df1.dropna(subset=['Daily'])
df2=df2.dropna(subset=['Daily'])
df3=df3.dropna(subset=['Daily'])
df4=df4.dropna(subset=['Daily'])
df5=df5.dropna(subset=['Daily'])
df6=df6.dropna(subset=['Daily'])
df7=df7.dropna(subset=['Daily'])
df8=df8.dropna(subset=['Daily'])

#add station ID Column
df1.insert(1,"StationID","3114005",True)
df2.insert(1,"StationID","3114113",True)
df3.insert(1,"StationID","3114114",True)
df4.insert(1,"StationID","3116003",True)
df5.insert(1,"StationID","3116006",True)
df6.insert(1,"StationID","3117006",True)
df7.insert(1,"StationID","3117070",True)
df8.insert(1,"StationID","3216007",True)

##Combine the file into one dataframe
Flood = pd.concat([df1, df2,df3,df4,df5,df6,df7,df8], axis=0)

#remove redundant column
del Flood["Unnamed: 3" ]

## change Daily to datetime so we are able to slice the date, convert name to df
Flood['Daily'] =  pd.to_datetime(Flood['Daily'])
df = Flood[['StationID', 'Rainfall','Flood Event']]


#Preprocessing / Normalization
df['Rainfall']= (df['Rainfall']-min(df['Rainfall']))/(max(df['Rainfall']-min(df['Rainfall'])))



#machine learning with random forest

X = df[['StationID', 'Rainfall']]
y = df['Flood Event']

#split data to test and train (80/20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=999)

# Model Train
clf = RandomForestClassifier()
clf.fit(X_train,y_train)

# Testing Model
pred = clf.predict(X_test)







#functions to be used for streamlit app

#setup
df_coord=pd.read_csv("station_coord.csv")
df_coord["lat_long"] = list(zip(df_coord["lat"], df_coord["long"]))
df_coord['diff']=[0,0,0,0,0,0,0,0]

# for identifying the right station id for ml based on user input
def dist(coord):
    df_coord['diff'] = df_coord['lat_long'].apply(lambda x: great_circle(coord, x).km)
    difference=df_coord["diff"]
    min=difference.min()
    return int(df_coord.Station_ID[df_coord["diff"]==min])

#to run ml
def ml(stationID,rainfall):
    x=[stationID,rainfall]
    X_test=np.array(x).reshape(1,-1)
    pred = clf.predict(X_test)
    
    #assume it will flood if rainfall>max of historical data
    if rainfall>Flood.Rainfall.max():
        pred=1
    
    return int(pred)


#to run ml for df (assume preshaped)
def ml_df(x):
    pred = clf.predict(x)
    pred=pd.Series(pred)
    return pred



    
