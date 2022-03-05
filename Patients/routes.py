from flask import Blueprint, flash, redirect, render_template, url_for, request, make_response, jsonify
from Patients.form import *
from models import *
from flask_login import login_manager, LoginManager, login_user, login_required, logout_user, current_user
from twilio.rest import Client
import random, datetime, stripe, os

patients = Blueprint('patients', __name__)

login_manager = LoginManager()
login_manager.init_app(patients)
stripe.api_key = os.environ['Stripe_api_key']
account_sid = os.environ['Twilio_account_sid']
auth_token = os.environ['Twilio_auth_key']
clients = Client(account_sid, auth_token)

@patients.route("/patient-signup", methods=["POST", "GET"])
def patient_register():
  form = patient_registration()
  try:
    if form.validate_on_submit():
      patient = Patients (
        patient_id = random.randint(100000,999999),
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
        account_type = "patient"
      )
      db.session.add(patient)
      db.session.commit()
      flash(f"Account successfully created", category="success")
      return redirect(url_for('patients.patient_signin'))

    if form.errors != {}:
      for err_msg in form.errors.values():
        flash(f"There was an error creating the user: {err_msg}", category="danger")
  except:
    flash(f"An error occurred when submitting the form. Check the from and try again", category="danger")
  return render_template("patient_signup.html", form=form)

@patients.route("/patient-signin", methods=["POST", "GET"])
def patient_signin():
  form = login()
  if form.validate_on_submit():
    patient = Patients.query.filter_by(email=form.email.data).first()
    if patient is None:
      flash(f"No user with that email", category="danger")
    elif patient and patient.check_password_correction(attempted_password=form.password.data):
      login_user(patient, remember=True)
      flash(f"Login successfull, welcome {current_user.first_name} {current_user.second_name}", category="success")
      next = request.args.get("next")
      return redirect(next or url_for("patients.patient_portal"))
    else:
      flash(f"Invalid Login Credentials", category="danger")

  return render_template("signin.html", form=form)

@patients.route("/patient-portal")
@login_required
def patient_portal():
  if current_user.account_type != "patient":
    flash(f"Only patients are allowed", category="warning")
    return redirect(url_for('patients.patient_signin'))
  session = Session.query.filter_by(patient=current_user.id, status="Active").first()
  doctors = Doctors.query.all()
  appointments = Appointment.query.all()
  appointmentz = Appointment.query.filter_by(status="Closed").all()
  prescriptions = Prescription.query.filter_by(patient=current_user.id).all()
  transactions = Transaction.query.filter_by(patient=current_user.id).all()
  medicines = Medicine.query.all()
  
  return render_template("patient_portal.html", session=session, doctors=doctors, appointments=appointments, appointmentz=appointmentz, prescriptions=prescriptions, medicines=medicines, transactions=transactions)

@patients.route("/book-appointment", methods=["POST", "GET"])
@login_required
def book_appointment():
  if current_user.account_type != "patient":
    flash(f"Only patients are allowed", category="warning")
    return redirect(url_for('patients.patient_signin'))
  available_doctors = []
  doctors = Doctors.query.all()
  for doctor in doctors:
    appointment = Appointment.query.filter_by(doctor=doctor.id, status="Active").first()
    if appointment == None:
      available_doctors.append(doctor)
  if len(available_doctors) == 0:
    flash(f"Could not create appointment, no available doctors to assign", category="info")
    return redirect(url_for('patients.patient_portal'))
  random_doctor = random.choice(available_doctors)
  appointment = Appointment.query.filter_by(patient=current_user.id, status="Active").first()
  if appointment:
    flash(f"You have an active appointment, complete it before creating a new one", category="danger")
  else:
    new_appointment = Appointment (
      appointment_id = random.randint(100000,999999),
      name = "Doctor consultation",
      patient = current_user.id,
      doctor = random_doctor.id,
      date_created = datetime.datetime.now(),
      status = 'Active'
    )
    db.session.add(new_appointment)
    current_user.doctor = random_doctor.id
    if current_user.gender == None:
      current_user.gender = request.form.get("gender")
    db.session.commit()
    new_session = Session (
      session_id = random.randint(100000,999999),
      appointment = new_appointment.id,
      patient = new_appointment.patient,
      doctor = new_appointment.doctor,
      date_opened = datetime.datetime.now(),
      status = "Active"
    )
    db.session.add(new_session)
    db.session.commit()
    flash(f"Appointment created successfully", category="success")
    doctor = Doctors.query.filter_by(id=current_user.doctor).first()
    # clients.messages.create(
    #   to = '+254796897011',
    #   from_ = '+16203191736',
    #   body = f'\nCongratulations {current_user.first_name} {current_user.second_name} you have successfully created an appointment. Your appointment ID is {new_appointment.appointment_id}\nYou have been assigned doctor {doctor.first_name} {doctor.second_name}, tel {doctor.phone}, email {doctor.email}\nYour session ID is {new_session.session_id}'
    # )
    return redirect(url_for('patients.patient_session', session_id=new_session.id))

  return redirect(url_for('patients.patient_portal'))

@patients.route("/current-session/<int:session_id>", methods=["POST", "GET"])
@login_required
def patient_session(session_id):
  if current_user.account_type != "patient":
    flash(f"Only patients are allowed", category="warning")
    return redirect(url_for('patients.patient_signin'))
  session = Session.query.get(session_id)
  appointment = Appointment.query.filter_by(id=session.appointment).first()
  doctor = Doctors.query.filter_by(id=session.doctor).first()
  medicines = Medicine.query.all()
  symptoms = request.form
  if symptoms:
    session.symptoms = symptoms
    db.session.commit()
    flash(f"Your symptoms have been saved and sent to your doctor", category="success")
    return redirect(url_for('patients.patient_session', session_id=session.id))

  return render_template("patient_session.html", session=session, appointment=appointment, doctor=doctor, medicines=medicines)

@patients.route("/symptoms/<int:session_id>", methods=["POST", "GET"])
@login_required
def patient_symptoms(session_id):
  if current_user.account_type != "patient":
    flash(f"Only patients are allowed", category="warning")
    return redirect(url_for('patients.patient_signin'))
  session = Session.query.get(session_id)
  req = request.get_json()
  print(req)
  if req["name"]:
    new_symptom = Symptoms(
      name = req["name"],
      session = session.id
    )
    db.session.add(new_symptom)
    db.session.commit()
  res = make_response(jsonify(req), 200)
  
  return res

@patients.route("/add-allergies", methods=["POST", "GET"])
@login_required
def patient_allergies():
  if current_user.account_type != "patient":
    flash(f"Only patients are allowed", category="warning")
    return redirect(url_for('patients.patient_signin'))
  new_allergy = Allergies(
    name = request.form.get("names"),
    severe = request.form.get("severe"),
    patient = current_user.id
  )
  db.session.add(new_allergy)
  db.session.commit()
  flash(f"Your allergy has been added", category="success")

  return redirect(url_for('patients.patient_portal'))

@patients.route("/medical-bill-payment")
@login_required
def medical_bill_payment():
  if current_user.account_type != "patient":
    flash(f"Only patients are allowed", category="warning")
    return redirect(url_for('patients.patient_signin'))
  total = []
  prescriptions = Prescription.query.filter_by(patient=current_user.id, status="Active").all()
  for prescription in prescriptions:
    medicines = Medicine.query.filter_by(id=prescription.medicine).all()
    for medicine in medicines:
      total.append(medicine.price)
  checkout_session = stripe.checkout.Session.create(
    line_items = [
      {
        'price_data': {
          'currency': 'KES',
          'product_data': {
            'name': 'Medical Bill',
          },
          'unit_amount': (sum(total)*100),
        },
        'quantity': 1,
      }
    ],
    mode='payment',
    success_url=request.host_url + 'payment-complete',
    cancel_url=request.host_url + 'payment-failed',
  )
  
  return redirect(checkout_session.url)

@patients.route("/payment-failed")
@login_required
def payment_failed():
  flash(f"Payment process failed, try again", category="danger")
  return redirect(url_for('patients.patient_portal'))

@patients.route("/payment-complete")
@login_required
def payment_complete():
  if current_user.account_type != "patient":
    flash(f"Only patients are allowed", category="warning")
    return redirect(url_for('patients.patient_signin'))
  prescriptions = Prescription.query.filter_by(patient=current_user.id, status="Active").all()
  session = Session.query.filter_by(patient=current_user.id, status="Active").first()
  appointment = Appointment.query.filter_by(patient=current_user.id, status="Active").first()
  new_transaction = Transaction (
    transaction_id = random.randint(100000, 999999),
    patient = current_user.id,
    date = datetime.datetime.now(),
    status = "Success"
  )
  db.session.add(new_transaction)
  db.session.commit()
  for prescription in prescriptions:
    prescription.transactions = new_transaction.id
    prescription.status = "Closed"
    db.session.commit()
  current_user.doctor = None
  session.status = "Closed"
  appointment.status = "Closed"
  appointment.date_closed = datetime.datetime.now()
  session.date_closed = datetime.datetime.now()
  db.session.commit()
  flash(f"Medical bill has been cleared successfully", category="success")

  return redirect(url_for('patients.patient_portal'))

@patients.route("/logout")
@login_required
def patient_logout():
  logout_user()
  flash(f"Logged out successfully", category="success")
  return redirect(url_for('patients.patient_signin'))
