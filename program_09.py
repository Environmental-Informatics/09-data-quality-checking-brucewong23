#!/bin/env python
# Shizhang Wang
# 4/19/2020
# the following script will perform a data quality check including 'No Data',
# 'Gross Error', 'Min Max Swap' and 'Range Check' for provided filename, then plot
# the original and modified data for comparison
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def ReadData( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    raw data read from that file in a Pandas DataFrame.  The DataFrame index
    should be the year, month and day of the observation.  DataFrame headers
    should be "Date", "Precip", "Max Temp", "Min Temp", "Wind Speed". Function
    returns the completed DataFrame, and a dictionary designed to contain all 
    missing value counts."""
    
    # define column names
    colNames = ['Date','Precip','Max Temp', 'Min Temp','Wind Speed']

    # open and read the file
    DataDF = pd.read_csv("DataQualityChecking.txt",header=None, names=colNames,  
                         delimiter=r"\s+",parse_dates=[0])
    DataDF = DataDF.set_index('Date')
    
    # define and initialize the missing data dictionary
    ReplacedValuesDF = pd.DataFrame(0, index=["1. No Data"], columns=colNames[1:])
     
    return( DataDF, ReplacedValuesDF )
 
def Check01_RemoveNoDataValues( DataDF, ReplacedValuesDF ):
    """This check replaces the defined No Data value with the NumPy NaN value
    so that further analysis does not use the No Data values.  Function returns
    the modified DataFrame and a count of No Data values replaced."""

    # add your code here
    DataDF.replace(-999, np.nan, inplace=True) # replace value of -999 with NaN
    ReplacedValuesDF.loc['1. No Data'] = DataDF.isna().sum()
    # count NaN in a column, https://stackoverflow.com/questions/26266362/how-to-count-the-nan-values-in-a-column-in-pandas-dataframe
    return( DataDF, ReplacedValuesDF )
    
def Check02_GrossErrors( DataDF, ReplacedValuesDF ):
    """This function checks for gross errors, values well outside the expected 
    range, and removes them from the dataset.  The function returns modified 
    DataFrames with data the has passed, and counts of data that have not 
    passed the check."""
 
    # add your code here
    # filter values outside specified range, https://stackoverflow.com/questions/38802675/create-bool-mask-from-filter-results-in-pandas
    DataDF['Precip'].mask((DataDF['Precip'] < 0) | (DataDF['Precip'] > 25), 
          np.nan, inplace=True)
    DataDF['Max Temp'].mask((DataDF['Max Temp'] < -25) | (DataDF['Max Temp'] > 35), 
          np.nan, inplace=True)
    DataDF['Min Temp'].mask((DataDF['Min Temp'] < -25) | (DataDF['Min Temp'] > 35), 
          np.nan, inplace=True)
    DataDF['Wind Speed'].mask((DataDF['Wind Speed'] < 0) | (DataDF['Wind Speed'] > 10), 
          np.nan, inplace=True)
    ReplacedValuesDF.loc['2. Gross Error'] = (DataDF.isna().sum() - 
                        ReplacedValuesDF.loc['1. No Data'])
    # accumulated replacement is all the NaN value mins what gather in step 1
    return( DataDF, ReplacedValuesDF )
    
def Check03_TmaxTminSwapped( DataDF, ReplacedValuesDF ):
    """This function checks for days when maximum air temperture is less than
    minimum air temperature, and swaps the values when found.  The function 
    returns modified DataFrames with data that has been fixed, and with counts 
    of how many times the fix has been applied."""
    
    # add your code here
    
    idx = DataDF['Max Temp'] < DataDF['Min Temp'] # index where max temp is lower than min temp
    total = sum(idx)
    DataDF.loc[idx, ['Max Temp', 'Min Temp']] = DataDF.loc[idx, ['Min Temp', 'Max Temp']].values
    # swapping values based on condition created index
    ReplacedValuesDF.loc['3. Swapped'] = (0, total, total, 0)
    # total swap assigned manually since only counts needed, a more elaborate way is perhaps making a copy before swapping and 
    # check if values are changed
    return( DataDF, ReplacedValuesDF )
    
def Check04_TmaxTminRange( DataDF, ReplacedValuesDF ):
    """This function checks for days when maximum air temperture minus 
    minimum air temperature exceeds a maximum range, and replaces both values 
    with NaNs when found.  The function returns modified DataFrames with data 
    that has been checked, and with counts of how many days of data have been 
    removed through the process."""
    
    # add your code here
    idx = (DataDF['Max Temp']-DataDF['Min Temp']) > 25 # create bool mask for range > 25
#    total = sum(idx) # could be used to manually assign counts
#    print('idx sum:', total)
    DataDF.loc[idx, ['Max Temp', 'Min Temp']] = np.nan # NaN assigned to cell according to index
    ReplacedValuesDF.loc['4. Range Fail'] = (DataDF.isna().sum() - ReplacedValuesDF[0:2].sum())
    # NaN is count is the first two steps (0:2), otherwise, total can be used again as in step 3
    return( DataDF, ReplacedValuesDF )

# the following condition checks whether we are running as a script, in which 
# case run the test code, otherwise functions are being imported so do not.
# put the main routines from your code after this conditional check.

if __name__ == '__main__':

    fileName = "DataQualityChecking.txt"
    DataDF, ReplacedValuesDF = ReadData(fileName)
    
    print("\nRaw data.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check01_RemoveNoDataValues( DataDF, ReplacedValuesDF )
    
    print("\nMissing values removed.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check02_GrossErrors( DataDF, ReplacedValuesDF )
    
    print("\nCheck for gross errors complete.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check03_TmaxTminSwapped( DataDF, ReplacedValuesDF )
    
    print("\nCheck for swapped temperatures complete.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check04_TmaxTminRange( DataDF, ReplacedValuesDF )
    
    print("\nAll processing finished.....\n", DataDF.describe())
    print("\nFinal changed values counts.....\n", ReplacedValuesDF)
    
    # original data
    colNames = ['Date','Precip','Max Temp', 'Min Temp','Wind Speed']
    DataDF_original = pd.read_csv("DataQualityChecking.txt",header=None, names=colNames,  
                         delimiter=r"\s+",parse_dates=[0])
    DataDF_original = DataDF_original.set_index('Date')
    # plot and save files
    # precipitation
    plt.figure(0)
    plt.plot(DataDF_original.index, DataDF_original['Precip'], label='Original', linewidth=0.8)
    plt.plot(DataDF.index, DataDF['Precip'], color='red', label='Modified', linewidth=0.8)
    plt.xticks(rotation=45)
    plt.xlabel('Date')
    plt.ylabel('Precipitation (mm)')
    plt.title('Precipitation before & after Correction')
    plt.legend()
    plt.savefig('Precip.png', dpi=300, bbox_inches='tight')
    
    # Max temp
    plt.figure(1)
    plt.plot(DataDF_original.index, DataDF_original['Max Temp'], label='Original', linewidth=0.8)
    plt.plot(DataDF.index, DataDF['Max Temp'], color='red', label='Modified', linewidth=0.8)
    plt.xticks(rotation=45)
    plt.xlabel('Date')
    plt.ylabel('Max Temp (C)')
    plt.title('Max Temperature before & after Correction')
    plt.legend()
    plt.savefig('Max_Temp.png', dpi=300, bbox_inches='tight')
    
    # min temp
    plt.figure(2)
    plt.plot(DataDF_original.index, DataDF_original['Min Temp'], label='Original', linewidth=0.8)
    plt.plot(DataDF.index, DataDF['Min Temp'], color='red', label='Modified', linewidth=0.8)
    plt.xticks(rotation=45)
    plt.xlabel('Date')
    plt.ylabel('Min Temp (C)')
    plt.title('Min Temperature before & after Correction')
    plt.legend()
    plt.savefig('Min_Temp.png', dpi=300, bbox_inches='tight')
    
    # wind speed
    plt.figure(3)
    plt.plot(DataDF_original.index, DataDF_original['Wind Speed'], label='Original', linewidth=0.8)
    plt.plot(DataDF.index, DataDF['Wind Speed'], color='red', label='Modified', linewidth=0.8)
    plt.xticks(rotation=45)
    plt.xlabel('Date')
    plt.ylabel('Wind Speed (m/s)')
    plt.title('Wind Speed before & after Correction')
    plt.legend()
    plt.savefig('Wind_Speed.png', dpi=300, bbox_inches='tight')
    
    plt.close('all') # close all figures
    # write modified data to file as original format
    DataDF.to_csv('modified_data.txt', sep=' ', header=None)
    
    # output failed checks to tab delimited file
    ReplacedValuesDF.to_csv('failed_checks.txt', sep='\t')