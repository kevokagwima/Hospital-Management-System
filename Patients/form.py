from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SelectField, TextAreaField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from models import Patients

class patient_registration(FlaskForm):
  first_name = StringField(label="First Name", validators=[DataRequired()])
  second_name = StringField(label="Second Name", validators=[DataRequired()])
  last_name = StringField(label="Last Name", validators=[DataRequired()])
  age = IntegerField(label="Age", validators=[DataRequired()])
  email_address = StringField(label="Email Address", validators=[Email(), DataRequired()])
  phone_number = StringField(label="Phone number",validators=[Length(min=10, max=10, message="Invalid Phone Number"),DataRequired()])
  address = StringField(label="County", validators=[Length(min=4, message="County must be more than 4 characters"), DataRequired()])
  address1 = StringField(label="City", validators=[Length(min=3, message="City must be more than 4 characters"),DataRequired()])
  password = PasswordField(label="Password", validators=[Length(min=5, message="Password must be more than 5 characters"), DataRequired()])
  password1 = PasswordField(label="Confirm Password", validators=[EqualTo("password", message="Passwords do not match"), DataRequired()])

  def validate_phone_number(self, phone_number_to_validate):
    phone_number = Patients.query.filter_by(phone=phone_number_to_validate.data).first()
    if phone_number:
      raise ValidationError("Phone Number already exists, Please try another one")

  def validate_phone_number_validity(self, phone_number_to_validate):
    if str(phone_number_to_validate.data)[0] != 0:
      raise ValidationError("Invalid phone number. Phone number must begin with 0 followed by 7 or 1")

  def validate_email_address(self, email_to_validate):
    email = Patients.query.filter_by(email=email_to_validate.data).first()
    if email:
      raise ValidationError("Email Address already exists, Please try another one")

class login(FlaskForm):
  email = StringField(label="Email Address", validators=[DataRequired()])
  password = PasswordField(label="Password", validators=[DataRequired()])
