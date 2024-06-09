"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email

import json

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth, url_signer)
def index():
    return dict(
        # COMPLETE: return here any signed URLs you need.
        my_callback_url = URL('my_callback', signer=url_signer),
    )

@action('my_callback')
@action.uses() # Add here things like db, auth, etc.
def my_callback():
    # The return value should be a dictionary that will be sent as JSON.
    return dict(my_value=3)


@action('location',  method=['GET', 'POST'])
@action.uses('location.html', db, auth, url_signer)
def location():
    return dict(my_value=3)

@action('get_heatmap_data')
@action.uses(db, auth)
def get_heatmap_data_action():
    try:
        species = request.params.get('species', 'all')
        if species is None:
            species = 'all'
        logger.info(f"Received species: {species}")  # Log for debugging
        heatmap_data = get_heatmap_data(species)
        return dict(heatmap_data=heatmap_data)
    except Exception as e:
        logger.error(f"Error in get_heatmap_data_action: {str(e)}")  # Log for debugging
        response.status = 500
        return dict(error=str(e))
    


#Location Page 
@action('api/get_sightings', method=['GET', 'POST'])
@action.uses(db)
def get_sightings():
    species = request.params.get('species', 'American Robin')
    sightings = db(db.sightings.specie == species).select().as_list()
    
    # Debugging: print the species and sightings fetched
    #print(f"Species: {species}")
    #print("Sightings:", sightings)

    for sighting in sightings:
        sei_value = sighting['sei']
        checklist = db(db.checklists.sei == sei_value).select().first()

        # Debugging: check if the checklist is found and print its content
        if checklist:
            #print(f"Found checklist for SEI {sei_value}: {checklist}")
            sighting['date'] = checklist.date
        else:
            #print(f"No checklist found for SEI {sei_value}")
            sighting['date'] = None

    # Remove entries without a valid date
    sightings = [s for s in sightings if s['date']]
    #print("Processed sightings with dates:", sightings)

    return dict(sightings=sightings)

@action('api/get_species_list', method=['GET', 'POST'])
@action.uses(db)
def get_species_list():
    try:
        # Fetch distinct species from the sightings table
        species_list = db(db.sightings).select(db.sightings.specie).as_list()
        
        # Count the number of sightings for each species
        for species in species_list:
            species['sightings'] = db(db.sightings.specie == species['specie']).count()
            
        print(species_list)
        return dict(speciesList=species_list)
    except Exception as e:
        logger.error(f"Error fetching species list: {str(e)}")
        return dict(error=str(e))




