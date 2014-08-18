import celery
from flask import Flask, render_template, request


import tasks
from services import MissingSender, MissingRecipient

app = Flask(__name__)

email_format = {
    "to": {"type": basestring, "required": True},
    "from_email": {"type": basestring, "required": True},
    "subject": {"type": basestring, "required": False},
    "text": {"type": basestring, "required": False}
}


class InvalidFormError(ValueError):
    pass


@app.route("/")
def render_index():
    return render_template("index.html")


@app.route("/email/api/1.0/send", methods=["POST"])
def send_email():
    try:
        check_form_values()
    except InvalidFormError as err:
        return(str(err), 400)
    try:
        task = tasks.send_mail.delay(request.form.to_dict())
        email_service = task.get(timeout=5)
        return ("Email was sent by %s" % email_service)
    except (MissingRecipient, MissingSender) as err:
        return (str(err), 400)
    except celery.exceptions.TimeoutError:
        return ("Email is queued", 200)

    return ("%s sent your email!" % email_service, 200)


def check_form_values():
    for key in email_format.iterkeys():
        if key not in request.form:
            raise InvalidFormError("Attribute, %s, invalid post data" % key)
        if not isinstance(request.form[key], email_format[key]["type"]):
            raise InvalidFormError("Attribute, %s, was not a string." % key)
        if email_format[key]["required"] and not request.form[key]:
            raise InvalidFormError("Attribute, %s, cannot be blank." % key)

if __name__ == "__main__":
    app.run(debug=True)
