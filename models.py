"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *
import csv # To read csv files


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_user_id():
    return auth.current_user.get('id') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()

# -------------------------- ADDED FUNCTIONS -------------------------- #
# Should we start with row 1 instead of row 0 in these functions ??
# - Because the first line shows what information is contained in each line

# Function to prime the species database
# species.csv contains the species of birds (about 400)
def prime_species():
    if db(db.species).isempty():
        with open('/csvfiles/species.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                db.species.insert(specie=row[0])

# Function to prime the checklists database
# checklists.csv contains the checklists
def prime_checklist():
    if db(db.checklists).isempty():
        with open('/csvfiles/checklists.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                parsed_line = row[0].split(',')
                db.checklists.insert(
                    sei=parsed_line[0],
                    latitude=parsed_line[1],
                    longitude=parsed_line[2],
                    date=parsed_line[3],
                    time=parsed_line[4],
                    observer_id=parsed_line[5],
                    duation=parsed_line[6]
                )

# Function to prime the sightings database
# sightings.csv contains the sightings
# Each sighting has a checklist, a species, and a number of birds seen.
def prime_sightings():
    if db(db.sightings).isempty():
        with open('/csvfiles/sightings.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                parsed_line = row[0].split(',')
                db.sightings.insert(
                    sei=parsed_line[0],
                    specie=parsed_line[1],
                    count=parsed_line[2],
                )

# -------------------------- DATABASES -------------------------- #

### SPECIES DATABASE ###
# COMMON NAME
db.define_table('species',
    Field('specie')        # SPECIE - common name of the specie
)

### CHECKLIST DATABASE ###
# SAMPLING EVENT IDENTIFIER,LATITUDE,LONGITUDE,OBSERVATION DATE,TIME OBSERVATIONS STARTED,OBSERVER ID,DURATION MINUTES
db.define_table('checklists',
    Field('sei'),           # SAMPLING EVENT IDENTIFIER - connects checklist & sightings
    Field('latitude'),      # LATITUDE - latitude of sighting
    Field('longitude'),     # LONGITUDE - longitude of sighting
    Field('date'),          # DATE - observation date
    Field('time'),          # TIME - time observations started
    Field('observer_id'),   # OBSERVER_ID - observer ID, from checklist.csv
    Field('duration'),      # DURATION - duration of minutes of observations
    Field('user_id')        # USER_ID - ID of user account, user needs to be logged in to enter a checklist and access personal checklist page
)

### SIGHTINGS DATABASE ###
# SAMPLING EVENT IDENTIFIER,COMMON NAME,OBSERVATION COUNT
db.define_table('sightings',
    Field('sei'),           # SAMPLING EVENT IDENTIFIER - connects checklist & sightings
    Field('specie'),        # SPECIE - common name of the specie
    Field('count'),         # COUNT - observation count
    Field('favorite'),      # FAVORITE - our creative addition, whether it's a favorite of the user :)
)

## always commit your models to avoid problems later

db.commit()
