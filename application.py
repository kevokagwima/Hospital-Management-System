from flask import Flask, render_template, redirect, url_for, request, sessions
from flask.helpers import flash
from models import db, Patients, Doctors, Appointment, Session, Medicine, Prescription, Transaction
from form import patient_registration, login, doctor_registration
from flask_login import login_manager,LoginManager,login_user,login_required,logout_user,current_user
from werkzeug.utils import secure_filename
import datetime, random, stripe

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
  "mssql://@KEVINKAGWIMA/HMS?driver=SQL SERVER"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "mysecretkeythatyouarenotsupposedtosee"
stripe.api_key = "sk_test_51J8POQHxOFRqyd61L7UzfYpE75ICCFRlAkMeQn57fJtO8q6tD6RhcAAu743nGwM8ShVrMaNtuxpZF0PjX8U1snnB00BH2Sk76b"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = -1

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = "signin"
login_manager.login_message_category = "danger"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
  try:
    return Patients.query.filter_by(phone=user_id).first() or Doctors.query.filter_by(phone=user_id).first()
  except:
    return None

@app.route("/")
@app.route("/home")
def index():
  return render_template("index.html")

@app.route("/patient-signup", methods=["POST", "GET"])
def patient_register():
  form = patient_registration()
  try:
    if form.validate_on_submit():
      user = Patients (
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
      db.session.add(user)
      db.session.commit()
      flash(f"Account successfully created", category="success")
      return redirect(url_for('signin'))

    if form.errors != {}:
      for err_msg in form.errors.values():
        flash(f"There was an error creating the user: {err_msg}", category="danger")
  except:
    flash(f"An error occurred when submitting the form. Check the from and try again", category="danger")
  return render_template("patient_signup.html", form=form)

@app.route("/doctor-signup", methods=["POST", "GET"])
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
      return redirect(url_for('signin'))

    if form.errors != {}:
      for err_msg in form.errors.values():
        flash(f"There was an error creating the user: {err_msg}", category="danger")
  except:
    flash(f"An error occurred when submitting the form. Check the from and try again", category="danger")
    
  return render_template("patient_signup.html", form=form)

@app.route("/signin", methods=["POST", "GET"])
def signin():
  form = login()
  if form.validate_on_submit():
    patient = Patients.query.filter_by(email=form.email.data).first() 
    doctor = Doctors.query.filter_by(email=form.email.data).first()
    if patient is None and doctor is None:
      flash(f"No user with that email", category="danger")
    elif patient and patient.check_password_correction(attempted_password=form.password.data):
      login_user(patient, remember=True)
      flash(f"Login successfull, welcome {current_user.first_name} {current_user.second_name}", category="success")
      next = request.args.get("next")
      return redirect(next or url_for("patient_portal"))
    elif doctor and doctor.check_password_correction(attempted_password=form.password.data):
      login_user(doctor, remember=True)
      flash(f"Login successfull, welcome doctor {current_user.first_name} {current_user.second_name}", category="success")
      next = request.args.get("next")
      return redirect(next or url_for("doctor_portal"))
    else:
      flash(f"Invalid Login Credentials", category="danger")

  return render_template("signin.html", form=form)

@app.route("/patient-portal")
@login_required
def patient_portal():
  if current_user.account_type != "patient":
    flash(f"Only patients are allowed", category="warning")
    return redirect(url_for('signin'))
  session = Session.query.filter_by(patient=current_user.id, status="Active").first()
  doctors = Doctors.query.all()
  appointments = Appointment.query.all()
  appointmentz = Appointment.query.filter_by(status="Closed").all()
  prescriptions = Prescription.query.filter_by(patient=current_user.id).all()
  transactions = Transaction.query.filter_by(patient=current_user.id).all()
  medicines = Medicine.query.all()
  
  return render_template("patient_portal.html", session=session, doctors=doctors, appointments=appointments, appointmentz=appointmentz, prescriptions=prescriptions, medicines=medicines, transactions=transactions)

@app.route("/book-appointment", methods=["POST", "GET"])
@login_required
def book_appointment():
  if current_user.account_type != "patient":
    flash(f"Only patients are allowed", category="warning")
    return redirect(url_for('signin'))
  available_doctors = []
  doctors = Doctors.query.all()
  for doctor in doctors:
    appointment = Appointment.query.filter_by(doctor=doctor.id, status="Active").first()
    if appointment == None:
      available_doctors.append(doctor)
  if len(available_doctors) == 0:
    flash(f"No available doctors to assign, all doctors are already engaged in a session", category="info")
    return redirect(url_for('patient_portal'))
  random_doctor = random.choice(available_doctors)
  appointment = Appointment.query.filter_by(patient=current_user.id, status="Active").first()
  if appointment:
    flash(f"You have an active appointment, complete it before creating a new one", category="danger")
  else:
    new_appointment = Appointment (
      appointment_id = random.randint(100000,999999),
      name = "Doctor Consultation",
      patient = current_user.id,
      doctor = random_doctor.id,
      date_created = datetime.datetime.now(),
      status = 'Active'
    )
    db.session.add(new_appointment)
    current_user.doctor = random_doctor.id
    current_user.gender = request.form.get("gender")
    db.session.commit()
    new_session = Session (
      session_id = random.randint(100000,999999),
      appointment = new_appointment.id,
      patient = new_appointment.patient,
      doctor = new_appointment.doctor,
      status = "Active"
    )
    db.session.add(new_session)
    db.session.commit()
    flash(f"Appointment created successfully", category="success")
    return redirect(url_for('patient_session', session_id=new_session.id))

  return redirect(url_for('patient_portal'))

@app.route("/current-session/<int:session_id>", methods=["POST", "GET"])
def patient_session(session_id):
  if current_user.account_type != "patient":
    flash(f"Only patients are allowed", category="warning")
    return redirect(url_for('signin'))
  session = Session.query.get(session_id)
  appointment = Appointment.query.filter_by(id=session.appointment).first()
  doctor = Doctors.query.filter_by(id=session.doctor).first()
  medicines = Medicine.query.all()
  sysmptoms = request.form.get("symptoms")
  if sysmptoms:
    session.symptoms = sysmptoms
    db.session.commit()
    flash(f"Your symptoms have been saved and sent to your doctor", category="success")
    return redirect(url_for('patient_session', session_id=session.id))

  return render_template("patient_session.html", session=session, appointment=appointment, doctor=doctor, medicines=medicines)

@app.route("/medical-bill-payment")
@login_required
def medical_bill_payment():
  if current_user.account_type != "patient":
    flash(f"Only patients are allowed", category="warning")
    return redirect(url_for('signin'))
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

@app.route("/payment-failed")
@login_required
def payment_failed():
  flash(f"Payment process failed, try again", category="danger")
  return redirect(url_for('patient_portal'))

@app.route("/payment-complete")
@login_required
def payment_complete():
  if current_user.account_type != "patient":
    flash(f"Only patients are allowed", category="warning")
    return redirect(url_for('signin'))
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
  db.session.commit()
  flash(f"Medical bill has been cleared successfully", category="success")

  return redirect(url_for('patient_portal'))

@app.route("/doctor-portal")
@login_required
def doctor_portal():
  if current_user.account_type != "doctor":
    flash(f"Only doctors are allowed", category="warning")
    return redirect(url_for('signin'))
  session = Session.query.filter_by(doctor=current_user.id, status="Active").first()
  appointments = Appointment.query.all()  
  appointmentz = Appointment.query.filter_by(status="Closed").all()
  patients = Patients.query.all()
  medicines = Medicine.query.all()

  return render_template("doctor_portal.html", session=session, appointments=appointments, appointmentz=appointmentz, patients=patients, medicines=medicines)

@app.route("/doctor-patient-session/<int:session_id>")
@login_required
def doctor_session(session_id):
  if current_user.account_type != "doctor":
    flash(f"Only doctors are allowed", category="warning")
    return redirect(url_for('signin'))
  session = Session.query.get(session_id)
  appointment = Appointment.query.filter_by(id=session.appointment).first()
  patient = Patients.query.filter_by(id=session.patient).first()
  medicines = Medicine.query.all()

  return render_template("doctor_session.html", session=session, appointment=appointment, patient=patient, medicines=medicines)

@app.route("/patient-diagnosis/<int:session_id>", methods=["POST", "GET"])
@login_required
def diagnosis(session_id):
  if current_user.account_type != "doctor":
    flash(f"Only doctors are allowed", category="warning")
    return redirect(url_for('signin'))
  session = Session.query.get(session_id)
  diagnosis = request.form.get("diagnosis")
  session.diagnosis = diagnosis
  db.session.commit()
  flash(f"Diagnosis updated successfully, patient will be alerted", category="success")
  
  return redirect(url_for('doctor_session', session_id=session.id))

@app.route("/patient-prescription/<int:session_id>", methods=["POST", "GET"])
@login_required
def prescription(session_id):
  if current_user.account_type != "doctor":
    flash(f"Only doctors are allowed", category="warning")
    return redirect(url_for('signin'))
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

  return redirect(url_for('doctor_session', session_id=session.id))

@app.route("/patient-notes/<int:session_id>", methods=["POST", "GET"])
@login_required
def notes(session_id):
  if current_user.account_type != "doctor":
    flash(f"Only doctors are allowed", category="warning")
    return redirect(url_for('signin'))
  session = Session.query.get(session_id)
  session.notes = request.form.get("notes")
  db.session.commit()
  flash(f"Additional notes sent successfully", category="success")

  return redirect(url_for('doctor_session', session_id=session.id))

@app.route("/patient-vitals/<int:session_id>", methods=["POST", "GET"])
@login_required
def patient_vitals(session_id):
  if current_user.account_type != "doctor":
    flash(f"Only doctors are allowed", category="warning")
    return redirect(url_for('signin'))
  session = Session.query.get(session_id)
  patient = Patients.query.filter_by(id=session.patient).first()
  patient.blood_pressure = request.form.get("blood_pressure")
  patient.weight = request.form.get("weight")
  patient.height = request.form.get("height")
  db.session.commit()
  flash(f"Patient's vitals updated successfully", category="success")

  return redirect(url_for('doctor_session', session_id=session.id))

@app.route("/add-new-medicine", methods=["POST", "GET"])
@login_required
def add_medicine():
  if current_user.account_type != "doctor":
    flash(f"Only doctors are allowed", category="warning")
    return redirect(url_for('signin'))
  new_medicine = Medicine (
    name = request.form.get("name"),
    type = request.form.get("type"),
    treatment = request.form.get("treatment"),
    price = request.form.get("price")
  )
  db.session.add(new_medicine)
  db.session.commit()
  flash(f"Medicine added successfully", category="success")

  return redirect(url_for('doctor_portal'))

@app.route("/logout")
@login_required
def logout():
  logout_user()
  flash(f"Logged out successfully", category="success")
  return redirect(url_for('signin'))

if __name__ == '__main__':
  app.run(debug=True)
