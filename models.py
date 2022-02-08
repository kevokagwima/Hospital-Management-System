from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

db = SQLAlchemy()
bcrypt = Bcrypt()

class Patients(db.Model, UserMixin):
  __tablename__ = "Patients"
  id = db.Column(db.Integer(), primary_key=True)
  patient_id = db.Column(db.Integer(), nullable=False)
  first_name = db.Column(db.String(length=50), nullable=False)
  second_name = db.Column(db.String(length=50), nullable=False)
  last_name = db.Column(db.String(length=50), nullable=False)
  age = db.Column(db.Integer(), nullable=False)
  email = db.Column(db.String(length=100), nullable=False)
  phone = db.Column(db.String(length=10), nullable=False)
  address = db.Column(db.String(20), nullable=False)
  address2 = db.Column(db.String(20), nullable=False)
  doctor = db.Column(db.Integer(), db.ForeignKey("Doctors.id"))
  appointment = db.relationship("Appointment", backref="doctor-appointment", lazy=True)
  blood_pressure = db.Column(db.Integer(), nullable=True)
  prescription = db.relationship("Prescription", backref="patient-prescription", lazy=True)
  height = db.Column(db.Integer(), nullable=True)
  weight = db.Column(db.Integer(), nullable=True)
  allergies = db.Column(db.String(length=100), nullable=True)
  date = db.Column(db.DateTime())
  password = db.Column(db.String(), nullable=False)
  account_type = db.Column(db.String(length=7), nullable=False)

  @property
  def passwords(self):
    return self.passwords

  @passwords.setter
  def passwords(self, plain_text_password):
    self.password = bcrypt.generate_password_hash(plain_text_password).decode("utf-8")

  def check_password_correction(self, attempted_password):
    return bcrypt.check_password_hash(self.password, attempted_password)

class Doctors(db.Model, UserMixin):
  __tablename__ = "Doctors"
  id = db.Column(db.Integer(), primary_key=True)
  doctor_id = db.Column(db.Integer(), nullable=False)
  first_name = db.Column(db.String(length=50), nullable=False)
  second_name = db.Column(db.String(length=50), nullable=False)
  last_name = db.Column(db.String(length=50), nullable=False)
  age = db.Column(db.Integer(), nullable=False)
  email = db.Column(db.String(length=100), nullable=False)
  phone = db.Column(db.String(length=10), nullable=False)
  address = db.Column(db.String(20), nullable=False)
  address2 = db.Column(db.String(20), nullable=False)
  patient = db.relationship("Patients", backref="patient", lazy=True)
  appointment = db.relationship("Appointment", backref="patient-appointment", lazy=True)
  prescription = db.relationship("Prescription", backref="doctor-prescription", lazy=True)
  date = db.Column(db.DateTime())
  password = db.Column(db.String(), nullable=False)
  account_type = db.Column(db.String(length=7), nullable=False)

  @property
  def passwords(self):
    return self.passwords

  @passwords.setter
  def passwords(self, plain_text_password):
    self.password = bcrypt.generate_password_hash(plain_text_password).decode("utf-8")

  def check_password_correction(self, attempted_password):
    return bcrypt.check_password_hash(self.password, attempted_password)

class Appointment(db.Model):
  __tablename__ = "Appointments"
  id = db.Column(db.Integer(), primary_key=True)
  appointment_id = db.Column(db.Integer(), nullable=False)
  name = db.Column(db.String(length=50), nullable=False)
  patient = db.Column(db.Integer(), db.ForeignKey("Patients.id"))
  doctor = db.Column(db.Integer(), db.ForeignKey("Doctors.id"))
  date_created = db.Column(db.DateTime(), nullable=False)
  session = db.relationship("Session", backref="session", lazy=True)
  date_closed = db.Column(db.DateTime(), nullable=True)
  status = db.Column(db.String(length=6), nullable=False)

class Session(db.Model):
  __tablename__ = 'Sessions'
  id = db.Column(db.Integer(), primary_key=True)
  session_id = db.Column(db.Integer(), nullable=False)
  appointment = db.Column(db.Integer(), db.ForeignKey("Appointments.id"))
  patient = db.Column(db.Integer(), db.ForeignKey("Patients.id"))
  doctor = db.Column(db.Integer(), db.ForeignKey("Doctors.id"))
  symptoms = db.Column(db.String(length=200), nullable=True)
  diagnosis = db.Column(db.String(length=100), nullable=True)
  prescription = db.relationship("Prescription", backref="session-prescription", lazy=True)
  notes = db.Column(db.String(length=200), nullable=True)
  cost = db.Column(db.Integer(), nullable=True)

class Medicine(db.Model):
  __tablename__ = 'Medicines'
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String(length=50), nullable=False)
  type = db.Column(db.String(length=10), nullable=False)
  treatment = db.Column(db.String(length=100), nullable=False)
  price = db.Column(db.Integer(), nullable=False)
  prescription = db.relationship("Prescription", backref="medicine-prescription", lazy=True)

class Prescription(db.Model):
  __tablename__ = 'Prescriptions'
  id = db.Column(db.Integer(), primary_key=True)
  medicine = db.Column(db.Integer(), db.ForeignKey("Medicines.id"))
  session = db.Column(db.Integer(), db.ForeignKey("Sessions.id"))
  patient = db.Column(db.Integer(), db.ForeignKey("Patients.id"))
  doctor = db.Column(db.Integer(), db.ForeignKey("Doctors.id"))
  dose = db.Column(db.String(length=10), nullable=False)
  frequency = db.Column(db.Integer(), nullable=False)
  date = db.Column(db.DateTime(), nullable=False)
