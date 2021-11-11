# File Management
import os # Operating system library
import pathlib # file paths

# ----------------------------------------------------------------------------
# CONFIG SETTINGS
# ----------------------------------------------------------------------------
DATA_PATH = pathlib.Path(__file__).parent.joinpath("data")
ASSETS_PATH = pathlib.Path(__file__).parent.joinpath("assets")
REQUESTS_PATHNAME_PREFIX = os.environ.get("REQUESTS_PATHNAME_PREFIX", "/")

# ----------------------------------------------------------------------------
# SECURITY FUNCTION
# ----------------------------------------------------------------------------
def get_django_user():
    """
    Utility function to retrieve logged in username
    from Django
    """
    DJANGO_LOGIN_API = os.environ.get("DJANGO_LOGIN_API", None)
    DJANGO_SESSION_COOKIE = os.environ.get("DJANGO_SESSION_COOKIE", None)
    try:
        if not DJANGO_LOGIN_API:
            return True
        if not DJANGO_SESSION_COOKIE:
            raise Exception("DJANGO_SESSION_COOKIE environment variable missing")
        if not request:
            raise Exception("Request context missing while trying to authorize user")
        session_id = request.cookies.get(DJANGO_SESSION_COOKIE)
        if not session_id:
            print("Request cookies: ", request.cookies)
            raise Exception("{cookie} cookie is missing".format(cookie=DJANGO_SESSION_COOKIE))
        api = "{django_login_api}".format(
            django_login_api=DJANGO_LOGIN_API
        )
        response = requests.get(
            api,
            headers = {
                'cookie': '{cookie}={session_id}'.format(
                    cookie=DJANGO_SESSION_COOKIE,
                    session_id=session_id
                )
            }
        )
        return response.json()
    except Exception as e:
        print(e)
        return None

# ----------------------------------------------------------------------------
# STYLING
# ----------------------------------------------------------------------------

TACC_IFRAME_SIZE = {
    "max-width" : "1060px", "max-height" : "980px" # THESE ARE SET TO FIT IN THE 1080x1000 TACC iFRAME.  CAN BE REMOVED IF THOSE CONSTRAINTS COME OFF
}

CONTENT_STYLE = {
    "padding": "2rem 1rem",
    "font-family": 'Arial, Helvetica, sans-serif',
}

export_style = '''
    position:absolute;
    right:25px;
    bottom:-55px;
    font-family: Arial, Helvetica, sans-serif;
    margin: 10px;
    color: #fff;
    background-color: #17a2b8;
    border-color: #17a2b8;
    display: inline-block;
    font-weight: 400;
    text-align: center;
    white-space: nowrap;
    vertical-align: middle;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
    border: 1px solid transparent;
    padding: .375rem .75rem;
    font-size: 1rem;
    line-height: 1.5;
    border-radius: .25rem;
    transition: color .15s ease-in-out,background-color .15s ease-in-out,border-color .15s ease-in-out,box-shadow .15s ease-in-out;
'''
