# -*- coding: utf-8 -*-
import time
import datetime
import logging
import sys
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
#from twisted.conch.insults.window import cursor
import Const
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config



CheckMatchEndInterval = 300

RetryInterval = 10
SpiderTimeOut = 24 * 3600
PageLoadTimeOut = 90

refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI1YWY0YTdlY2VkZWM5OTNhOWNhZjNjOGQiLCJpYXQiOjE1MjU5ODMyNjR9.7jOCYGQsc6E0DVfbepUe6SqY83irmbWx2VIiRSi6sHM"
access_token = ""
fixture_id = ""
url = ''
home_team_name = ""
away_team_name = ""
fixture_data = {}
final_data = []
player_nams = {}
logger = None
retry_count = 0
conn = None


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def ConnectData():
    global conn
    db_config = read_db_config()
    try:
        conn = MySQLConnection(**db_config)
        if conn.is_connected():
            print('Connected to MySQL database')
            return 1
 
    except Error as e:
        print(e)
        return 0

def CreateLogger():
    
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT)
    # 创建Logger
    return_logger = logging.getLogger()

    return return_logger

def ParseTeamName():
    global home_team_name, away_team_name
    home_team_name = fixture_data["team_season_home_name"]
    away_team_name = fixture_data["team_season_away_name"]
    print "home_team_name=" + home_team_name + " away_team_name=" + away_team_name


def GetAccessToken():
    global access_token
    get_url = "https://api.sportdeer.com/v1/accessToken?refresh_token={}".format(refresh_token)
    
    token_response = requests_retry_session().get(get_url)
    #response.close()
    #logger.info("page got")
    while (token_response.status_code != 200):
        time.sleep(100)
        print "GetAccessToken Response Error"
        token_response = requests_retry_session().get(url)
        
    if token_response.status_code != 200:
        print "GetAccessToken Response Error"
        raise ResponseError(token_response.status_code)
    else:
        #logger.info(token_response.text)
        data = json.loads(token_response.text)
        access_token = data["new_access_token"]


def GetPage(fixture_id):
    global url, fixture_data
    url = 'https://api.sportdeer.com/v1/fixtures/{}?populate=lineups&populate=events&access_token={}'.format(fixture_id, access_token)
    #logger.info("start get page:" + url)
    response = requests.get(url,verify=False)
    #response.close()
    print "page got"
    if response.status_code != 200:
        print "GetPage Response Error:{}".format(response.status_code)
        raise ResponseError(response.status_code)
    else:
        data = json.loads(response.text)
        fixture_data = data["docs"][0]


    ##print(driver.page_source)
def GetLeague(League_id):
    global url,conn
    cursor = None
    response = None
    url = 'https://api.sportdeer.com/v1/leagues/{}/seasons?access_token={}'.format(League_id, access_token)
    #logger.info("start get page:" + url)
    response = requests_retry_session().get(url)
    #response.close()
    print "page got"
    while (response.status_code != 200):
        time.sleep(100)
        print "GetPage Response Error"
        response = requests_retry_session().get(url)
        #response.close()
    
    if response.status_code != 200:
        print "GetPage Response Error"
        raise ResponseError(response.status_code)
    else:
        data = json.loads(response.text)
        fixture_data = data["docs"]
        islasts = None
        for x in fixture_data:
            if 'is_last_season' not in x:
                islasts = 0
            else:
                islasts = 1
            try:
                if conn.is_connected():
                    query = "INSERT INTO  LeagueSeasons(_id,name,years,id_country,id_league,is_last_season) " \
                    "VALUES(%s,%s,%s,%s,%s,%s)"
                    args = (int(x["_id"]), x["name"],x["years"],int(x["id_country"]),int(x["id_league"]),islasts)
                    cursor = conn.cursor()
                    cursor.execute(query, args)
                    '''
                    if cursor.lastrowid:
                        print('last insert id', cursor.lastrowid)
                    else:
                        print('last insert id not found')
                    '''
                    conn.commit()
            except Error as error:
                print(error)
 
            finally:
                cursor.close()
            
        return fixture_data
    ##print(driver.page_source)
    
def GetMatches_Deatiles():
    global url,conn
    for years  in Const.NEWTEMPORADAS1:
        try:
            if conn.is_connected():
                query = """SELECT `_id` FROM LeagueSeasons WHERE `years` = '{}'""".format(Const.NEWTEMPORADAS[years])
                #print query
                cursor = conn.cursor()
                cursor.execute(query)
                row = cursor.fetchone()
                if row is not None:
                    League_id = row[0]
                    url = 'https://api.sportdeer.com/v1/seasons/{}/fixtures?populate=lineups&populate=events&access_token={}'.format(League_id, access_token)
                    #logger.info("start get page:" + url)
                    
                    response = requests_retry_session().get(url)
                    #response.close()
                    print "page got of year {}".format(years)
                    while (response.status_code != 200):
                        time.sleep(300)
                        print"GetPage Response Error"
                        response = requests_retry_session().get(url)
                        #response.close()
                    
                    if response.status_code != 200:
                        print "GetPage Response Error"
                        raise ResponseError(response.status_code)
                    else:
                        data = json.loads(response.text)
                        fixture_data = data["docs"]
                        for i in range(1, int(data["pagination"]["pages"]) + 1):
                            if i != 1:
                                GetAccessToken()
                                url = 'https://api.sportdeer.com/v1/seasons/{}/fixtures?populate=lineups&populate=events&page={}&access_token={}'.format(League_id,i, access_token)
                                
                                response = requests_retry_session().get(url)
                                print "page got"
                                while (response.status_code != 200):
                                    time.sleep(300)
                                    print "GetPage Response Error"
                                    response = requests_retry_session().get(url)
                                    #response.close()
                                
                                if response.status_code != 200:
                                    print "GetPage Response Error"
                                    raise ResponseError(response.status_code)
                                else:
                                    data = json.loads(response.text)
                                    fixture_data = data["docs"]
                                    Matchesdatainsert(fixture_data)
                            else:
                                #print fixture_data
                                Matchesdatainsert(fixture_data)
                        print "Finish of year {}".format(years)
                                
               
        except Error as error:
           print(error)

        finally:
           cursor.close()
    ''' 
    url = 'https://api.sportdeer.com/v1/seasons/2/fixtures?populate=lineups&populate=events&access_token={}'.format(League_id, access_token)
    #logger.info("start get page:" + url)
    response = requests.get(url)
    response.close()
    logger.info("page got")
    if response.status_code != 200:
        logger.error("GetPage Response Error:{}".format(response.status_code))
        raise ResponseError(response.status_code)
    else:
        data = json.loads(response.text)
        fixture_data = data["docs"]
        islasts = None
        for x in fixture_data:
            if 'is_last_season' not in x:
                islasts = 0
            else:
                islasts = 1
            try:
                query = "INSERT INTO  LeagueSeasons(_id,name,years,id_country,id_league,is_last_season) " \
                "VALUES(%s,%s,%s,%s,%s,%s)"
                args = (int(x["_id"]), x["name"],x["years"],int(x["id_country"]),int(x["id_league"]),islasts)
                cursor = conn.cursor()
                cursor.execute(query, args)
                
                if cursor.lastrowid:
                    print('last insert id', cursor.lastrowid)
                else:
                    print('last insert id not found')
                conn.commit()
            except Error as error:
                print(error)
 
            finally:
                cursor.close()
            
        return fixture_data
    '''

def Matchesdatainsert(our_data):
    global conn,fixture_data
    response = None
    for x in our_data:
        if conn.is_connected():
            cursor = conn.cursor()
            try:
                sql = """INSERT INTO `MatchesFixtures`(`_id`, `id_country`, `id_league`, `id_season`, `id_stage`, `fixture_status`, `fixture_status_short`, `id_team_season_away`, `id_team_season_home`, `number_goal_team_away`, `number_goal_team_home`, `round`, `schedule_date`, `stadium`, `team_season_away_name`, `team_season_home_name`, `id_referee`, `referee_name`, `game_started_at`, `lineup_confirmed`, `first_half_ended_at`, `second_half_started_at`, `spectators`, `game_ended_at`, `second_half_ended_at`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                #query = "INSERT INTO  LeagueSeasons(_id,name,years,id_country,id_league,is_last_season) " \
                #"VALUES(%s,%s,%s,%s,%s,%s)"
                args = (int(x["_id"]),int(x["id_country"]),int(x["id_league"])
                        ,int(x["id_season"]),int(x["id_stage"]),x["fixture_status"]
                        ,x["fixture_status_short"],int(x["id_team_season_away"])
                        ,int(x["id_team_season_home"]),int(x["number_goal_team_away"])
                        ,int(x["number_goal_team_home"]),int(x["round"]),x["schedule_date"]
                        ,x["stadium"],x["team_season_away_name"],x["team_season_home_name"]
                        ,int(x["id_referee"]) if 'id_referee' in x else None 
                        ,x["referee_name"] if 'referee_name' in x else None
                        ,x["game_started_at"] if 'game_started_at' in x else None
                        ,x["lineup_confirmed"] if 'lineup_confirmed' in x else None
                        ,x["first_half_ended_at"] if 'first_half_ended_at' in x else None
                        ,x["second_half_started_at"] if 'second_half_started_at' in x else None
                        ,int(x["spectators"]) if 'spectators' in x else None
                        ,x["game_ended_at"] if 'game_ended_at' in x else None
                        ,x["second_half_ended_at"] if 'second_half_ended_at' in x else None)
                #cursor = conn.cursor()
                cursor.execute(sql, args)
                conn.commit()
                if 'events' in x:
                    if x["events"]:
                        Matcheseventsdatainsert(x["events"])
                    #print fixevents
                '''
                if 'lineups' in x:
                    if x["lineups"]:
                        fixlineups = x["lineups"]
                    #print fixlineups
                '''
            except Error as error:
                print(error)
    
            finally:
                cursor.close()
                
                
def Matcheseventsdatainsert(matchevents):
    global conn,fixture_data
    for x in matchevents:
        if conn.is_connected():
            cursor = conn.cursor()
            try:
                if 'type' in x:
                    if x["type"] == "goal":
                        sql = """INSERT INTO `MatchesGoals`(`_id`, `id_fixture`, `elapsed`, `goal_subtype`, `goal_type_code`, `goal_type_desc`, `id_team_season`, `team_name`, `id_team_season_scorer`, `id_team_season_assister`, `player_name`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                        #query = "INSERT INTO  LeagueSeasons(_id,name,years,id_country,id_league,is_last_season) " \
                        #"VALUES(%s,%s,%s,%s,%s,%s)"
                        args = (None,int(x["id_fixture"]),int(x["elapsed"])
                                ,x["goal_subtype"] if 'goal_subtype' in x else None 
                                ,x["goal_type_code"] if 'goal_type_code' in x else None 
                                ,x["goal_type_desc"] if 'goal_type_desc' in x else None 
                                ,int(x["id_team_season"])
                                ,x["team_name"]
                                ,int(x["id_team_season_scorer"]) if 'id_team_season_scorer' in x else None
                                ,int(x["id_team_season_assister"]) if 'id_team_season_assister' in x else None
                                ,x["player_name"] if 'player_name' in x else None)
                        cursor.execute(sql, args)
                        conn.commit()
                    elif x["type"] == "card":
                        sql = """INSERT INTO `MatchesCards`(`_id`, `id_fixture`, `elapsed`, `card_type`, `id_team_season`, `team_name`, `id_team_season_player`, `player_name`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
                        args = (None,int(x["id_fixture"]),int(x["elapsed"])
                                ,x["card_type"] if 'card_type' in x else None 
                                ,int(x["id_team_season"]) 
                                ,x["team_name"] if 'team_name' in x else None 
                                ,int(x["id_team_season_player"]) if 'id_team_season_player' in x else None
                                ,x["player_name"] if 'player_name' in x else None)
                        cursor.execute(sql, args)
                        conn.commit()
                    elif x["type"] == "subst":
                        sql = """INSERT INTO `MatchesSubst`(`_id`, `id_fixture`, `elapsed`, `id_team_season`, `team_name`, `id_team_season_player_in`, `id_team_season_player_out`) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
                        args = (None,int(x["id_fixture"]),int(x["elapsed"])
                                ,int(x["id_team_season"])
                                ,x["team_name"] if 'team_name' in x else None
                                ,int(x["id_team_season_player_in"]) if 'id_team_season_player_in' in x else None
                                ,x["id_team_season_player_out"] if 'id_team_season_player_out' in x else None)
                        cursor.execute(sql, args)
                        conn.commit()
                        
                #cursor = conn.cursor()
            except Error as error:
                print(error)
    
            finally:
                cursor.close()
    
    
def ParseGoalIncident(event_info, event_time, event_phase, team_name):
    event_type = "goal"
    if "goal_type_code" in event_info.keys():
        if event_info["goal_type_code"] == "ng" or event_info["goal_type_code"] == "p":
            event_type = "goal"
        elif event_info["goal_type_code"] == "og":
            event_type = "own_goal"
        elif event_info["goal_type_code"] == "dg":
            return
        else:
            print "ParseGoalIncident unknown goal type:{}".format(event_info["goal_type_code"])
            return

    player_name = ""
    player_team_season_id = event_info["id_team_season_scorer"]
    if player_team_season_id in player_nams.keys():
        player_name = player_nams.get(player_team_season_id)
    else:
        print "ParseGoalIncident can't find player name player_team_season_id={}".format(player_team_season_id)

    incident_data = {"host_team": home_team_name, "away_team": away_team_name, "team": team_name, "player": player_name,
                     "time": event_time, "type": event_type, "phase": event_phase}
    final_data.append(incident_data)


def ParseCardIncident(event_info, event_time, event_phase, team_name):
    player_name = ""
    player_team_season_id = event_info["id_team_season_player"]
    if player_team_season_id in player_nams.keys():
        player_name = player_nams.get(player_team_season_id)
    else:
        print "ParseCardIncident can't find player name player_team_season_id={}".format(player_team_season_id)

    event_type = "yellow_card"
    if event_info["card_type"] == "y":
        event_type = "yellow_card"
    elif event_info["card_type"] == "r":
        event_type = "red_card"
    elif event_info["card_type"] == "y2":
        event_type = "secondyellow"
    else:
        print "ParseCardIncident wrong time:{} player:{}".format(event_time, player_name)

    incident_data = {"host_team": home_team_name, "away_team": away_team_name, "team": team_name, "player": player_name,
                     "time": event_time, "type": event_type, "phase": event_phase}
    final_data.append(incident_data)


def ParseSubStIncident(event_info, event_time, event_phase, team_name):
    player_in_name = ""
    player_out_name = ""
    player_in_id = event_info["id_team_season_player_in"]
    player_out_id = event_info["id_team_season_player_out"]
    if player_in_id in player_nams.keys():
        player_in_name = player_nams.get(player_in_id)
    else:
        print "ParseSubStIncident can't find player name player_in_id={}".format(player_in_id)

    if player_out_id in player_nams.keys():
        player_out_name = player_nams.get(player_out_id)
    else:
        print "ParseSubStIncident can't find player name player_out_id={}".format(player_out_id)

    incident_in_data = {"host_team": home_team_name, "away_team": away_team_name, "team": team_name, "player": player_in_name,
                     "time": event_time, "type": "substitution_enter", "phase": event_phase}
    final_data.append(incident_in_data)
    incident_out_data = {"host_team": home_team_name, "away_team": away_team_name, "team": team_name, "player": player_out_name,
                        "time": event_time, "type": "substitution_exit", "phase": event_phase}
    final_data.append(incident_out_data)



def ParseIncidentPhase(event_time):
        minute = int(event_time)
        if minute <= 45:
            return "first_half"
        elif minute <= 90:
            return "second_half"
        elif minute <= 105:
            return "overtime_first_half"
        elif minute <= 120:
            return "overtime_second_half"
        elif minute > 120:
            return "penalty_shootout"
        else:
            logger.error("ParseIncidentPhase Error event_time={}, minute={}".format(event_time, minute))
            return "wrong_time"


#分析阵容
def ParseMatchPlayers():
    lineup_data = fixture_data["lineups"]
    for player_info in lineup_data:
        player_nams[player_info["id_team_season_player"]] = player_info["player_name"]
        lineup_type = "starting_lineup"
        if player_info["is_startingXI"] is False:
            lineup_type = "alternate"

        player_data = {"host_team": home_team_name, "away_team": away_team_name, "team": player_info["team_name"],
                       "player": player_info["player_name"], "time": "00:00", "type": lineup_type,
                       "phase": "first_half"}
        final_data.append(player_data)


#分析事件
def ParseMatchIncidents():
    event_data = fixture_data["events"]
    logger.info("match incidents count={}".format(len(event_data)))
    for event_info in event_data:
        event_time = int(event_info["elapsed"])
        if "elapsed_plus" in event_info.keys():
            event_time += int(event_info["elapsed_plus"])
        event_phase = ParseIncidentPhase(event_info["elapsed"])
        team_name = event_info["team_name"]
        original_event_type = event_info["type"]
        if original_event_type == "goal":
            ParseGoalIncident(event_info, "{}:00".format(event_time), event_phase, team_name)
        elif original_event_type == "card":
            ParseCardIncident(event_info,  "{}:00".format(event_time), event_phase, team_name)
        elif original_event_type == "subst":
            ParseSubStIncident(event_info,  "{}:00".format(event_time), event_phase, team_name)
        else:
            continue




def CheckMatchEnd():
    if "game_ended_at" in fixture_data.keys():
        return True
    else:
        return False


class MatchNotEndError(RuntimeError):
    def __init__(self):
        pass


class ResponseError(RuntimeError):
    def __init__(self, reponse_code):
        self.response_code = reponse_code



def LoadPage():
    global fixture_id
    GetAccessToken()
    if len(sys.argv) > 1:
        numoffunc = int(sys.argv[1])
        if numoffunc == 1: #(1)
            if len(sys.argv) == 3:
                fixture_id = sys.argv[2]
                GetPage(fixture_id)
                if CheckMatchEnd() is False:
                    raise MatchNotEndError()
                else:
                    logger.info("Match End")
            
                ParseTeamName()
                ParseMatchPlayers()
                ParseMatchIncidents()
                logger.info("final_data={}".format(final_data))
            else:
                print "ex: file.py 1 (fixture_id)"
        elif numoffunc == 2: #(2)
            if len(sys.argv) == 3:
                League_id = sys.argv[2]
                GetLeague(League_id)
            else:
                print "ex: file.py 2 (League_id)"
        elif numoffunc == 3: #(3)
            if len(sys.argv) == 2:
                #all matches for all years 
                GetMatches_Deatiles()
                print "Finish :)"
            elif len(sys.argv) == 3:
                print "mm"
            else:
                print "ex: file.py 2\n"
                print "ex: file.py 2 (Seazon id)"
        else:
            print "Please choose command number 1......9"
        conn.close()
    else:
        print "Please choose command number 1......9"

def PostResult():
    r = requests.post('http://httpbin.org/post', json=final_data)
    logger.info("Post status_code= {}".format(r.status_code))


#logger = CreateLogger()
isconn = ConnectData()
start_time = time.time()
while time.time() - start_time < SpiderTimeOut:
    try:
        retry_count += 1
        print "try times:{}".format(retry_count)
        LoadPage()
    except MatchNotEndError:
        print "Match is not end yet!!, sleep for a while"
        time.sleep(CheckMatchEndInterval)
    else:
        print "Load Page Sccessed!!!"
        #PostResult()
        break
    '''
    except Exception as e:
        logger.error("Exception :{}".format(e))
        import traceback
        traceback.print_exc()
        time.sleep(RetryInterval)
        
        
        
        logging.shutdown()
    s'''
    
else:
   print "Spider Time Out"




