from flask import Blueprint, flash, redirect, render_template, url_for, request, abort
from Doctors.form import *
from models import *
from flask_login import login_user, login_required,logout_user,current_user
import random, datetime

doctors = Blueprint('doctors', __name__)

@doctors.route("/doctor-signup", methods=["POST", "GET"])
def doctor_register():
  form = doctor_registration()
  try:
    if form.validate_on_submit():
      user = Doctors (
        doctor_id = random.randint(100000,999999),
        first_name = form.first_name.data,
        second_name = form.second_name.data,
        last_name = form.last_name.data,
        age = form.age.data,
        email = form.email_address.data,
        phone = form.phone_number.data,
        address = form.address.data,
        address2 = form.address1.data,
        date = datetime.datetime.now(),
        passwords = form.password.data,
        account_type = "doctor"
      )
      db.session.add(user)
      db.session.commit()
      flash(f"Account successfully created", category="success")
      return redirect(url_for('doctors.doctor_signin'))

    if form.errors != {}:
      for err_msg in form.errors.values():
        flash(f"There was an error creating the user: {err_msg}", category="danger")
  except:
    flash(f"An error occurred when submitting the form. Check the from and try again", category="danger")
    
  return render_template("doctor_signup.html", form=form)

@doctors.route("/doctor-signin", methods=["POST", "GET"])
def doctor_signin():
  form = login()
  if form.validate_on_submit():
    doctor = Doctors.query.filter_by(email=form.email.data).first()
    if doctor is None:
      flash(f"No user with that email", category="danger")
    elif doctor and doctor.check_password_correction(attempted_password=form.password.data):
      login_user(doctor, remember=True)
      flash(f"Login successfull, welcome doctor {current_user.first_name} {current_user.second_name}", category="success")
      next = request.args.get("next")
      return redirect(next or url_for("doctors.doctor_portal"))
    else:
      flash(f"Invalid Login Credentials", category="danger")

  return render_template("doctor_signin.html", form=form)

@doctors.route("/doctor-portal")
@login_required
def doctor_portal():
  if current_user.account_type != "doctor":
    abort(403)
  session = Session.query.filter_by(doctor=current_user.id, status="Active").first()
  appointments = Appointment.query.all()  
  appointmentz = Appointment.query.filter_by(doctor=current_user.id, status="Closed").all()
  sessionz = Session.query.filter_by(doctor=current_user.id, status="Closed").all()
  patients = Patients.query.all()
  medicines = Medicine.query.all()
  transactions = Transaction.query.all()

  return render_template("doctor_portal.html", session=session, appointments=appointments, appointmentz=appointmentz, patients=patients, medicines=medicines, transactions=transactions, sessionz=sessionz)

@doctors.route("/doctor-patient-session/<int:session_id>")
@login_required
def doctor_session(session_id):
  if current_user.account_type != "doctor":
    abort(403)
  session = Session.query.get(session_id)
  if session:
    appointment = Appointment.query.filter_by(id=session.appointment).first()
    patient = Patients.query.filter_by(id=session.patient).first()
  else:
    abort(404)
  medicines = Medicine.query.all()
  appointments = Appointment.query.all()
  doctors = Doctors.query.all()

  return render_template("doctor_session.html", session=session, appointment=appointment, patient=patient, medicines=medicines, appointments=appointments, doctors=doctors)

@doctors.route("/patient-diagnosis/<int:session_id>", methods=["POST", "GET"])
@login_required
def diagnosis(session_id):
  if current_user.account_type != "doctor":
    abort(403)
  session = Session.query.get(session_id)
  diagnosis = request.form.get("diagnosis")
  session.diagnosis = diagnosis
  db.session.commit()
  flash(f"Diagnosis updated successfully, patient will be alerted", category="success")
  
  return redirect(url_for('doctors.doctor_session', session_id=session.id))

@doctors.route("/patient-prescription/<int:session_id>", methods=["POST", "GET"])
@login_required
def prescription(session_id):
  if current_user.account_type != "doctor":
    abort(403)
  session = Session.query.get(session_id)
  new_prescription = Prescription (
    medicine = request.form.get("drug"),
    session = session.id,
    patient = session.patient,
    doctor = session.doctor,
    dose = request.form.get("dose"),
    frequency = request.form.get("frequency"),
    date = datetime.datetime.now(),
    status = "Active"
  )
  db.session.add(new_prescription)
  db.session.commit()
  flash(f"Prescription added successfully", category="success")

  return redirect(url_for('doctors.doctor_session', session_id=session.id))

@doctors.route("/patient-notes/<int:session_id>", methods=["POST", "GET"])
@login_required
def notes(session_id):
  if current_user.account_type != "doctor":
    abort(403)
  session = Session.query.get(session_id)
  session.notes = request.form.get("notes")
  db.session.commit()
  flash(f"Additional notes sent successfully", category="success")

  return redirect(url_for('doctors.doctor_session', session_id=session.id))

@doctors.route("/patient-vitals/<int:session_id>", methods=["POST", "GET"])
@login_required
def patient_vitals(session_id):
  if current_user.account_type != "doctor":
    abort(403)
  session = Session.query.get(session_id)
  patient = Patients.query.filter_by(id=session.patient).first()
  if patient.age > 18:
    if int(request.form.get("blood_pressure")) < 100 or int(request.form.get("blood_pressure")) > 150:
      flash(f"Patient's blood pressure is abnormal, recommend retest", category="danger")
      return redirect(url_for('doctors.doctor_session', session_id=session.id))
    elif int(request.form.get("weight")) < 50 or int(request.form.get("weight")) > 100:
      flash(f"Patient's weight is abnormal, recommend retest", category="danger")
      return redirect(url_for('doctors.doctor_session', session_id=session.id))
    elif int(request.form.get("height")) < 165 or int(request.form.get("height")) > 500:
      flash(f"Patient's height is abnormal, recommend retest", category="danger")
      return redirect(url_for('doctors.doctor_session', session_id=session.id))
    elif patient.age < 18:
      if int(request.form.get("blood_pressure")) < 60 or int(request.form.get("blood_pressure")) > 80:
        flash(f"Patient's blood pressure is abnormal, recommend retest", category="danger")
        return redirect(url_for('doctors.doctor_session', session_id=session.id))
      elif int(request.form.get("weight")) < 40 or int(request.form.get("weight")) > 80:
        flash(f"Patient's weight is abnormal, recommend retest", category="danger")
        return redirect(url_for('doctors.doctor_session', session_id=session.id))
      elif int(request.form.get("height")) < 50 or int(request.form.get("height")) > 164:
        flash(f"Patient's height is abnormal, recommend retest", category="danger")
        return redirect(url_for('doctors.doctor_session', session_id=session.id))
  patient.blood_pressure = request.form.get("blood_pressure")
  patient.weight = request.form.get("weight")
  patient.height = request.form.get("height")
  db.session.commit()
  flash(f"Patient's vitals updated successfully", category="success")

  return redirect(url_for('doctors.doctor_session', session_id=session.id))

@doctors.route("/blood-test/<int:session_id>")
@login_required
def blood_test(session_id):
  if current_user.account_type != "doctor":
    abort(403)
  session = Session.query.get(session_id)
  blood_groups = ["A-", "A+", "B-", "B+", "O-", "O+", "AB-", "AB+"]
  result = random.choice(blood_groups)
  new_test = Tests(
    test_id = random.randint(100000, 999999),
    name = "Blood Test",
    sample = "Blood Sample",
    result = result,
    date = datetime.datetime.now(),
    session = session.id,
    doctor = current_user.id,
    patient = session.patient,
    status = "Success"
  )
  db.session.add(new_test)
  db.session.commit()
  patient = Patients.query.filter_by(id=session.patient).first()
  patient.blood_type = result
  db.session.commit()
  
  return render_template("test.html", new_test=new_test), {"Refresh": f"2; url=http://127.0.0.1:5000/doctor-patient-session/{session.id}"}

@doctors.route("/add-new-medicine", methods=["POST", "GET"])
@login_required
def add_medicine():
  if current_user.account_type != "doctor":
    abort(403)
  try:
    new_medicine = Medicine (
      name = request.form.get("name"),
      type = request.form.get("type"),
      treatment = request.form.get("treatment"),
      price = request.form.get("price")
    )
    db.session.add(new_medicine)
    db.session.commit()
    flash(f"Medicine added successfully", category="success")
  except:
    flash(f"An error occured, try again", category="danger")

  return redirect(url_for('doctors.doctor_portal'))

@doctors.route("/doctor-logout")
@login_required
def doctor_logout():
  if current_user.account_type != "doctor":
    abort(403)
  logout_user()
  flash(f"Logged out successfully", category="success")
  return redirect(url_for('doctors.doctor_signin'))
