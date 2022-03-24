from flask import Blueprint, flash, redirect, render_template, url_for, request, abort
from Doctors.form import *
from models import *
from twilio.rest import Client
from sendgrid.helpers.mail import Mail, Email, To, Content
from flask_login import login_user, login_required,logout_user,current_user
import random, datetime, sendgrid
import os

doctors = Blueprint('doctors', __name__)

account_sid = os.environ['Twilio_account_sid']
auth_token = os.environ['Twilio_auth_key']
clients = Client(account_sid, auth_token)
sg = sendgrid.SendGridAPIClient(api_key=os.environ['Email_api_key'])
from_email = Email("kevinkagwima4@gmail.com")
subject = "From PHMS team"

@doctors.route("/doctor-signup", methods=["POST", "GET"])
def doctor_register():
  form = doctor_registration()
  try:
    if form.validate_on_submit():
      doctor = Doctors (
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
      db.session.add(doctor)
      db.session.commit()
      flash(f"Account successfully created", category="success")
      try:
        to_email = To(f"kevokagwima@gmail.com, {current_user.email}")
        content = Content("text/plain", f"'Congratulations! {doctor.first_name} {doctor.second_name} you have successfully created a doctor account. Your doctor ID is {doctor.doctor_id}. Login to your portal with your email and password.")
        mail = Mail(from_email, to_email, subject, content)
        mail_json = mail.get()
        response = sg.client.mail.send.post(request_body=mail_json)
        print(response.headers)
      except:
        flash(f"Failed to send an email", category="danger")
      # try:
      #   clients.messages.create(
      #     to = '+254796897011',
      #     from_ = '+16203191736',
      #     body = f'Congratulations! {doctor.first_name} {doctor.second_name} you have successfully created a doctor account. Your doctor ID is {doctor.doctor_id}. Login to your portal with your email and password.'
      #   )
      # except:
      #   flash(f"Failed to send sms", category="danger")
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
  if session and session.doctor == current_user.id:
    appointment = Appointment.query.filter_by(id=session.appointment).first()
    patient = Patients.query.filter_by(id=session.patient).first()
  else:
    return redirect(url_for('doctors.session_access', session_id=session.id))
  medicines = Medicine.query.all()
  appointments = Appointment.query.all()
  doctors = Doctors.query.all()

  return render_template("doctor_session.html", session=session, appointment=appointment, patient=patient, medicines=medicines, appointments=appointments, doctors=doctors)

@doctors.route("/special-session-access/<int:session_id>", methods=["POST", "GET"])
@login_required
def session_access(session_id):
  if current_user.account_type != "doctor":
    abort(403)
  session = Session.query.get(session_id)

  return render_template("access.html", session=session)

@doctors.route("/verifying-session-id/<int:session_id>", methods=["POST", "GET"])
@login_required
def verify_access(session_id):
  if current_user.account_type != "doctor":
    abort(403)
  session = Session.query.get(session_id)
  form_session = request.form.get("numbers")
  if int(form_session) == session.session_id:
    flash(f"Session ID verified successfully", category="success")
    return redirect(url_for('doctors.doctor_special_session', session_id=session.id))
  else:
    flash(f"The session ID entered is invalid", category="danger")
    return redirect(url_for('doctors.session_access', session_id=session.id))

@doctors.route("/special-doctor-patient-session/<int:session_id>")
@login_required
def doctor_special_session(session_id):
  if current_user.account_type != "doctor":
    abort(403)
  session = Session.query.get(session_id)
  if session:
    appointment = Appointment.query.filter_by(id=session.appointment).first()
    patient = Patients.query.filter_by(id=session.patient).first()
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
  diagnosis = request.form.get("diagnosis").capitalize()
  session.diagnosis = diagnosis
  db.session.commit()
  flash(f"Diagnosis updated successfully, patient will be alerted", category="success")
  
  return redirect(url_for('doctors.doctor_session', session_id=session.id))

@doctors.route("/review-patient-diagnosis/<int:session_id>", methods=["POST", "GET"])
@login_required
def review_diagnosis(session_id):
  if current_user.account_type != "doctor":
    abort(403)
  session = Session.query.get(session_id)
  if session:
    session.diagnosis = None
    db.session.commit()
    flash(f"Diagnosis successfully reviewed", category="success")

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

@doctors.route("/remove-patient-prescription/<int:session_id>/<int:prescription_id>", methods=["POST", "GET"])
@login_required
def remove_prescription(session_id, prescription_id):
  if current_user.account_type != "doctor":
    abort(403)
  session = Session.query.get(session_id)
  prescription = Prescription.query.get(prescription_id)
  db.session.delete(prescription)
  db.session.commit()
  flash(f"Prescription removed successfully", category="success")

  return redirect(url_for('doctors.doctor_session', session_id=session.id))

@doctors.route("/patient-notes/<int:session_id>", methods=["POST", "GET"])
@login_required
def notes(session_id):
  if current_user.account_type != "doctor":
    abort(403)
  session = Session.query.get(session_id)
  prescriptions = Prescription.query.filter_by(session=session.id).all()
  presc = ''
  for prescription in prescriptions:
    medicine = Medicine.query.filter_by(id=prescription.medicine).first()
    presc += medicine.name + f'({medicine.type})' + " " + prescription.dose + '*' + str(prescription.frequency) + '\n'
  session.notes = request.form.get("notes")
  db.session.commit()
  flash(f"Additional notes sent successfully", category="success")
  try:
    to_email = To(f"kevokagwima@gmail.com, {current_user.email}")
    content = Content("text/plain", f"Your session with Dr. {current_user.first_name} {current_user.second_name} is coming to an end. Details for this session include:\nDiagnosis - {session.diagnosis}\nPrescriptions:\n{presc}\nAdditional notes - {session.notes}")
    mail = Mail(from_email, to_email, subject, content)
    mail_json = mail.get()
    response = sg.client.mail.send.post(request_body=mail_json)
    print(response.headers)
  except:
    flash(f"Failed to send an email", category="danger")
  # try:
  #   clients.messages.create(
  #     to = '+254796897011',
  #     from_ = '+16203191736',
  #     body = f"Your session with Dr. {current_user.first_name} {current_user.second_name} is coming to an end. Details for this session include:\nDiagnosis - {session.diagnosis}\nPrescriptions:\n{presc}\nAdditional notes - {session.notes}"
  #   )
  # except:
  #   flash(f"Failed to send sms", category="danger")

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
  # try:
  #   clients.messages.create(
  #     to = '+254796897011',
  #     from_ = '+16203191736',
  #     body = f"Dear {patient.first_name} {patient.second_name}, your vitals have been successfully updated. Login into your dashboard to view your latest medical data."
  #   )
  # except:
  #   flash(f"Failed to send sms", category="danger")

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
  # try:
  #   clients.messages.create(
  #     to = '+254796897011',
  #     from_ = '+16203191736',
  #     body = f"Dear patient, your blood test has been successfully tested. Result from the test indicate your blood group is {new_test.result}.Login into your portal to view your latest medical data."
  #   )
  # except:
  #   flash(f"Failed to send sms", category="danger")
  
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
