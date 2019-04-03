#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# encoding: utf-8
__author__ = 'Mohamad-Husari'

import datetime
import time
import csv
import re , sys

from bs4 import BeautifulSoup
import requests

import Const
#from Main import writer
#from FutbolClass import Partido

# WEB: http://www.resultados-futbol.com
partidos = dict()

deteilindex = -1
'''
with open('matchesdetails.csv', 'wb+') as master:
            fieldnames = ['id', 'goalteam' , 'changed_result' , 'player_name' , 'player_img' ,
                    'player_profile' , 'status' , 'time']
            writernew = csv.DictWriter(master, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)
            writernew.writeheader()
'''

# Change teams names with the full name
def replace_equipos(equipo):
    equipo = equipo.replace('Atletico-Madrid', 'Atletico de Madrid')
    equipo = equipo.replace('Real-Sociedad', 'Real Sociedad')
    equipo = equipo.replace('Celta', 'Celta de Vigo')
    equipo = equipo.replace('Athletic Club-Bilbao', 'Athletic Club')
    equipo = equipo.replace('Athletic-Bilbao', 'Athletic Club')
    equipo = equipo.replace('Real Betis', 'Betis')
    equipo = equipo.replace('Zaragoza', 'Real Zaragoza')
    equipo = equipo.replace('Recreativo', 'Recreativo de Huelva')
    equipo = equipo.replace('Sporting de Gijon-Gijon', 'Sporting de Gijon')
    equipo = equipo.replace('Sporting-Gijon', 'Sporting de Gijon')
    equipo = equipo.replace('Racing', 'Racing de Santander')
    equipo = equipo.replace('Real-Madrid', 'Real Madrid')
    equipo = equipo.replace('Valencia-Cf', 'Valencia')
    equipo = equipo.replace('Ud-Palmas', 'Las Palmas')
    equipo = equipo.replace('Gimnastic-Tarragona', 'Gimnastic de Tarragona')
    equipo = equipo.replace('Ucam-Murcia-C-F', 'UCAM Murcia')
    equipo = equipo.replace('Real-Real Zaragoza', 'Real Zaragoza')
    equipo = equipo.replace('Rayo-Vallecano', 'Rayo Vallecano')
    equipo = equipo.replace('Ad-Alcorcon', 'Alcorcon')
    equipo = equipo.replace('Real-Oviedo', 'Real Oviedo')
    equipo = equipo.replace('Sevilla-B', 'Sevilla Atletico')
    equipo = equipo.replace('Girona-Fc', 'Girona')

    return equipo


# Get The date and the time of the match
def get_fecha_partido(fecha_sucia):
    charts_remove = ['[', '\\n', '\\t']
    fecha = re.sub(r'[<](/)?td[^>]*[>]', '', fecha_sucia)\
        .translate(None, ''.join(charts_remove))
    fecha = fecha.split('<br/>')[0].strip()
    fecha = fecha.split(' ')
    meses = {'Ene': '01', 'Feb': '02', 'Mar': '03', 'Abr': '04', 'May': '05',
             'Jun': '06', 'Jul': '07', 'Ago': '08', 'Sep': '09', 'Oct': '10',
             'Nov': '11', 'Dic': '12', 'Oc': '10', 'Ee': '01'}
    fecha = "%s/%s/20%s" % (fecha[0], meses[fecha[1]], fecha[2])

    return fecha


# Get Name of the teams
def get_equipo(equipo_sucio):
    club = equipo_sucio.find_all('a')[0].find_all('img')[0].attrs['alt']
    '''
    club = equipo_sucio.find_all('a')[1].get_text()
    club = re.sub(r'[<](/)?a[^>]*[>]', '', club).replace('</a>','').strip()
    '''
    #club = equipo_sucio.find_all('a')[1].attrs['href'].replace('/', '')
    return replace_equipos(club.strip())


# Get Results <tr>
def get_resultado(resultado_sucio):
    resultado = resultado_sucio.find('a').text
    resultado = re.sub(r'[<](/)?a[^>]*[>]', '', resultado).replace('</a>',
                                                                   '').strip()
    if 'x' in resultado:
        return None
    else:
        return resultado.split('-')

def get_golasandcards(details_GAC):
    resultado = details_GAC.find('a').text
    resultado = re.sub(r'[<](/)?a[^>]*[>]', '', resultado).replace('</a>',
                                                                   '').strip()
    if 'x' in resultado:
        return None
    else:
        return resultado.split('-')
    
def get_matchid(dae_mach_get,deteilindex):
    charts_remove = ['[', '\\n', '\\t']
    alldeteils = (re.sub(r'[<](/)?span[^>]*[>]', '', dae_mach_get))\
        .translate(None, ''.join(charts_remove))
    alldeteils = re.sub(r'[<](/)?small[^>]*[>]', '', alldeteils)\
        .translate(None, ''.join(charts_remove))
    alldeteils = alldeteils.split('<br/>')[0].strip()
    alldeteils = re.findall(r'id=\".*?\"', alldeteils)
    #print repr(alldeteils[deteilindex].replace('id="dae-mach-', '').replace('"', ''))
    return alldeteils[deteilindex].replace('id="dae-mach-', '').replace('"', '')

def get_goalscard(golascards,dae_mach,writernew):
    changed_res_home = 0
    changed_res_away = 0
    if golascards:
        for tks in golascards:
            #print tks
            m1local = BeautifulSoup(str(tks.find_all('td', {'class': 'equipo1'})), "html.parser")
            m2visit = BeautifulSoup(str(tks.find_all('td', {'class': 'equipo2'})), "html.parser")
            theresult = BeautifulSoup(str(tks.find_all('td', {'class': 'rstd'})), "html.parser")
            resultclass = str(theresult.find("span")['class']).replace("u'", '').replace("[", '').replace("]", '').replace("'", '')
            statusval = str()
            if resultclass == "flaticon-live-3":
                statusval = "redcard"
            elif resultclass == "flaticon-live-4":
                statusval = "yellowbeforredcard"
            elif resultclass == "flaticon-live-15": 
                statusval = "penaltyfailed"
                
            #print "momom"
            #val3 = repr(m1local.get_text().encode('ascii', 'ignore').decode('ascii')).replace('\\n', '').replace('\\', '').replace('\n', '').replace(' ', '')
            #val4 =  repr(m2visit.get_text().encode('ascii', 'ignore').decode('ascii')).replace('\\n', '').replace('\\', '').replace('\n', '').replace(' ', '')
            #print val3
            #print val4
            val1 = m1local.get_text().encode('ascii', 'ignore').decode('ascii')
            val1 = val1.replace('\\n', '').replace('\\', '').replace('\n', '').replace(' ', '')
            #print repr(val1)
            val2 = m2visit.get_text().encode('ascii', 'ignore').decode('ascii')
            val2 = val2.replace('\\n', '').replace('\\', '').replace('\n', '').replace(' ', '')
            #print val1
            #print val2
            #print repr(val2)
            '''
            print repr(str(m1local.text))
            print repr(str(m2visit.text))
            print repr(m1local.get_text().encode("ascii"))
            val = str(m1local.get_text().encode("ascii"))
            print val
            print repr(val.replace('\\n', '').replace('\\', '').replace(' ', ''))
            print repr(m2visit.get_text().strip().replace('\\n', '').replace('\\', '').replace(' ', ''))
            #val = str(m2visit.text).sub('\n|\r', '', '\nx\n\r\n')
            #print repr(val)
            '''
            # print str(m1local.text).replace('\\n', '').replace('\\', '') + "\n\n\n"
            # print str(m2visit.text).replace('\\n', '').replace('\\', '') + " mohamad"
            if val1 != "[]" :
                # print "goal home team"
                if resultclass == "url":
                    changed_res_home = changed_res_home + 1
                    statusval = "goal"
                elif resultclass == "flaticon-live-6":
                    changed_res_away = changed_res_away + 1
                    statusval = "owngoal"
                
                chres = str(changed_res_home) + "=" + str(changed_res_away)
                #print chres
                ''''
                #changed_result
                print str(changed_res_home) + "-" + str(changed_res_away)  
                #status (goal,card,penalty failed)
                print statusval
                #match_goal_time
                print m1local.find("b").text
                #player_img
                print m1local.find("img").attrs['src']
                #player_profile
                print m1local.find("span").find("a").attrs['href']
                #print m1local.find("span").find("a").text
                #listnameplayer = m1local.find("span").find("a").attrs['href'].split("/")[2].split("-")
                #player_name
                #print listnameplayer[0] + ". " + listnameplayer[1]
                '''
                listnameplayer = m1local.find("span").find("a").text.encode('ascii', 'ignore').decode('ascii')
                listnameplayer = listnameplayer.replace('\\n', '').replace('\\', '').replace('\n', '')
                #listnameplayer =  str(listnameplayer).encode("utf-8")
                #print listnameplayer
                ##listnameplayer = m1local.find("span").find("a").attrs['href'].split("/")[2].split("-")
                ##print listnameplayer[0] + ". " + listnameplayer[1]
                writernew.writerow({'id': dae_mach, 'goalteam': 'HT', 'changed_result': str(chres), 'player_name': listnameplayer,
                                     'player_img': m1local.find("img").attrs['src'], 'player_profile': m1local.find("span").find("a").attrs['href'],
                                      'status': statusval, 'time': m1local.find("b").text})
                
            if val2 != "[]":
                #print "goal away team"
                if resultclass == "url":
                    changed_res_away = changed_res_away + 1
                    statusval = "goal"
                elif resultclass == "flaticon-live-6":
                    changed_res_home = changed_res_home + 1
                    statusval = "owngoal"
                chres = str(changed_res_home) + "=" + str(changed_res_away)
                #print chres
                '''   
                #changed_result
                print str(changed_res_home) + "-" + str(changed_res_away)   
                #status (goal,card,penalty failed)
                print statusval
                print m2visit.find("b").text
                print m2visit.find("img").attrs['src']
                print m2visit.find("span").find("a").attrs['href']
                #listnameplayer = m2visit.find("span").find("a").attrs['href'].split("/")[2].split("-")
                #print listnameplayer[0] + ". " + listnameplayer[1]
                
                #listnameplayer = m2visit.find("span").find("a").attrs['href'].split("/")[2].split("-")
                #print listnameplayer[0] + ". " + listnameplayer[1]
                '''
                listnameplayer = m2visit.find("span").find("a").text.encode('ascii', 'ignore').decode('ascii')
                listnameplayer = listnameplayer.replace('\\n', '').replace('\\', '').replace('\n', '')
                #listnameplayer =  str(listnameplayer).encode("utf-8")
                #print listnameplayer
                writernew.writerow({'id': dae_mach, 'goalteam': 'AT', 'changed_result': str(chres), 'player_name': listnameplayer,
                                     'player_img': m2visit.find("img").attrs['src'], 'player_profile': m2visit.find("span").find("a").attrs['href'],
                                      'status': statusval, 'time': m2visit.find("b").text})
            
    
def get_partido(tr_partido, tr_details_GAC, deteilindex,writernew):
    soup_tr_details_GAC = BeautifulSoup(tr_details_GAC, "html.parser")
    soup_tr = BeautifulSoup(tr_partido, "html.parser")

    '''
    dae_mach_get = str(soup_tr.find_all('td', {'class': 'fecha'}))
    charts_remove = ['[', '\\n', '\\t']
    alldeteils = (re.sub(r'[<](/)?span[^>]*[>]', '', dae_mach_get))\
        .translate(None, ''.join(charts_remove))
    alldeteils = re.sub(r'[<](/)?small[^>]*[>]', '', alldeteils)\
        .translate(None, ''.join(charts_remove))
    alldeteils = alldeteils.split('<br/>')[0].strip()
    alldeteils = re.findall(r'id=\".*?\"', alldeteils)
    dae_mach = alldeteils[deteilindex].replace('id="dae-mach-', '').replace('"', '')
    '''
    if deteilindex == 10:
        deteilindex = -1
    deteilindex += 1
    dae_mach = get_matchid(str(soup_tr.find_all('td', {'class': 'fecha'})) , deteilindex)
    isfix =  BeautifulSoup(str(soup_tr.find_all('td', {'class': 'rstd'})), "html.parser")
    isfix = isfix.find("a").find("div")
    if isfix:
        if len(sys.argv) == 2 or len(sys.argv) == 3:
            fecha = get_fecha_partido(str(soup_tr.find_all('td', {'class': 'fecha'})))
            #print fecha
            local = get_equipo(
                BeautifulSoup(str(soup_tr.find_all('td', {'class': 'equipo1'})), "html.parser"))
            #print local
            visitante = get_equipo(
                BeautifulSoup(str(soup_tr.find_all('td', {'class': 'equipo2'})), "html.parser"))
            #print visitante
            resultado = BeautifulSoup(str(soup_tr.find_all('td', {'class': 'rstd'})), "html.parser")
            resultado = resultado.find("a").find("div").text
            #print resultado
            return {
            "id": dae_mach,
            "local": local,
            "visitante": visitante,
            "time": resultado,
            "fecha": fecha
            }

        elif len(sys.argv) == 1:
            return
        
    elif len(sys.argv) == 1:
        golascards = soup_tr_details_GAC.find_all(attrs={"data-match": dae_mach})
        get_goalscard(golascards,dae_mach,writernew)
    elif len(sys.argv) == 2  or len(sys.argv) == 3:
        return
            
        '''
    elif len(sys.argv) == 2:
        if not golascards:
            fechanew = get_fecha_partido(str(soup_tr.find_all('td', {'class': 'fecha'})))
    '''      
        
        #changed_res_home = 0
        #changed_res_away = 0
        #print dae_mach
    
    fecha = get_fecha_partido(str(soup_tr.find_all('td', {'class': 'fecha'})))
    local = get_equipo(
        BeautifulSoup(str(soup_tr.find_all('td', {'class': 'equipo1'})), "html.parser"))
    visitante = get_equipo(
        BeautifulSoup(str(soup_tr.find_all('td', {'class': 'equipo2'})), "html.parser"))
    resultado = get_resultado(
        BeautifulSoup(str(soup_tr.find_all('td', {'class': 'rstd'})), "html.parser"))
    #print tr_details_GAC
    #golascards = get_golasandcards(
        #BeautifulSoup(str(soup_tr.find_all('td', {'class': 'rstd'})), "html.parser"))
    return {
    "id": dae_mach,
    "local": local,
    "visitante": visitante,
    "gLocal": resultado[0],
    "gVisitante": resultado[1],
    "fecha": fecha
}
        
        
def find_partidos(tabla_partidos,writernew):
        partidos_jornada = list()
        soup_tabla = BeautifulSoup(tabla_partidos, "html.parser")
        #tr_goalscards = soup_tabla.find_all('tr', {'class': 'vevent'})
        tr_details_GAC = soup_tabla.find_all('tr', {'class': 'league-match-events'})
        tr_partidos = soup_tabla.find_all('tr', {'class': 'vevent'})
    
        for tr in tr_partidos:
            try:
                partidos_jornada.append(get_partido(str(tr), str(tr_details_GAC), deteilindex,writernew))
            except:
                pass
    
        return partidos_jornada


# The opening function
def get_partidos(contador):
    if len(sys.argv) == 1:
        with open('matches.csv', 'wb+') as csvfile , open('matchesdetails.csv', 'wb+') as master:
            fieldnames = ['id', 'goalteam' , 'changed_result' , 'player_name' , 'player_img' ,
                        'player_profile' , 'status' , 'time']
            writernew = csv.DictWriter(master, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)
            writernew.writeheader()
            fieldnames = ['id', 'season' , 'round' , 'hometeam' , 'awayteam' ,
                    'goals_home_team' , 'goals_away_team' , 'matchdate' , 'timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            
            for year in Const.NEWTEMPORADAS1:
                print "****** EPL SEASON %s ******" % Const.NEWTEMPORADAS[year]
        
                # Get all the "jawlat" for every year
                for i in range(1, Const.MAX_JORNADAS_1 + 1):
                    # Url and but the year after that "jawla"
                    url = Const.URL_PRIMERA_2018 % (year, i)
                    print "Geting Data : %s\n" % url
        
                    # Send a request to get the URL cons
                    req_primera = requests.get(url)
        
                    #BeautifulSoup Moudel to get the page code "HTML" concept
                    soup_primera = BeautifulSoup(req_primera.text, "html.parser")
        
                    #Get from the HTML code the Table : of id = tabla1
                    tabla_partidos = str(soup_primera.find('table', {'id': 'tabla1'}))
                    
                    partidos_jornada = find_partidos(tabla_partidos,writernew)
                    
                    for part in partidos_jornada:
                        if part != None:
                            contador += 1
                            '''
                            partidos[contador] = Partido(contador, Const.NEWTEMPORADAS[year], 1, i,
                                                     part['local'], part['visitante'],
                                                     part['gLocal'], part['gVisitante'],
                                                     part['fecha'])
                            '''
                            timestampe = int(time.mktime(
                            datetime.datetime.strptime(part['fecha'], "%d/%m/%Y").timetuple()))
                            writer.writerow({'id': part['id'], 'season': Const.NEWTEMPORADAS[year], 'round': i, 'hometeam': part['local'], 'awayteam': part['visitante'], 'goals_home_team': part['gLocal'], 'goals_away_team': part['gVisitante'], 'matchdate': part['fecha'], 'timestamp': timestampe})
    elif len(sys.argv) == 2 or len(sys.argv) == 3 :
        rangefrom = None
        rangeto = None
        if len(sys.argv) == 2:
            rangefrom = 1
            rangeto = Const.MAX_JORNADAS_1
        else:
            rangeto = int(sys.argv[2])
            rangefrom = int(sys.argv[2])
        with open('fix.csv', 'wb+') as csvfile :
            fieldnames = ['id', 'season' , 'round' , 'hometeam' , 'awayteam' ,
                     'time' , 'matchdate' , 'timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            # Get all the "jawlat" for every year
            for i in range(rangefrom, rangeto + 1):
                # Url and but the year after that "jawla"
                url = Const.URL_PRIMERA_2018 % (sys.argv[1], i)
                print "Geting Data : %s\n" % url
    
                # Send a request to get the URL cons
                req_primera = requests.get(url)
    
                #BeautifulSoup Moudel to get the page code "HTML" concept
                soup_primera = BeautifulSoup(req_primera.text, "html.parser")
    
                #Get from the HTML code the Table : of id = tabla1
                tabla_partidos = str(soup_primera.find('table', {'id': 'tabla1'}))
                
                partidos_jornada = find_partidos(tabla_partidos,writer)
                for part in partidos_jornada:
                    if part != None:
                        timestampe = int(time.mktime(
                        datetime.datetime.strptime(part['fecha'], "%d/%m/%Y").timetuple()))
                        writer.writerow({'id': part['id'], 'season': Const.NEWTEMPORADAS[sys.argv[1]], 'round': i, 'hometeam': part['local'], 'awayteam': part['visitante'], 'time': part['time'], 'matchdate': part['fecha'], 'timestamp': timestampe})
    else:
            print "Error while running"
                        
