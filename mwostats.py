#c:\Python27\python.exe
from __future__ import division
import mechanize, cookielib, re, csv
from bs4 import BeautifulSoup as bs

#############################################################
# Simple MWO stats scraper.
# Logs into mwomercs.com, grabs and dumps specified users
# battle mech stats to MechStats.csv.
#
# Script Requirements:
#   - Python 2.7 interpreter
#   - http://wwwsearch.sourceforge.net/mechanize
#      pip install mechanize
#   - https://pypi.python.org/pypi/beautifulsoup4
#      pip install bs4
#############################################################

# MWO username & password
Email = 'mwostats@gmail.com'
Password = 'fakepassword'

# File to dump
StatsFile = 'MechStats.csv'

# Open stats csv
try:
    csvStatsFile = open(StatsFile, 'wb', 0)
    csvWriter = csv.writer(csvStatsFile)
except Exception, Error:
    print 'Unable to open stats file %s - %s' % (StatsFile, Error)
    exit()
    
# Define some URLs
LoginURL = 'https://mwomercs.com/login'
StatsURL = 'https://mwomercs.com/profile/stats?type=mech'

# Instantiate browser & cookie jar
br = mechanize.Browser()
br.addheaders = [('User-agent',
  'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1')]

cj = cookielib.CookieJar()
br.set_cookiejar(cj)

# Debug traces
#br.set_debug_http(True)
#br.set_debug_redirects(True)
#br.set_debug_responses(True)

# Authenticate
br.open(LoginURL)
br.select_form(nr=0)
br['email'] = Email
br['password'] = Password
br.submit()

# Fetch stats
page = br.open(StatsURL)
soup = bs(page, 'html.parser')
table = soup.find('table')

# Variables for global stats
MatchesTot = 0
WinsTot = 0
LossesTot = 0
KillsTot = 0
DeathsTot = 0
DmgTot = 0
DmgPMTot = 0
XPTot = 0

# Dump headers
csvWriter.writerow(['Mech', 'Matches', 'Wins', 'Losses', 'WL Ratio',
                    'Kills', 'Deaths', 'KDR', 'Damage', 'XP', 'Time Played',
                    'Dmg per Match', 'DPM/400', 'KDR/2', 'Kills Per Match',
                    'Rating'])

# Parse Stats 
for row in soup('table')[0].findAll('tr'):
    col = row.findAll('td')
    if len(col) == 0: continue
    try:
        # PGI stats
        Mech = col[0].string.encode('utf-8')
        Matches = int(col[1].string.encode('utf-8'))
        Wins = int(col[2].string.encode('utf-8'))
        Losses = int(col[3].string.encode('utf-8'))
        WLRatio = float(col[4].string.encode('utf-8'))
        Kills = int(col[5].string.encode('utf-8'))
        Deaths = int(col[6].string.encode('utf-8'))
        KDR = float(col[7].string.encode('utf-8'))
        Dmg = int(re.sub(r'(,)', r'',col[8].string.encode('utf-8')))
        XP = int(re.sub(r'(,)', r'', col[9].string.encode('utf-8')))
        Time = col[10].string.encode('utf-8')
        
        # Extra Calculated stats
        DmgPM = round(Dmg/Matches, 2)
        DPM400 = round(float(DmgPM/400), 2)
        KDR2 = round(KDR/2, 2)
        KPM = round(Kills/Matches, 2)
        Rating = round(WLRatio+DPM400+KDR2, 2)
        
        # Track Overall stats
        MatchesTot += Matches
        WinsTot += Wins
        LossesTot += Losses
        KillsTot += Kills
        DeathsTot += Deaths
        DmgTot += Dmg
        XPTot += XP
        
        # Dump stats
        csvWriter.writerow([Mech, Matches, Wins, Losses, WLRatio, Kills,
                            Deaths, KDR, Dmg, XP, Time, DmgPM, DPM400,
                            KDR2, KPM, Rating])
    except Exception, Error:
        print 'Something wicked happened - %s' % (Error)
        exit()
            
# Dump overall stats
WLRatioTot = round(WinsTot/LossesTot, 2)
KDRTot = round(KillsTot/DeathsTot, 2)
DmgPMTot = round(DmgTot/MatchesTot, 2)

csvWriter.writerow(['Overall Statistics Totals'])
csvWriter.writerow(['Matches', 'Wins', 'losses', 'WL Ratio', 'Kills', 'Deaths', 'KDR', 'Damage', 'XP', 'Dmg per Match'])
csvWriter.writerow([MatchesTot, WinsTot, LossesTot, WLRatioTot, KillsTot, DeathsTot, KDRTot, DmgTot, XPTot, DmgPMTot])

        
print 'Success - stats saved to %s' % (StatsFile)
