# Football Matches Database

## Scraping

1.- http://www.resultados-futbol.com/

2.- http://api.sportdeer.com/


# First Script :
Download all the files install the requierd modules start the Main.py file.
###### Requierd modules:
```ssh
$ pip install beautifulsoup4
$ pip install requests
```
###### Run the script:
```ssh
$ cd /download-folder
$ python Main.py
```

# Second Script :
Get the data from sportdeer.com website with a spider that work on API token and but all the data in mysql Database, you need to update your mysql server connection details in the config.ini file. (example mysql database in file : EPL-Database.sql)
###### Requierd modules:
```ssh
$ pip install requests
$ pip install configparser
$ pip install logging
```
###### Run the script:
```ssh
$ cd /download-folder
$ python SportDeerSpider.py
```
