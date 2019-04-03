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

def main():
    with open('fix.csv', 'wb+') as csvfile :
        fieldnames = ['id', 'season' , 'round' , 'hometeam' , 'awayteam' ,
                'goals_home_team' , 'goals_away_team' , 'matchdate' , 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        
        if len(sys.argv) == 2:
            # Get all the "jawlat" for every year
            for i in range(1, Const.MAX_JORNADAS_1 + 1):
                # Url and but the year after that "jawla"
                url = Const.URL_PRIMERA_2018 % (sys.argv[1], i)
                print "Geting Data : %s\n" % url
    
                # Send a request to get the URL cons
                req_primera = requests.get(url)
    
                #BeautifulSoup Moudel to get the page code "HTML" concept
                soup_primera = BeautifulSoup(req_primera.text, "html.parser")
    
                #Get from the HTML code the Table : of id = tabla1
                tabla_partidos = str(soup_primera.find('table', {'id': 'tabla1'}))
                
                partidos_jornada = find_partidos(tabla_partidos,writernew)
                
                for part in partidos_jornada:
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
        elif len(sys.argv) == 3:
            url = Const.URL_PRIMERA_2018 % (sys.argv[1], sys.argv[2])
            print "Geting Data : %s\n" % url

            # Send a request to get the URL cons
            req_primera = requests.get(url)

            #BeautifulSoup Moudel to get the page code "HTML" concept
            soup_primera = BeautifulSoup(req_primera.text, "html.parser")

            #Get from the HTML code the Table : of id = tabla1
            tabla_partidos = str(soup_primera.find('table', {'id': 'tabla1'}))
            
            partidos_jornada = find_partidos(tabla_partidos,writernew)
            
            for part in partidos_jornada:
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
        else:
            print "Error while running"
                    
if __name__ == '__main__':
    main()
