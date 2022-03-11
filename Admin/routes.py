from flask import Blueprint, flash, redirect, render_template, url_for, request, abort
from Admin.form import *
from models import *
from flask_login import login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import random
from datetime import datetime

admin = Blueprint('admin', __name__)
bcrypt = Bcrypt()

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
    elif doctor:
      flash(f"Doctor {doctor.first_name} {doctor.second_name}'s account has been deleted successfully", category="success")
  else:
    flash(f"User not found", category="danger")
  
  return redirect(url_for('admin.admin_portal'))

@admin.route("/Add-new-patient", methods=["POST", "GET"])
def add_patient():
  try:
    password = bcrypt.generate_password_hash("11111").decode("utf-8")
    new_patient = Patients(
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
    db.session.add(new_patient)
    db.session.commit()
    flash(f"New patient added successfully", category="success")
    return redirect(url_for('admin.admin_portal'))
  
  except:
    flash(f"An error occured, try again", category="danger")
    return redirect(url_for('admin.admin_portal'))

@admin.route("/Add-new-doctor", methods=["POST", "GET"])
def add_doctor():
  try:
    password = bcrypt.generate_password_hash("11111").decode("utf-8")
    new_patient = Doctors(
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
    db.session.add(new_patient)
    db.session.commit()
    flash(f"New doctor added successfully", category="success")
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
