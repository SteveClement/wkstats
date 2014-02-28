wkstats
=======

A script that generates [WaniKani](https://www.wanikani.com) statistics for the [Total Annihilation Challenge](http://www.reddit.com/r/totalanguage/) on [Reddit](http://www.reddit.com/)

[gnuplot](http://www.gnuplot.info/) has to be installed and available in the path to run this script. Before you can use the script the api key for WaniKani has to be placed in a file called api_key.txt in the same directory as the script.

How to use the script:

$ python wkstats.py

Downloads the current data from WaniKani and prints a Reddit formatted table with the data from WaniKani. If previous data is available locally (see --save option) the table will include changes from the last time. If there are at least one earlier data point saved a graph will also be plotted that shows the progress over time.

$ python wkstats.py --save

Does the same as when run without the --save option, but it also saves the data from WaniKani to file. If there is already data saved for the same day the old data will be overwritten.
