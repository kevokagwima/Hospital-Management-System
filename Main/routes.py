from flask import Blueprint, render_template, flash, redirect, request, url_for, request
import sendgrid, os
from sendgrid.helpers.mail import Mail, Email, To, Content

main = Blueprint("main", __name__)

sg = sendgrid.SendGridAPIClient(api_key=os.environ['Email_api_key'])
from_email = Email("kevinkagwima4@gmail.com")

@main.route("/")
@main.route("/home")
def index():
  return render_template("index.html")

@main.route("/contact", methods=["POST", "GET"])
def contact():
  first_name = request.form.get("fname")
  last_name = request.form.get("lname")
  email = request.form.get("email")
  message = request.form.get("message")
  try:
    to_email = To(f"kevokagwima@gmail.com")
    subject = f"Enquiry From {first_name} {last_name}"
    content = Content("text/plain", f"{message}\nYou can reach out via {email}")
    mail = Mail(from_email, to_email, subject, content)
    mail_json = mail.get()
    response = sg.client.mail.send.post(request_body=mail_json)
    print(response.headers)
    flash(f"Message sent successfully", category="success")
  except:
    flash(f"Failed to send email", category="danger")
  
  return redirect(url_for('main.index'))
