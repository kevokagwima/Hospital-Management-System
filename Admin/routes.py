from flask import Blueprint, flash, redirect, render_template, url_for, request
from Admin.form import *
from models import *
from flask_login import login_manager,  LoginManager, login_user, login_required, logout_user, current_user

admin = Blueprint('admin', __name__)

login_manager = LoginManager()
login_manager.init_app(admin)

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
    flash(f"Only admins are allowed", category="warning")
    return redirect(url_for('admin_signin'))
  patients = Patients.query.all()
  doctors = Doctors.query.all()
  appointments = Appointment.query.all()
  sessions = Session.query.all()
  prescriptions = Prescription.query.all()
  transactions = Transaction.query.all()
  medicines = Medicine.query.all()

  return render_template("admin.html", patients=patients, doctors=doctors, appointments=appointments, sessions=sessions, prescriptions=prescriptions, transactions=transactions, medicines=medicines)

@admin.route("/admin-logout")
@login_required
def admin_logout():
  logout_user()
  flash(f"Logged out successfully", category="success")
  return redirect(url_for('admin.admin_signin'))
