#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
__author__ = 'Mohamad Husari/Abed Arauat'

# web: http://www.bdfutbol.com
URL_PRIMERA = "http://www.bdfutbol.com/es/t/teng%s.html"
#URL_SEGUNDA = "http://www.bdfutbol.com/en/t/teng%s2a.html"
TEMPORADAS = [
    "2014-15", "2015-16",
    "2016-17", "2017-18"
]
'''
TEMPORADAS = [
    "2000-01", "2001-02", "2002-03", "2003-04", "2004-05", "2005-06", "2006-07",
    "2007-08", "2008-09", "2009-10",
    "2010-11", "2011-12", "2012-13", "2013-14", "2014-15", "2015-16",
    "2016-17", "2017-18"
]
'''

NEWTEMPORADAS = {
    "2001" : "2000-01", "2002" : "2001-02", "2003" : "2002-03", "2004" : "2003-04",
    "2005" : "2004-05", "2006" : "2005-06", "2007" : "2006-07", "2008" : "2007-08",
    "2009" : "2008-09", "2010" : "2009-10", "2011" : "2010-11", "2012" : "2011-12",
    "2013" : "2012-13", "2014" : "2013-14", "2015" : "2014-15", "2016" : "2015-16",
    "2017" : "2016-17", "2018" : "2017-18"
}
'''
#web: http://www.resultados-futbol.com/ Get all the resualts for this years :
NEWTEMPORADAS = {
    "2002" : "2001-02"
}
'''

NEWTEMPORADAS1 = [
    "2001", "2002", "2003", "2004", "2005", "2006",
    "2007", "2008", "2009",
    "2010", "2011", "2012", "2013", "2014", "2015",
    "2016", "2017", "2018"
]



TEMPORADA_2018 = "2017-2018"
URL_PRIMERA_2018 = "http://www.resultados-futbol.com/premier%s/grupo1/jornada%s"
#URL_SEGUNDA_2018 = "http://www.resultados-futbol.com/segunda/grupo1/jornada%s"
MAX_JORNADAS_PERPAGE = 10
MAX_JORNADAS_1 = 38
MAX_JORNADAS_2 = 42