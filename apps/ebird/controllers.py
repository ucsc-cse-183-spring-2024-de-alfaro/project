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
from .models import get_user_email, get_heatmap_data

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth, url_signer)
def index():
    return dict(
        my_callback_url = URL('my_callback', signer=url_signer),
        get_heatmap_data_url = URL('get_heatmap_data', signer=url_signer),  # Add this line
        checklist_url = URL('checklist', signer=url_signer),
    )

@action('my_callback')
@action.uses() # Add here things like db, auth, etc.
def my_callback():
    # The return value should be a dictionary that will be sent as JSON.
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
    
@action('checklist', method=['POST', 'GET'])
@action.uses('checklist.html', session, db, auth.user, url_signer)
def checklist(): 
    return dict(
            checklist_url = URL('checklist', signer=url_signer),
            load_checklists_url = URL('load_checklists'),
            search_species_url = URL('search'),
            )

# @action('load_checklists')
# @action.uses(db, session, auth.user)
# def load_checklists(): 
#     data = db(db.sightings).select(db.sightings.specie, db.sightings.count.sum().with_alias('total_count'), 
#                                groupby=db.sightings.specie).as_list()
#     return dict(data=data) 


@action('load_checklists')
@action.uses(db, session, auth.user)
def load_checklists(): 

    data = db(db.sightings).select(db.sightings.specie, db.sightings.count.sum().with_alias('total_count'), 
                                groupby=db.sightings.specie).as_list()
    for row in data:
        db.checklist_data.update_or_insert((db.checklist_data.specie == row['sightings']['specie']),
                                           specie=row['sightings']['specie'], total_count=row['total_count'])
    d = db(db.checklist_data).select().as_list()
    return dict(data=d)

# @action('add_checklist')
# @action.uses(db,session, auth.user)
# def add_checklist(): 


@action('search')
@action.uses(db, session, auth.user)
def search(): 
    q = request.params.get('q')
    results = db(db.checklist_data.specie.like(f"%{q}%")).select(db.checklist_data.specie,
                                db.checklist_data.total_count, 
                                groupby=db.checklist_data.specie).as_list()
    return dict(results=results)

