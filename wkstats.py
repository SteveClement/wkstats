import json
import os.path
import subprocess
import sys
import time
import urllib2

## Generated files ##

graphFile = "wk_progress.png"
resultFile = "result.txt"
apiKeyFile = "api_key.txt"
storedDataFile = "wkstats.dat"
plotDataFile = "wkstats_plot.tmp"


## Api Key related methods ##

def getApiKey():
    if os.path.isfile(apiKeyFile) is False:
        createApiFile(apiKeyFile)
        apiKeyNotFound(apiKeyFile)

    with open(apiKeyFile, "r") as f:
        for line in f:
            if line.startswith("#") or len(line.strip()) != 32:
                continue
            return line.strip()

    apiKeyNotFound(apiKeyFile)

def createApiFile(file):
    with open(file, "w") as f:
        f.write("# Please paste your WaniKani API key on the line below, you\n")
        f.write("# can find it on the account setings page on WaniKani.\n")

def apiKeyNotFound(file):
    print "API key not found. Please enter your WaniKani api key in the file " + file
    exit()


## WaniKani interaction ##

def processWaniKaniResponse(data):
    if "error" in data:
        print "WaniKani returned an error: " + data["error"]["message"]
        exit()

    ret = {}
    ret["date_saved"] = time.strftime("%Y-%m-%d")
    ret["level"] = data["user_information"]["level"]
    ret["requested_information"] = data["requested_information"]
    return ret

def readFromWaniKani():
    api_key = getApiKey()
    url = "https://www.wanikani.com/api/user/" + api_key + "/srs-distribution"
    j = json.loads(urllib2.urlopen(url).read())
    return processWaniKaniResponse(j)


## Data handling ##

def oneCell(new, old):
    if old == new:
        return "{:d}".format(new)
    else:
        return "{:d} ({:+d})".format(new, new - old)

def getLine(thisTime, lastTime, which):
    a = oneCell(thisTime["apprentice"][which], lastTime["apprentice"][which])
    g = oneCell(thisTime["guru"][which], lastTime["guru"][which])
    m = oneCell(thisTime["master"][which], lastTime["master"][which])
    e = oneCell(thisTime["enlighten"][which], lastTime["enlighten"][which])
    b = oneCell(thisTime["burned"][which], lastTime["burned"][which])
    return which.capitalize() + "|" + a +"|" + g + "|" + m + "|" + e + "|" + b

def getTableHeader(thisTime, lastTime):
    return "**Lvl " + oneCell(thisTime["level"], lastTime["level"]) + "**|**Apprentice**|**Guru**|**Master**|**Enlightened**|**Burned**"

def makeBold(line):
    def bold(word):
        return "**" + word + "**"

    return "|".join(map(bold, line.split("|")))

def getResult(thisTime, lastTime):
    key = "requested_information"
    ret = []
    ret.append(getTableHeader(thisTime, lastTime))
    ret.append("--|--:|--:|--:|--:|--:")
    ret.append(getLine(thisTime[key], lastTime[key], "radicals"))
    ret.append(getLine(thisTime[key], lastTime[key], "kanji"))
    ret.append(getLine(thisTime[key], lastTime[key], "vocabulary"))
    ret.append(makeBold(getLine(thisTime[key], lastTime[key], "total")))
    return ret;

def getBurnedCount(data, what):
    return data["requested_information"]["burned"][what]

def getTotalCount(data, what):
    return data["requested_information"]["apprentice"][what] + data["requested_information"]["guru"][what] + data["requested_information"]["master"][what] + data["requested_information"]["enlighten"][what] + getBurnedCount(data, what)


## File handling ##

def storeData(data):
    lines = []
    lastLine = None
    if os.path.isfile(storedDataFile) is not False:
        with open(storedDataFile, "r") as f:
            lines = f.readlines()
        lastLine = json.loads(lines[-1])

    with open(storedDataFile, "w") as f:
        if lastLine is not None and lastLine["date_saved"] == data["date_saved"]:
            f.writelines(lines[:-1])
        else:
            f.writelines(lines)

        json.dump(data, f, sort_keys = True)
        f.write("\n")
    print "Latest data saved to: " + storedDataFile

def getLastEntry():
    if os.path.isfile(storedDataFile) is False:
        return None

    with open(storedDataFile, "r") as f:
        for line in f:
            pass
        return json.loads(line)

# result is a list of lines to write to the file
def printResultToFile(result):
    with open(resultFile, "w") as f:
        output = "\n".join(result)
        f.write(output)
        print "Reddit table with latest data written to: " + resultFile

# returns true if plot data was successfully written to file
def writePlotData(thisTime):
    if os.path.isfile(storedDataFile) is False:
        print "Warning: No previously stored data found, unable to plot a graph."
        return False

    weeks = []
    with open(storedDataFile, "r") as f:
        weeks = f.readlines()

    if thisTime is not None:
        # thisTime is None if the result was stored to file
        weeks.append(thisTime)

    if len(weeks) == 1:
        print "Warning: Only one stored entry found, unable to plot a graph."
        return False

    with open(plotDataFile, "w") as f:
        for week in weeks:
            data = json.loads(week)
            rburn = getBurnedCount(data, "radicals")
            rtot = getTotalCount(data, "radicals")
            kburn = getBurnedCount(data, "kanji")
            ktot = getTotalCount(data, "kanji")
            vburn = getBurnedCount(data, "vocabulary")
            vtot = getTotalCount(data, "vocabulary")
            level = data["level"]

            f.write(data["date_saved"] + " " + str(rburn) + " " + str(rtot) + " " + str(kburn) + " " + str(ktot) + " " + str(vburn) + " " + str(vtot) + " " + str(level) + "\n")
    return True


## Graph plotting ##

def plotGraph():
    command = "gnuplot wkstats.p"
    subprocess.call(command.split())
    print "Graph of WaniKani progress written to: " + graphFile

def deletePlotData():
    os.remove(plotDataFile)

def makeGraph(thisTime):
    if writePlotData(thisTime) is True:
        plotGraph()
        deletePlotData()

## Main handling ##

def incorrectArguments(args):
    print "Incorrect usage: " + " ".join(args)
    print "Supported options:"
    print " --save: Saves the data read from WaniKani to file. If the last entry"
    print "         in the file is from today it will be replaced with the new"
    print "         data from WaniKani."


def wkstats():
    shouldSave = False
    if len(sys.argv) > 1 and sys.argv[1] == "--save":
        shouldSave = True
    elif len(sys.argv) > 1:
        incorrectArguments(sys.argv)
        exit()

    thisTime = readFromWaniKani()
    lastTime = getLastEntry()
    if lastTime is None:
        lastTime = thisTime

    thisTimeString = None
    if shouldSave:
        storeData(thisTime)
    else:
        thisTimeString = json.dumps(thisTime)

    result = getResult(thisTime, lastTime)
    printResultToFile(result)
    makeGraph(thisTimeString)


if __name__ == "__main__":
    wkstats();

''' Example response from WaniKani:
{
  "user_information": {
    "username": "nibarius",
    "gravatar": "4dff6dbd5d9ec926ffb5266be887526f",
    "level": 25,
    "title": "Turtles",
    "about": "",
    "website": null,
    "twitter": "",
    "topics_count": 9,
    "posts_count": 101,
    "creation_date": 1355330482,
    "vacation_date": null
  },
  "requested_information": {
    "apprentice": {
      "radicals": 8,
      "kanji": 36,
      "vocabulary": 56,
      "total": 100
    },
    "guru": {
      "radicals": 13,
      "kanji": 76,
      "vocabulary": 257,
      "total": 346
    },
    "master": {
      "radicals": 15,
      "kanji": 96,
      "vocabulary": 245,
      "total": 356
    },
    "enlighten": {
      "radicals": 56,
      "kanji": 220,
      "vocabulary": 552,
      "total": 828
    },
    "burned": {
      "radicals": 250,
      "kanji": 404,
      "vocabulary": 1272,
      "total": 1926
    }
  }
}
'''
