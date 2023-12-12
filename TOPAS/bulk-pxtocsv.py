from datetime import datetime, timedelta
from pypxlib import Table
import csv
import glob
import pandas as pd
import os


def split_by_month(df, location):
    """ Splits the DF data by month.

        Parameters:
        -----------
        df : pandas dataframe
        location : string
            string that represents the location of station

        Output:
        -------
        year-month-location.csv in it's respective yearly folder
    
    """
    for year in set(df['TimeStamp'].dt.year):
        for month in range(1,13,1):
            data = df[(df['TimeStamp'].dt.year == year) & (df['TimeStamp'].dt.month == month)]
            if(df.empty != True):
                if not os.path.exists('export/' + str(year)):  
                    os.mkdir('export/' + str(year))  
                data.to_csv(f"export/{str(year)+'/'+location+'-'+str(year)+'-'+str(month)}.csv", index=False, mode= 'a', header=True)


def setup():
    """ Initialize the script checking for basic "export" folder and selecting proper
        location of TOPAS

        Returns
        -------
        location : string
            string that represents the location of station
    """

    if not os.path.exists('export'):
        os.makedirs('export')
    

    f = open(os.getcwd() + '/TOPAS/pxtocsv/locations', "r")
    lines = f.readlines()
    for (i, item) in enumerate(lines, 1):
        print(str(i) + '-', item, end="")
    try:
        location = lines[int(input("Index of location: "))-1]
    except IndexError:
        print("Index out of range, defaulting to NN")
        location = "NN"

    print("Location selected: " + location)
    
    return  location.strip('\n')

def readPX(location):
    """ Reads px database and generates a CSV file based on px data.
           
        Parameters
        ----------
        location : string
            string that represents the location of station

        Output
        ------
        location-TOPAS.csv with all the pxdb data
    """

    print("Reading Series folder... ", end = "")
    samples = glob.glob('./Series/*.DB')

    file = open(location + '-TOPAS' + '.csv', 'w')

    writer = csv.writer(file)

    # read all .db files on samples folder and write content to samples.csv
    for name in samples:
        pxData = Table(name)
        for row in pxData:
            data= [row['TimeStamp'].strftime("%m/%d/%Y, %H:%M:%S"), row['Total Particles'], row['PM10 particles'], row['PM2.5 particles'],row['PM1 particles']]
            if(data != ['01/01/1900, 00:00:00','####0.0','####0.0','###0.00','###0.00'] and data != ['12/31/1899, 00:00:00','ug/m^3','ug/m^3','ug/m^3','ug/m^3']):
                writer.writerow(data)
        pxData.close()  #closes the px .DB file
    file.close()    #closes the csv file

    print("Done")

def sort_data(location,df):
    """ Sorts the data by timestamp. It also exports and creates yearly folders for the data. 

        Parameters
        ----------
        df : pandas dataframe with raw TOPAS data 
        location: string of location
    """
    print("Sorting and deleting duplicates... ", end="")
    df['Total Particles'] = df['Total Particles'].apply(lambda x: str(x).replace(',','.'))
    df['PM10 particles'] = df['PM10 particles'].apply(lambda x: str(x).replace(',','.'))
    df['PM2.5 particles'] = df['PM2.5 particles'].apply(lambda x: str(x).replace(',','.'))
    df['PM1 particles'] = df['PM1 particles'].apply(lambda x: str(x).replace(',','.'))

    
    df = df.sort_values(by="TimeStamp")
    print(df)
    #Not needed for now.
    df.to_csv('samples_sorted.csv', index=False) 

    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'])

    split_by_month(df,location)
    print("Done")

def readCSV(location):
    """ Read raw exported CSV, drop the duplicates and add header

        Returns
        -------
        df : pandas dataframe
            dataframe with CSV data
    """
    df = pd.read_csv(location + '-TOPAS' + '.csv', names=["TimeStamp", "Total Particles", "PM10 particles", "PM2.5 particles", "PM1 particles"])
    df = df.drop_duplicates()
    print(df)
    return df

location = setup()
readPX(location)
sort_data(location, readCSV(location))