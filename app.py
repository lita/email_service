from celery.exceptions import TimeoutError
from flask import Flask, render_template, request


import tasks

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
        request_data = request.form.to_dict()
        check_form_values(request_data)
    except InvalidFormError as err:
        return(str(err), 400)
    try:
        task = tasks.send_mail.delay(request_data)
        email_result = task.get(timeout=5)
    except TimeoutError:
        return ("Email is queued", 200)

    return (email_result, 200)


def check_form_values(request_data):
    """
    Determines if the post request has all the data needed to send the email
    """
    for key in email_format.iterkeys():
        if key not in request_data:
            raise InvalidFormError("Attribute, %s, invalid post data" % key)
        if not isinstance(request_data[key], email_format[key]["type"]):
            raise InvalidFormError("Attribute, %s, was not a string." % key)
        if email_format[key]["required"] and not request_data[key]:
            raise InvalidFormError("Attribute, %s, cannot be blank." % key)

if __name__ == "__main__":
    app.run(debug=True)
