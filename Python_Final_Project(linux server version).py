import requests
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys

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

def accessRainfallAPI(apiKey, production, year, month, period="month"):
    url = "https://api.hcdp.ikewai.org/raster"
    header = {"Authorization": f"Bearer {apiKey}"}  

    period == "month":
        date = f"{year}-{monthsDict[month]}"
        paramsDict = {
            "datatype": "rainfall",
            "production": production,
            "period": period,
            "date": date,
            "extent": "statewide"
    }
        
    
    response = requests.get(url, headers=header, params=paramsDict)

    #this is to set make sure the API is valid
    assert response.status_code == 200, f"Error, your API key is not valid. Your HTTPS code is {response.status_code}!"
    
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

#this Dict is used in the API function for reformatting the month into the version necessary for the API 
monthsDict = {
    "january": "01", "february": "02", "march": "03", "april": "04", "may": "05",
    "june": "06", "july": "07", "august": "08", "september": "09", "october": "10",
    "november": "11", "december": "12"
}


#Usage Information and setting variables based on command line arguments.
if len(sys.argv) < 4:
    print("Usage: python program.py [apiKey] [month (in lowercase)] [save_path]")
    print("Example: python program.py yourApiKey january /path/to/save")
    sys.exit(1)

apiKey = sys.argv[1]
with open(apiKey, "r") as f:
    apiKey = f.read().strip()
    
month = sys.argv[2]
path = sys.argv[3]

#double checks that command line arguments are valid
assert os.path.exists(sys.argv[3]), f"The path {sys.argv[3]} does not exist. Please use an existing path"
assert month in monthsDict, f"The month provided: {month} is either not a real month, or not in the proper format. Please use a real month in lowercase."



#some variables to be used later
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
    
    legacyImg = accessRainfallAPI(apiKey, "legacy", year, month)
    newImg = accessRainfallAPI(apiKey, "new", year, month)
   
    difference = calculateDifference(newImg, legacyImg)
    differences.append(difference)
    
    basicDif = abs(newImg-legacyImg)
    sumDiffs += basicDif             #This section stores some variables for plots later on in the program.
    
    if maxDiff is None or difference  > maxDiff:
        maxDiff = difference
        yearMaxDiff = year
        maxOldImg = legacyImg   
        maxNewImg = newImg
        maxDiffImg = difference      #saves the images for later plotting. the images are based on which year has the largest difference    
        
print(f"The year with the largest difference is {yearMaxDiff} with a change of {maxDiff}.")


# Plotting the differences for each year ----------------------------------------------------------------------------------------------------------------------------

plt.plot(years, differences, linestyle='-', color='b', label='Line')
plt.title(f'Line graph of differences in precipitation for {month}')
plt.xlabel('Years 1990 through 2012')
plt.ylabel('Differences in precipitation')
plt.legend()
plt.savefig(os.path.join(path, "line_plot.png"))
plt.cla()
plt.clf()

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
plt.savefig(os.path.join(path, "4subplots.png"))
plt.cla()
plt.clf()













