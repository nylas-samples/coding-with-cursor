import os
from functools import wraps

from utils.mock_db import db

from io import BytesIO
from flask import Flask, request, send_file, g
from flask_cors import CORS

from nylas import APIClient
from nylas.client.restful_models import Webhook
from nylas.services.tunnel import open_webhook_tunnel


# Initialize the Nylas API client using the client id and secret specified in the .env file
nylas = APIClient(
    os.environ.get("NYLAS_CLIENT_ID"),
    os.environ.get("NYLAS_CLIENT_SECRET"),
    api_server = os.environ.get("NYLAS_API_SERVER") or "https://api.nylas.com"
)

# Before we start our backend, we should register our frontend
# as a redirect URI to ensure the auth completes
CLIENT_URI = 'http://localhost:3000'
updated_application_details = nylas.update_application_details(redirect_uris=[CLIENT_URI])
print('Application registered. Application Details: ', updated_application_details)

def run_webhook():
    """
    Run a webhook to receive real-time updates from the Nylas API.
    In this example, webhook open and error events and the messages received from the API are printed to the console.
    """
    def on_message(delta):
        """
        Raw webhook messages are parsed in the Nylas SDK and sent to this function as a delta
        """

        # Trigger logic on any webhook trigger Enum
        if delta["type"] == Webhook.Trigger.ACCOUNT_CONNECTED:
            print(delta)

    def on_open(ws):
        print("webhook tunnel opened")

    def on_error(ws, err):
        print("Error found")
        print(err)

    open_webhook_tunnel(
        nylas, {'on_message': on_message, 'on_open': on_open, 'on_error': on_error})


# Run the webhook
run_webhook()

# Initialize the Flask app
flask_app = Flask(__name__)

# Enable CORS for the Flask app
CORS(flask_app, supports_credentials=True)


@flask_app.route("/nylas/generate-auth-url", methods=["POST"])
def build_auth_url():
    """
    Generates a Nylas Hosted Authentication URL with the given arguments. 
    The endpoint also uses the app level constant CLIENT_URI to build the URL.

    This endpoint is a POST request and accepts the following parameters in the request body:
        success_url: The URL to redirect the user to after successful authorization.
        email_address: The email address of the user who is authorizing the app.

    Returns the generated authorization URL.
    """

    request_body = request.get_json()

    # Use the SDK method to generate a Nylas Hosted Authentication URL
    auth_url = nylas.authentication_url(
        (CLIENT_URI or "") + request_body["success_url"],
        login_hint=request_body["email_address"],
        scopes=['email.modify'],
        state=None,
    )

    return auth_url


@flask_app.route("/nylas/exchange-mailbox-token", methods=["POST"])
def exchange_code_for_token():
    """
    Exchanges an authorization code for an access token. 
    Once the access token is generated, it can be used to make API calls on behalf of the user. 
    For this example, we store the access token in our mock database.

    This endpoint is a POST request and accepts the following parameters: 
    
    Request Body:
        token: The authorization code generated by the Nylas Hosted Authentication.

    Returns a JSON object with the following information about the user:
        id: The identifier of the user in the database.
        emailAddress: The email address of the user.
    """

    request_body = request.get_json()

    # Use the SDK method to exchange our authorization code for an access token with the Nylas API
    access_token_obj = nylas.send_authorization(request_body["token"])

    # process the result and send to client however you want
    access_token = access_token_obj['access_token']
    email_address = access_token_obj['email_address']

    print('Access Token was generated for: ' + email_address)

    user = db.create_or_update_user(email_address, {
        'access_token': access_token,
        'email_address': email_address
    })

    return {
        'id': user['id'],
        'emailAddress': user['email_address']
    }


def is_authenticated(f):
    """
    A decorator that checks if the user is authenticated. 
    If the user is authenticated, the decorator sets the user's access token and returns the decorated function. 
    If the user is not authenticated, the decorator returns a 401 error. 

    This decorator is used for any endpoint that requires an access token to call the Nylas API.
    """

    @wraps(f)
    def decorator(*args, **kwargs):
        auth_headers = request.headers.get('Authorization')
        if not auth_headers:
            return 401

        # Find the user in the mock database
        user = db.find_user(auth_headers)
        if not user:
            return 401

        # Set the access token for the Nylas API client
        nylas.access_token = user['access_token']

        # Set the user in the Flask global object
        g.user = user

        return f(*args, **kwargs)
    return decorator


@flask_app.after_request
def after_request(response):
    """
    After request middleware that clear the Nylas access token after each request.
    """

    nylas.access_token = None

    return response


@flask_app.route('/nylas/read-emails', methods=['GET'])
@is_authenticated
def read_emails():
    """
    Retrieve the first 20 threads of the authenticated account from the Nylas API.

    This endpoint is a GET request and accepts no parameters.

    The threads are retrieved using the Nylas API client, with the view set to "expanded".

    The threads are then returned as a JSON object.
    See our docs for more information about the thread object.
    https://developer.nylas.com/docs/api/#tag--Threads
    """

    # where() sets the query parameters for the request
    # all() executes the request and return the results
    res = nylas.threads.where(limit=5, view="expanded").all()

    # enforce_read_only=False is used to return the full thread objects
    res_json = [item.as_json(enforce_read_only=False) for item in res]

    return res_json


@flask_app.route('/nylas/message', methods=['GET'])
@is_authenticated
def get_message():
    """
    Retrieve a message from the Nylas API.

    This endpoint is a GET request and accepts the following:
    
    Query Parameters:
        'id': The identifier of the message to retrieve.

    The message is retrieved using the Nylas API client by id, with the view set to "expanded".

    The message is then returned as a JSON object.
    See our docs for more information about the message object.
    https://developer.nylas.com/docs/api/#tag--Messages
    """

    message_id = request.args.get('id')

    # where() sets the query parameters for the request
    # get() executes the request and return the results
    message = nylas.messages.where(view="expanded").get(message_id)

    # enforce_read_only=False is used to return the full message object
    return message.as_json(enforce_read_only=False)


@flask_app.route('/nylas/file', methods=['GET'])
@is_authenticated
def download_file():
    """
    Retrieve and download a file from the Nylas API.

    This endpoint is a GET request and accepts the following:

    Query Parameters:
        id: The identifier of the file to download.

    The file metadata is retrieved using the Nylas API client.
    A second request is sent to the API and the file is downloaded.

    Returns the file with metadata to the client for download.

    See our docs for more information about the file object.
    https://developer.nylas.com/docs/api/#tag--Files
    """

    file_id = request.args.get('id')
    file_metadata = nylas.files.get(file_id)

    file = file_metadata.download()

    return send_file(BytesIO(file), download_name=file_metadata.filename, mimetype=file_metadata.content_type, as_attachment=True)

