import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from_address = "djangotestemail31@gmail.com"
to_addresses = [
    "djangotestemail31@gmail.com",
    "grosdino2003@gmail.com",
    "emailtest4626@gmail.com"
]


# Credentials
username = 'djangotestemail31@gmail.com'  
password = 'nrsrhztfmmwyqzey'

# Sending the email
server = smtplib.SMTP('smtp.gmail.com', 587) 
server.ehlo()
server.starttls()
server.login(username,password)

for to_address in to_addresses:
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Test email"
    msg['From'] = from_address
    msg['To'] = to_address

    # Create the message (HTML).
    html = """\
    A new challenge has been posted!
    """

    # Record the MIME type - text/html.
    part1 = MIMEText(html, 'html')

    # Attach parts into message container
    msg.attach(part1)
 
    server.sendmail(from_address, to_address, msg.as_string())  

server.quit()