import joblib
import pandas as pd
import numpy as np

model=joblib.load("./model/lgbm.joblib")

    
def create_df(date, hour, latitude, longitude, place, age, race, gender, precinct, borough):

    hour = int(hour) if int(hour) < 24 else 0
    day = date.day
    month = date.month
    year = date.year
    in_park = 1 if place == "In park" else 0
    in_public = 1 if place == "In public housing" else 0
    in_station = 1 if place == "In station" else 0
    boro = borough.upper()
    completed = 1
    ADDR_PCT_CD = float(precinct)
    age = int(age)

    columns = np.array(['year', 'month', 'day', 'hour', 'Latitude', 'Longitude','COMPLETED','ADDR_PCT_CD', 'IN_PARK', 'IN_PUBLIC_HOUSING',
                        'IN_STATION', 'BORO_NM_BRONX', 'BORO_NM_BROOKLYN', 'BORO_NM_MANHATTAN', 'BORO_NM_QUEENS',
                        'BORO_NM_STATEN ISLAND', 'BORO_NM_UNKNOWN', 'VIC_AGE_GROUP_18-24', 'VIC_AGE_GROUP_25-44',
                        'VIC_AGE_GROUP_45-64', 'VIC_AGE_GROUP_65+', 'VIC_AGE_GROUP_-18', 'VIC_AGE_GROUP_UNKNOWN',
                        'VIC_RACE_AMERICAN INDIAN/ALASKAN NATIVE', 'VIC_RACE_ASIAN / PACIFIC ISLANDER', 'VIC_RACE_BLACK',
                        'VIC_RACE_BLACK HISPANIC', 'VIC_RACE_OTHER', 'VIC_RACE_UNKNOWN', 'VIC_RACE_WHITE',
                        'VIC_RACE_WHITE HISPANIC', 'VIC_SEX_D', 'VIC_SEX_E', 'VIC_SEX_F', 'VIC_SEX_M', 'VIC_SEX_U'])

    data = [[year, month, day, hour, latitude, longitude,completed,ADDR_PCT_CD, in_park, in_public, in_station,
             1 if boro == "BRONX" else 0, 1 if boro == "BROOKLYN" else 0, 1 if boro == "MANHATTAN" else 0,
             1 if boro == "QUEENS" else 0, 1 if boro == "STATEN ISLAND" else 0, 1 if boro not in (
             "BRONX", "BROOKLYN", "MANHATTAN", "QUEENS", "STATEN ISLAND") else 0,  # Assuming "year" is a parameter
             1 if age in range(18, 25) else 0, 1 if age in range(25, 45) else 0, 1 if age in range(45, 65) else 0,
             1 if age >= 65 else 0, 1 if age < 18 else 0, 0,
             1 if race == "AMERICAN INDIAN/ALASKAN NATIVE" else 0, 1 if race == "ASIAN / PACIFIC ISLANDER" else 0,
             1 if race == "BLACK" else 0, 1 if race == "BLACK HISPANIC" else 0, 1 if race == "OTHER" else 0,
             1 if race == "UNKNOWN" else 0, 1 if race == "WHITE" else 0, 1 if race == "WHITE HISPANIC" else 0,
             0, 0, 1 if gender == "Female" else 0, 1 if gender == "Male" else 0, 0]]

    df = pd.DataFrame(data, columns=columns)
    return df.values

def predict(data):
   pred = model.predict(data)[0]
   if pred==0:
      return 'DRUGS/ALCOHOL',['DANGEROUS DRUGS', 'INTOXICATED & IMPAIRED DRIVING',
             'ALCOHOLIC BEVERAGE CONTROL LAW', 'INTOXICATED/IMPAIRED DRIVING',
             'UNDER THE INFLUENCE OF DRUGS', 'LOITERING FOR DRUG PURPOSES']
   if (pred == 2):
      return 'PROPERTY',['BURGLARY', 'PETIT LARCENY', 'GRAND LARCENY', 'ROBBERY', 'THEFT-FRAUD', 
        'GRAND LARCENY OF MOTOR VEHICLE', 'FORGERY', 'JOSTLING', 'ARSON',
        'PETIT LARCENY OF MOTOR VEHICLE', 'OTHER OFFENSES RELATED TO THEF',
        "BURGLAR'S TOOLS", 'FRAUDS', 'POSSESSION OF STOLEN PROPERTY',
        'CRIMINAL MISCHIEF & RELATED OF', 'OFFENSES INVOLVING FRAUD',
        'FRAUDULENT ACCOSTING', 'THEFT OF SERVICES']
   elif pred==1:
      return 'PERSONAL',['ASSAULT 3 & RELATED OFFENSES', 'FELONY ASSAULT',
            'OFFENSES AGAINST THE PERSON', 'HOMICIDE-NEGLIGENT,UNCLASSIFIE',
            'HOMICIDE-NEGLIGENT-VEHICLE', 'KIDNAPPING & RELATED OFFENSES',
            'ENDAN WELFARE INCOMP', 'OFFENSES RELATED TO CHILDREN',
            'CHILD ABANDONMENT/NON SUPPORT', 'KIDNAPPING', 'DANGEROUS WEAPONS',
            'UNLAWFUL POSS. WEAP. ON SCHOOL']
   else:
      return 'SEXUAL',['SEX CRIMES', 'HARRASSMENT 2', 'RAPE', 'PROSTITUTION & RELATED OFFENSES',
          'FELONY SEX CRIMES', 'LOITERING/DEVIATE SEX']
