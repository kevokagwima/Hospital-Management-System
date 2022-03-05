import os

class Config:
  SQLALCHEMY_DATABASE_URI = ("mssql://@KEVINKAGWIMA/HMS?driver=SQL SERVER")
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SECRET_KEY = os.environ['Hms_secret_key']
