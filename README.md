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

###### Some examples for sql queries to get data:

```ssh
SELECT A.* FROM `MatchesGoals` A WHERE `id_fixture` IN ( SELECT B._id FROM MatchesFixtures B Where team_season_away_name = 'Liverpool' and team_season_home_name = 'Chelsea') GROUP BY id_fixture

SELECT A.* FROM `MatchesGoals` A WHERE `id_fixture` IN ( SELECT B._id FROM MatchesFixtures B Where (team_season_away_name = 'Liverpool' and team_season_home_name = 'Chelsea') or (team_season_away_name = 'Chelsea' and team_season_home_name = 'Liverpool'))

SELECT A.* FROM `MatchesGoals` A WHERE `id_fixture` IN ( SELECT B._id FROM MatchesFixtures B Where ((team_season_away_name = 'Liverpool' and team_season_home_name = 'Chelsea') or (team_season_away_name = 'Chelsea' and team_season_home_name = 'Liverpool')) or (goal_type_code = 'ng' or goal_type_code = 'og' or goal_type_code = 'p'))

SELECT A.* FROM `MatchesGoals` A WHERE `id_fixture` IN ( SELECT B._id FROM MatchesFixtures B Where ((team_season_away_name = 'Liverpool' and team_season_home_name = 'Chelsea') or (team_season_away_name = 'Chelsea' and team_season_home_name = 'Liverpool')) and (A.goal_type_code = 'ng' or A.goal_type_code = 'og' or A.goal_type_code = 'p')) ORDER BY `A`.`elapsed` ASC

SELECT COUNT(B._id) FROM MatchesFixtures B Where (team_season_away_name = 'Chelsea' or team_season_home_name = 'Chelsea') and (team_season_home_name = 'Liverpool' or team_season_away_name = 'Liverpool')

1)
SELECT COUNT(B._id) FROM MatchesFixtures B Where (team_season_home_name = '{}' and team_season_away_name = '{}')
2)
SELECT COUNT(A._id) FROM `MatchesGoals` A WHERE `id_fixture` IN ( SELECT B._id FROM MatchesFixtures B Where B.team_season_home_name = '{}' and B.team_season_away_name = '{}') and (A.goal_type_code = 'ng' or A.goal_type_code = 'og' or A.goal_type_code = 'p')) ORDER BY `A`.`id_fixture` ASC
```
