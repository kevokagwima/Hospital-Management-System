from flask import Flask, abort
from Patients.routes import patients
from Doctors.routes import doctors
from Admin.routes import admin
from Main.routes import main
from Errors.handlers import errors
from models import *
from config import Config
from flask_login import login_manager, LoginManager

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
app.register_blueprint(patients)
app.register_blueprint(doctors)
app.register_blueprint(admin)
app.register_blueprint(main)
app.register_blueprint(errors)
login_manager = LoginManager()
login_manager.blueprint_login_views = {
  'patients': '/patient-signin',
  'doctors': '/doctor-signin',
  'admin' : '/admin-signin',
}
login_manager.login_message_category = "danger"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
  try:
    return Patients.query.filter_by(phone=user_id).first() or Doctors.query.filter_by(phone=user_id).first() or Admin.query.filter_by(phone=user_id).first()
  except:
    abort(500)

if __name__ == '__main__':
  app.run(debug=True)
