
################################################################################
# Geocode data using Google and GeoNames
# Benjamin P. Stewart, May, 2013
# Purpose: Geocoding is something we need to do frequently, so this script will do that.
#   It leverages GeoNames (http://www.geonames.org/) primarily, and then tries to use
#   Google if GeoNames does not use. The reason for this is the request limit for Google
####  Corrected for Python 3, Hamza Haloui, May 2017
################################################################################

import urllib, xlrd, unicodedata, time, json

###USER Variables
inputExcelDocument = r"C:\Users\WB512163\Documents\test.xls"
outputDoc = open(r"C:\Users\WB512163\Documents\test_geocoded.tsv", 'w')
#Define the columns in the inputExcelDocument that describe the place to geocode.
#   The values will be separated by a comma to create a single string
locColumns = [0,0]
sheetIdx = 0 #Zer0-Based!!! If the data is not on the first sheet, you can change it here

#This bit makes the function emulate a firefox request...I really don't know if it is necessary
userAgent = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 GTB7.1 (.NET CLR 3.5.30729)" 
headers = { 'User-Agent' : userAgent }
values = { 's' : 'nothing' }
data = urllib.parse.urlencode(values).encode('utf8')

#Open the excel input dictionary, get the first sheet
dataDict = xlrd.open_workbook(inputExcelDocument)
projects = dataDict.sheet_by_index(sheetIdx)   
outputDoc.write("OBJECTID\tPostal\tLat\tLng\n")
print("There are %s projects to geocode" % projects.nrows)

#Wrapper for the geo location tools 
def geoCode(self, data, headers):
    geogLoc = getGeogLocation(self.rawLocation, data, headers)
    return(geogLoc)

def getJSONresponse(url, data, headers):
    urlReq = urllib.request.Request(url, data, headers)
    req = urllib.request.urlopen(urlReq)
    return(json.loads(req.read()))    

# This is where the geolocation action actually happens
def getGeogLocation (location, data, headers):
    location2 = urllib.parse.quote(location) # get the internet version of the location string
    #Perform the geonames.org geolocation    
    geoNamesUrl = "http://api.geonames.org/searchJSON?q=" + location2 + "&maxRows=3&username=petie_stewart&featureClass=P"    
    jsonResponse = getJSONresponse(geoNamesUrl, data, headers)
    ret = dict(lat=-999, lng=-999)
    # If the geonames result has a length
    geoCodeSource = "nothing"
    if (jsonResponse['totalResultsCount'] > 0):
        res = jsonResponse['geonames'][0]
        ret = dict(lat=res['lat'], lng=res['lng'])
        geoCodeSource = "geonames"
    else:
        googleUrl = "http://maps.googleapis.com/maps/api/geocode/json?address=" + location2 + "&sensor=false"
        jsonResponse = getJSONresponse(googleUrl, data, headers)
        if (jsonResponse['status'] == "OK"):
            res = jsonResponse['results'][0]['geometry']['location']
            ret = dict(lat=res['lat'], lng=res['lng'])
            geoCodeSource = "google"
        else:
            print(location + " was not found")
    return({'location':ret, 'source':geoCodeSource})


class projectLocation:
    def __init__(self, curProject, columns):         
        try:
            locString = ",".join([str(curProject[k]) for k in columns])        
            self.rawLocation = locString #unicodedata.normalize('NFKD', locString)
        except:
            self.source = "StringError"
            self.geogLoc = dict(lat=-999, lng=-999)
            self.rawLocation = ''
        geogCodeResult = geoCode(self, data, headers)
        self.geogLoc = geogCodeResult['location']        
        self.source = geogCodeResult['source']


googleCnt = 0
geoNames = 0
missed = 0

for rownum in range(1, projects.nrows):
    curProject = projects.row_values(rownum)    
    if rownum < 5:
        print(curProject)
    projLocation = projectLocation(curProject, locColumns)
    if projLocation.source == "StringError":
        print("Error with row %s" % rownum)
        print(curProject)
    geoNames = (geoNames + 1 if projLocation.source == "geonames" else geoNames)
    googleCnt = (googleCnt + 1 if projLocation.source == "google" else googleCnt)
    missed = (missed + 1 if projLocation.source == "nothing" else missed)
    outputDoc.write("%s\t%s\t%s\t%s\t%s\n" % (rownum, projLocation.rawLocation, projLocation.geogLoc['lat'], projLocation.geogLoc['lng'], projLocation.source))
    time.sleep(1)        

outputDoc.close()
print("Of %s projects, %s were found in GeoNames, %s were found in Google, %s were not found" %(projects.nrows, geoNames, googleCnt, missed))
