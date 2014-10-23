#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 redglory
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import codecs
import urllib2
from datetime import date, timedelta, datetime
from itertools import chain
from urlparse import urljoin
from bs4 import BeautifulSoup as BS

try:
    import json
except:
    import simplejson as json

BASE_URL = 'http://www.slbenfica.pt/'


def _full_url(url):
    ''' Retrieve full url '''
    return urljoin(BASE_URL, url)

def download_page(url, data=None):

    request = urllib2.Request(url, data)
    request.add_header('Accept-Encoding', 'utf-8')
    response = urllib2.urlopen(request)
    return response

def monthToNum(month):

    return{
            'Jan' : 1,
            'Fev' : 2,
            'Mar' : 3,
            'Abr' : 4,
            'Mai' : 5,
            'Jun' : 6,
            'Jul' : 7,
            'Ago' : 8,
            'Set' : 9, 
            'Out' : 10,
            'Nov' : 11,
            'Dez' : 12
    }[month.title()]

class Calendar(object):
    
    def __init__(self, startDate=None, numWeeks=None, language=None):
        
        if startDate:
            self.first_week_day, self.last_week_day = Calendar.first_last_week_day(startDate)
        else:
            self.first_week_day, self.last_week_day = Calendar.first_last_week_day(date.today())

        self.numWeeks = numWeeks if numWeeks else '1'

        self.language = language if language else 'pt-pt'


    @staticmethod
    def first_last_week_day(day):
        day_of_week = day.weekday()
    
        to_beginning_of_week = timedelta(days=day_of_week)
        beginning_of_week = day - to_beginning_of_week
    
        to_end_of_week = timedelta(days=6 - day_of_week)
        end_of_week = day + to_end_of_week
    
        return (beginning_of_week.strftime("%d-%m-%Y"), end_of_week.strftime("%d-%m-%Y"))

    def get_calendar(self):
        
        url = 'http://m.slbenfica.pt/HttpHandlers/SLBSportsAgenda.ashx?ModID=1172&LvlId=-1&AgendaStartDate='+self.first_week_day+'%2000:00:00&NumWeeks='+self.numWeeks+'&CurrentType=Event&Culture='+self.language+'&Mobile=true&PurchaseTicketURL=https://m.slbenfica.pt/'+self.language+'/bilhetes/comprar.aspx'

        # convert html to json
        calendar = {}
        events = []
        event  = {}

        html_soup = BS(download_page(url).read().decode('utf-8', 'ignore'))
        
        uls = html_soup.findAll('ul', {'class': 'agEvt'})
        lis = [ul.findAll('li') for ul in uls]

        for li in chain(*lis):
            
            day = int(li.find('span', {'class': 't20wt'}).string)
            _month = li.find('p', {'class': 't9red'}).string
            month = monthToNum(_month)
            year = datetime.now().year
            if _month < datetime.now().month:
                year = year + 1
            _date = date(year, month, day).strftime("%d-%m-%Y")

            weekday                 = li.find('p', {'class': 't9lt'}).string
            sport                   = li.find('div', {'class': 'agMod t14red'}).string
            event['sport']          = sport
            event['event']          = li.find('p', {'class': 'agTit t12wtB'}).string
            event['local']          = li.find('p', {'class': 'agLoc t12lt2B'}).string
            event['description']    = li.find('span', {'class': 't12lt'}).string if li.find('span', {'class': 't12lt'}) else '""'
            img_home                = li.find('div', {'class': 'eHo'})
            event['home_team_img']  = _full_url(img_home.img['src']) if img_home else ''
            event['home_team_name'] = img_home.img['alt'] if img_home else ''
            img_away                = li.find('div', {'class': 'eVi'})
            event['away_team_img']  = _full_url(img_away.img['src']) if img_away else ''
            event['away_team_name'] = img_away.img['alt'] if img_away else ''
            event['buy_ticket']     = li.find('a', {'class': 'agBt btDark'}).href if li.find('a', {'class': 'agBt btDark'}) else ''

            if calendar.get(_date):
                calendar[_date].append(event)
            else:
                events.append(event)
                calendar[_date] = events
            event = {}
            events = []

        return calendar if calendar else []
        
if __name__ == '__main__':
    
    _startdate = date(2014, 10, 25)
    calendar = Calendar(startDate=_startdate, numWeeks='2').get_calendar()
    if calendar:
        with codecs.open('calendar.json', "w", encoding='utf-8') as f:
            f.write(unicode(json.dumps(calendar, ensure_ascii=False)))
        f.close()
    else:   
        print "No response"