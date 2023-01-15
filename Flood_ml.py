import pandas as pd
import datetime
import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
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


#added to remove outliers
Flood=Flood[["Daily","StationID","Rainfall","Flood Event"]]
Flood["Flood Event"]=Flood["Flood Event"].astype(int)#converts to integer

#split the data to flood occured (flood1) and no Flood (flood0)
flood0=Flood[Flood["Flood Event"]==0]
flood1=Flood[Flood["Flood Event"]==1]

#further filter flood0 to only contain days where it rained
flood0_rain=flood0[flood0.Rainfall>0]

#Remove outliers shown in box plots (anything beyond upper bound of when it rained -flood0_rain) Upper bound=Q3*1.5
q75,q25=np.percentile(flood0_rain.Rainfall,[75,25])
iqr=q75-q25

upper_bound=q75+(1.5*iqr)

#convert all flood0_rain data wih rainfall>upper bound to null
flood0_rain.loc[flood0_rain.Rainfall>upper_bound,"Rainfall"]=np.nan
#check how many datapoints will be removed
flood0_rain.isnull().sum()  #747 data points will be removed

#remove the null (outliers)
flood0_rain=flood0_rain.dropna(axis=0)

ml_data=pd.concat([flood0_rain,flood1,flood0[flood0.Rainfall==0]])




df = ml_data[['StationID', 'Rainfall','Flood Event']]
max_rain=df.Rainfall.max()
min_rain=df.Rainfall.min()


#Preprocessing / Normalization
df.Rainfall= (df.Rainfall-df.Rainfall.min())/(df.Rainfall.max()-df.Rainfall.min())



#machine learning with random forest

X = df[['StationID', 'Rainfall']]
y = df['Flood Event']

#split data to test and train (80/20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

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
    Rainfall= (rainfall-min_rain)/(max_rain-min_rain)
    x=[stationID,Rainfall]
    X_test=np.array(x).reshape(1,-1)
    pred = clf.predict(X_test)
    
    #assume it will flood if rainfall>max of historical data
    if rainfall>Flood.Rainfall.max():
        pred=1
    
    return int(pred)


#to run ml for df (assume preshaped)
def ml_df(csv_station,csv_rainfall):
    csv_rainfall=(csv_rainfall-min_rain)/(max_rain-min_rain)
    x=pd.DataFrame({"station":csv_station,"rain":csv_rainfall})
    X_test=x.values
    pred = clf.predict(X_test)
    pred=pd.Series(pred)
    return pred



    