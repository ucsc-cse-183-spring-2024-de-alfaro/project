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
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.grid import Grid, GridClassStyleBulma

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth, url_signer)
def index():
    return dict(
        # COMPLETE: return here any signed URLs you need.
        my_callback_url = URL('my_callback', signer=url_signer),
        get_heatmap_data_url = URL('get_heatmap_data', signer=url_signer),  # Add this line
        checklist_url = URL('checklist', signer=url_signer),
    )

@action('my_callback')
@action.uses() # Add here things like db, auth, etc.
def my_callback():
    # The return value should be a dictionary that will be sent as JSON.
    return dict(my_value=3)

# -------------------------- LOCATION PAGE FUNCTIONS -------------------------- #

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
    

# -------------------------- CHECKLIST and MY_CHECKLIST PAGE FUNCTIONS -------------------------- #
@action('checklist', method=['POST', 'GET'])
@action.uses('checklist.html', session, db, auth.user, url_signer)
def checklist(): 
    return dict(
            checklist_url = URL('checklist', signer=url_signer),
            my_checklist_url = URL('my_checklist', signer=url_signer),
            load_checklists_url = URL('load_checklists'),
            search_species_url = URL('search'),
            inc_count_url = URL('inc_count')
            )

@action('my_checklist', method=['POST', 'GET'])
@action.uses('my_checklist.html', session, db, auth.user, url_signer)
def my_checklist(): 
    return dict(
            my_checklist_url = URL('my_checklist', signer=url_signer),
            checklist_url = URL('checklist', signer=url_signer),
            load_checklists_url = URL('load_checklists'),
            load_user_checklists_url = URL('load_user_checklists'),
            )   

@action('load_user_checklists')
@action.uses(db, session, auth.user)
def load_user_checklists():
    user_checklists = db(db.sightings.user_email == get_user_email()).select().as_list()
    return dict(data=user_checklists)
                
@action('load_checklists')
@action.uses(db, session, auth.user)
def load_checklists(): 
    checklist_table_data = db(db.checklist_data).select().as_list()
    return dict(data=checklist_table_data)

@action('inc_count', method='POST') 
@action.uses(db, session, auth.user)
def inc_count(): 
    # Get the count and id from the request
    count = request.json.get('count')
    id = request.json.get('id')
    specie=request.json.get('specie')
    
    # Add observation to sightings table
    # Figure out how to do SEI for new sightings
    db.sightings.insert(specie=specie, count=count, user_email=get_user_email())
    # sighting_id = db.sightings.insert(specie=specie, count=count, user_email=get_user_email())
    # print("sightings entry: ", db(db.sightings.id == sighting_id).select().first())      
    
    # Update data for checklist table displayed on server side
    specie = db(db.checklist_data.id == id).select().first()
    specie.total_count += count; 
    specie.update_record()
    return dict(total=specie.total_count)

@action('search')
@action.uses(db, session, auth.user)
def search(): 
    q = request.params.get('q')
    results = db(db.checklist_data.specie.like(f"%{q}%")).select(db.checklist_data.specie,
                                db.checklist_data.total_count, 
                                groupby=db.checklist_data.specie).as_list()
    return dict(results=results)
# ----------------------------------------------------------------------------- #


    


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
        species_list = db(db.sightings).select(db.sightings.specie, distinct=True).as_list()
        
        # Count the number of sightings for each species
        for species in species_list:
            species['sightings'] = db(db.sightings.specie == species['specie']).count()
            
        #print(species_list)
        return dict(speciesList=species_list)
    except Exception as e:
        logger.error(f"Error fetching species list: {str(e)}")
        return dict(error=str(e))
    

@action('api/get_top_contributors', method=['GET', 'POST'])
@action.uses(db)
def get_top_contributors():
    try:
        # Query to count the number of checklists per observer
        query = """
            SELECT observer_id, COUNT(*) as sighting_count
            FROM checklists
            GROUP BY observer_id
            ORDER BY sighting_count DESC
            LIMIT 10;  -- Limit to top 10 contributors
        """
        top_contributors = db.executesql(query, as_dict=True)

        return dict(topContributors=top_contributors)
    except Exception as e:
        logger.error(f"Error fetching top contributors: {str(e)}")
        return dict(error=str(e))
    
# -------------------------- STATISTICS PAGE FUNCTIONS -------------------------- #
@action('stats', method=['POST', 'GET'])
@action('stats/<path:path>', method=['POST', 'GET'])
@action.uses('stats.html', db, session, auth.user)
def stats(path=None):
    
    grid = Grid(path,
        formstyle=FormStyleBulma,
        grid_class_style=GridClassStyleBulma,
        query=(db.sightings.id > 0),
        orderby=[db.sightings.specie],
        search_queries=[['Search by Name', lambda val: db.sightings.specie.contains(val)]])
    return dict(grid=grid)

