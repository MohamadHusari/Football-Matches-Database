#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
__author__ = 'Mohamad-Husari'

#import ScrapBDFutbol as bd_futbol
import ScrapTemporada2018 as this_temporada
#import csv


#Get the Values
partidos_2017_18 = this_temporada.get_partidos(0)
'''
fichero = open('DataSetPartidos.txt', 'w')
fichero.write('count::id::season::round::hometeam::awayteam::'
              'goals_home_team::goals_away_team::matchdate::timestamp\n')

#for value in partidos.values():
    #fichero.write('%s\n' % str(value))

for value in partidos_2017_18.values():
    fichero.write('%s\n' % str(value))

fichero.close()


['id', 'season' , 'round' , 'hometeam' , 'awayteam' ,
                'goals_home_team' , 'goals_away_team' , 'matchdate' , 'timestamp']
with open('matches.csv', 'w', newline='') as csvfile:
    fieldnames = ['ID', 'Season' , 'Round' , 'HomeTeam' , 'AwayTeam' , 'Goals-Home-Team' , 'Goals-Away-Team' , 'MatchDate' , 'Timestamp']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
'''
   
