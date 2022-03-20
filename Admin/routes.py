from flask import Blueprint, flash, redirect, render_template, url_for, request, abort
from Admin.form import *
from models import *
from twilio.rest import Client
from flask_login import login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import random
from datetime import datetime
import os

admin = Blueprint('admin', __name__)

bcrypt = Bcrypt()
account_sid = os.environ['Twilio_account_sid']
auth_token = os.environ['Twilio_auth_key']
clients = Client(account_sid, auth_token)

@admin.route("/admin-signin", methods=["POST", "GET"])
def admin_signin():
  form = login()
  if form.validate_on_submit():
    admin = Admin.query.filter_by(email=form.email.data).first()
    if admin is None:
      flash(f"No user with that email", category="danger")
    elif admin and admin.check_password_correction(attempted_password=form.password.data):
      login_user(admin, remember=True)
      flash(f"Login successfull, welcome {current_user.username}", category="success")
      next = request.args.get("next")
      return redirect(next or url_for("admin.admin_portal"))
    else:
      flash(f"Invalid Login Credentials", category="danger")

  return render_template("admin_signin.html", form=form)

@admin.route("/admin-portal")
@login_required
def admin_portal():
  if current_user.account_type != "admin":
    abort(403)

  patients = Patients.query.all()
  doctors = Doctors.query.all()
  appointments = Appointment.query.all()
  sessions = Session.query.all()
  prescriptions = Prescription.query.all()
  transactions = Transaction.query.all()
  medicines = Medicine.query.all()
  symptoms = Symptoms.query.all()

  return render_template("admin.html", patients=patients, doctors=doctors, appointments=appointments, sessions=sessions, prescriptions=prescriptions, transactions=transactions, medicines=medicines, symptoms=symptoms)

@admin.route("/remove-user/<int:user_id>")
@login_required
def remove_user(user_id):
  patient = Patients.query.filter_by(patient_id=user_id).first()
  doctor = Doctors.query.filter_by(doctor_id=user_id).first()
  if patient or doctor:
    db.session.delete(patient or doctor)
    db.session.commit()
    if patient:
      flash(f"Patient {patient.first_name} {patient.second_name}'s account has been deleted successfully", category="success")
      # try:
      #   clients.messages.create(
      #     to = '+254796897011',
      #     from_ = '+16203191736',
      #     body = f"Dear {patient.first_name} {patient.second_name}, your patient account has been deleted permanently."
      #   )
      # except:
      #   flash(f"Failed to send sms", category="danger")
    elif doctor:
      flash(f"Doctor {doctor.first_name} {doctor.second_name}'s account has been deleted successfully", category="success")
      # try:
      #   clients.messages.create(
      #     to = '+254796897011',
      #     from_ = '+16203191736',
      #     body = f"Dear {doctor.first_name} {doctor.second_name}, your dctor account has been deleted permanently."
      #   )
      # except:
      #   flash(f"Failed to send sms", category="danger")
  else:
    flash(f"User not found", category="danger")
  
  return redirect(url_for('admin.admin_portal'))

@admin.route("/Add-new-patient", methods=["POST", "GET"])
def add_patient():
  try:
    password = bcrypt.generate_password_hash("11111").decode("utf-8")
    patient = Patients(
      patient_id = random.randint(100000, 999999),
      first_name = request.form.get("fname"),
      second_name = request.form.get("sname"),
      last_name = request.form.get("lname"),
      age = request.form.get('age'),
      email = request.form.get("email"),
      phone = request.form.get("phone"),
      address = request.form.get("address1"),
      address2 = request.form.get("address2"),
      date = datetime.now(),
      password = password, 
      account_type = "patient"
    )
    db.session.add(patient)
    db.session.commit()
    flash(f"New patient added successfully", category="success")
    # try:
    #   clients.messages.create(
    #     to = '+254796897011',
    #     from_ = '+16203191736',
    #     body = f'Congratulations! {patient.first_name} {patient.second_name} you have successfully created a patient account. Your patient ID is {patient.patient_id}. Login to your portal with your email and password.'
    #     )
    # except:
    #   flash(f"Failed to send sms", category="danger")
    return redirect(url_for('admin.admin_portal'))
  
  except:
    flash(f"An error occured, try again", category="danger")
    return redirect(url_for('admin.admin_portal'))

@admin.route("/Add-new-doctor", methods=["POST", "GET"])
def add_doctor():
  try:
    password = bcrypt.generate_password_hash("11111").decode("utf-8")
    doctor = Doctors(
      doctor_id = random.randint(100000, 999999),
      first_name = request.form.get("fname"),
      second_name = request.form.get("sname"),
      last_name = request.form.get("lname"),
      age = request.form.get('age'),
      email = request.form.get("email"),
      phone = request.form.get("phone"),
      address = request.form.get("address1"),
      address2 = request.form.get("address2"),
      date = datetime.now(),
      password = password, 
      account_type = "doctor"
    )
    db.session.add(doctor)
    db.session.commit()
    flash(f"New doctor added successfully", category="success")
    # try:
    #   clients.messages.create(
    #     to = '+254796897011',
    #     from_ = '+16203191736',
    #     body = f'Congratulations! {doctor.first_name} {doctor.second_name} you have successfully created a doctor account. Your doctor ID is {doctor.doctor_id}. Login to your portal with your email and password.'
    #   )
    # except:
    #   flash(f"Failed to send sms", category="danger")
    return redirect(url_for('admin.admin_portal'))
  
  except:
    flash(f"An error occured, try again", category="danger")
    return redirect(url_for('admin.admin_portal'))

@admin.route("/admin-logout")
@login_required
def admin_logout():
  if current_user.account_type != "admin":
    abort(403)
  logout_user()
  flash(f"Logged out successfully", category="success")
  return redirect(url_for('admin.admin_signin'))
