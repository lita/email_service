#Email Service
This was created for the Uber coding challenge. I choose the Email Service project, following the back-end track.

You can see this project live at http://email.litacho.com.

##My Background
I am very familiar with the Python language. I spent 3.5 years writing pipeline tools for Dreamworks Animation before going to Hacker School. I am currently interning for GNOME's Outreach for Women program, contributing to CPython full-time.

While at Hacker School, I made a BitTorrent client without any libraries in Python. I then used Flask to make it a video player (this is still a work in progress).

- https://github.com/lita/bittorrent
- https://github.com/lita/bittorrent/tree/video_torrent

I also pretend to be a JavaScript Developer, especially when I go to hackathons.

- https://github.com/ben-eath/the-surf-ace - Wrote the backend in Node.js
- http://challengepost.com/software/tunes-against-humanity - most of the interactions with the Firebase data.
- https://github.com/tilt-js/tilt.js - an open source library I am working on to make your mobile phone into a game controller.

##Technologies and Tools used
- Flask
- Celery
- RabbitMQ
- Redis
- Mailgun
- Mandrill
- Heroku

I was not familiar with Heroku, Celery or the email APIs before this project. I have tried setting up a page using Amazing EC2 servers. I like Heroku way more.

##Installation
1. Install the dependences using pip.
`pip install -r requirements.txt`

2. Start up RabbitMQ and Redis.

3. You have to set your environment variables before launching the web application.

  ```
  # Mandrill API
  MANDRILL_API_URL=[your API url]
  MANDRILL_API_KEY=[your API key]

  # Mailgun API
  MAILGUN_API_URL=https://api.mailgun.net/v2
  MAILGUN_API_KEY=[your API key]
  MAILGUN_DOMAIN=[your domain name registerd with Mailgun]

  # RabbitMQ and Redis. This assume you are running them locally.
  CLOUDAMQP_URL=amqp://guest@localhost/
  REDISTOGO_URL=redis://localhost:6379/0
  ```

4. Here are the commands to launch `celery` and `flask` app!

  `$ celery -A tasks worker --loglevel=info`

  Then run the Flask app!

  `$ python app.py`

  If you want to run it in production, you should run it with gunicorn.

  `$ gunicorn app:app --log-file=-`


5. If you are using foreman, you can store your environment variables in your virtual environment and run `foreman start`. This project has a Procfile all set up for you.

##Front-end Usage
All you need to do is make a post request to the following url.
`http://mail.litacho.com/email/api/1.0/send`

You must send it with the following names or else your email won't send:
- `to`: Sender's email
- `from_email`: Recipient's email
- `subject`: Subject
- `text`: Body of the message

##Architecture and Design
I knew the bottle neck would be making the request to the various email APIs and waiting for a response. So I did the following:

### Asynchronous Structure
`app.py` - The flask app. This handles checking to see if the front-end sends the necessary data in order to send an email. Then it will call `tasks` module to send the data. This is done with celery's `delay` method, so it can send many emails asynchronously.

`tasks.py` - This chooses a random email service and sends off the data.

###Email services
`services` - This has an abstract class, called `BaseService`, that all email service interfaces must subclass. If a developer wanted to add a new email service, they need to inherit this class and implement `ping`, `name` (which is the name of the service), and `send`. I have implemented `service.mandrill` and `service.mailgun` that subclass `BaseService` and interfaces with their respective APIs.

`loader.py` - this looks through the `services` folder and finds any classes that inherits from `BaseService` and creates a list of available services. Then `tasks.send_mail` selects a random email service from that list.

###Pros
*Abstraction* - This system separates parsing the web request and sending out the email. Thus if one email service went down, the system is able to retry with a different email service.

*Asynchronous and Multi-process* - Because the system is asynchronous and handles spawning multiple workers, this system can scale well when it is getting lots of requests. With Heroku and Celery, you can easily add more workers.

###Cons
*No notification* - If there are a lot of requests, the server might not have time to notify you when the email has been sent. All it will say is that the email has been queued.

##TODOs
- Use webhooks to notify the user if the email has been sent.
- Validate email. Currently, I allow multiple email address for the 'To' field. Right now, I am letting API handle the call.
- Handle bcc and cc.
- Add integration tests.
