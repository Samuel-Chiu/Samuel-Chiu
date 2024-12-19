import requests
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

#Def Section; Function 1---------------------------------------------------------------------------------------------------------------------------------------------
'''
The purpose of this function is to access the API and return the tiff file from it. 

inputs:
    production: the type of data production ("new" or "legacy")
    year: the year of data collection, from 1990 to 2012
    month: the month of the year (any month spelled out is good, all in lowercase)
    period: the period of data collection, default is month. can be set to all.

returns:
    this returns the image from the API in the form of a numpy array, with a mask applied to remove negative numbers.
'''

def accessRainfallAPI(production, year, month, period="month"):
    with open("apiKey.txt", "r") as f:  
        apiKey = f.read().strip()

    url = "https://api.hcdp.ikewai.org/raster"
    header = {"Authorization": f"Bearer {apiKey}"}  

    if period == "month":

    
        monthsDict = {"january": "01", "february": "02", "march": "03", "april": "04", "may": "05",
                      "june": "06", "july": "07", "august": "08", "september": "09", "october": "10",
                      "november": "11", "december": "12"}

        date = f"{year}-{monthsDict[month]}"

        paramsDict = {
            "datatype": "rainfall",
            "production": production,
            "period": period,
            "date": date,
            "extent": "statewide"
        }
        
    elif period == "year":

        date = year

        paramsDict = {
            "datatype": "rainfall",
            "production": production,
            "date": date,
            "extent": "statewide"
            }
    
    response = requests.get(url, headers=header, params=paramsDict)
    
    with open("tempFile.tiff", "wb") as f:
        f.write(response.content)
    
    with rasterio.open("tempFile.tiff", "r") as src:
        img = src.read()

    img[img < 0] = 0

    return img

#Function 2
'''
This takes two images of the same size and calculates the difference in arrays.

inputs:
    image 1, and image 2 (both in the form of arrays)

returns:
    the difference in arrays according to the formula provided in the assignment
'''

def calculateDifference(img1, img2):
    
    numerator = np.sum((img1 - img2) ** 2)
    denominator = np.sum(img1)
    
    difference = np.sqrt(numerator) / denominator 

    return difference


#Main code Section --------------------------------------------------------------------------------------------------------------------------------------------------

maxDiff = None
yearMaxDiff = None
maxOldImg = None
maxNewImg = None
maxDiffImg = None

sumDiffs = 0

differences = []
basicDifferences = []


years = list(range(1990, 2013))
for year in years:
    
    legacyImg = accessRainfallAPI("legacy", year, "january")
    newImg = accessRainfallAPI("new", year, "january")
   
    difference = calculateDifference(newImg, legacyImg)
    differences.append(difference)
    
    basicDif = abs(newImg-legacyImg)
    sumDiffs += basicDif
    
    if maxDiff is None or difference  > maxDiff:
        maxDiff = difference
        yearMaxDiff = year
        maxOldImg = legacyImg
        maxNewImg = newImg
        maxDiffImg = difference
        
print(f"The year with the largest difference is {yearMaxDiff} with a change of {maxDiff}.")


# Plotting the differences for each year ----------------------------------------------------------------------------------------------------------------------------

plt.plot(years, differences, marker='o', linestyle='-', color='b', label='Line')

plt.title('Basic Line Graph')
plt.xlabel('Years 1990 throuhgh 2012')
plt.ylabel('Differences in precipitation')

plt.legend()

plt.show()

# Plotting the 4 plots ---------------------------------------------------------------------------------------------------------------------------------------------------

basicDiffImg = abs(maxNewImg - maxOldImg)

differencesOverTimeImg = sumDiffs / 22

(fig, axes) = plt.subplots(2, 2)

axes[0, 0].imshow(maxOldImg[0], cmap='Blues')
axes[0, 0].set_title("Legacy Image (Max Diff Year)")

axes[0, 1].imshow(maxNewImg[0], cmap='Blues')
axes[0, 1].set_title("New Image (Max Diff Year)")

axes[1, 0].imshow(basicDiffImg[0], cmap='Blues')
axes[1, 0].set_title("Basic Difference (Max Diff Year)")

axes[1, 1].imshow(differencesOverTimeImg[0], cmap='Blues')
axes[1, 1].set_title("Mean Differences Over Time")

plt.tight_layout()
plt.show()












