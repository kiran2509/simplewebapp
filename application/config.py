
import os


class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'\xbeV\xa6\xb6\x0b\xeb\x0f\xd3!\xc8\xa2\x11\xfa5\xccr'
    MONGODB_SETTINGS ={'db' : 'UTA_Enrollment'}