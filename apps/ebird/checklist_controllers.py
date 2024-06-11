from .controllers import *

@action('checklist', method=['POST', 'GET'])
@action.uses('checklist.html', session, db, auth.user)
def checklist(): 
    return dict(
            my_callback_url = URL('my_callback', signer=url_signer),
            checklist_url = URL('checklist', signer=url_signer)
            )

