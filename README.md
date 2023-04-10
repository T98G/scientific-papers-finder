# scholar-crawler

This Script performes a refined search on google scholar for a query provided by the user

This script depends on the following packages :

*selenium
*scholarly
*tqdm
*re
*requests
*bs4
*argparse
*it also depends on Google Chrome web browser

This script takes the following command line arguments:

-q "A string with the phrase the user wants to search for, it must be delimited by quote marks"
-kw "key words to filter the search, they must be separated by spaces and delimited by quote marks"
-n "The maximum number of publications in the google scholar results to search through"
-p "the time in years to refine the search, it must be written as year-year delimited by quote marks" (optional)
-d "the website domains to take results from" (optional) #but really useful
-o "the output file name to store the url for the filtered urls"

This script can be run by the following command as an example

python3 crawler.py -q "query" -kw "keywords" -n 1 -p "2010-2022" -c 2  -d "acs nature science direct rcs mdpi" -o test.csv

# Please note:

** Google restricts the number of requests from automatized scripts to 50000 per day, which is not much
** So the user might want the limit the number of maximum publications to search for /
** as 1 publication correspond to multiple requests

# Do NOT close the Chrome windows opened by the script while it's running or it will crash


## Have Fun !

