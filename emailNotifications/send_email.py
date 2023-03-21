'''
DEPRECATED (by redundancy)
The email_user() functionality provided by the inbuilt
django.contrib.auth.models.User model is now used.

Original file docstring:
Emails through SMTP
Works with a test email address (djangotestemail31@gmail.com)
Password is an "App Password" (used by gmail)
'''

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def build_message(sender: str, recipient: str, subject: str) -> dict[str, str]:
    '''
    Create a message to be sent to a recipient via email

        :param sender: the sender's email address
        :param recipient: the recipient's email address
        :param subject: the subject of the message
        :return: the constructed message
    '''

    # Create message container
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    # Create the message (HTML)
    html = """\
    A new challenge has been posted!
    """

    # Record the MIME type - text/html
    part1 = MIMEText(html, 'html')

    # Attach parts into message container
    msg.attach(part1)    

    return msg


def send_email(sender: str, username: str, password: str, recipients_list: list[str], subject: str) -> None:
    '''
    Send an email to each recipient in a given list of recipients
   
    :params sender: the sender's email address
    :params username: the sender's username (email address)
    :params password: the sender's App Password
    :param recipients_list: the list of recipients' email addresses
    :param subject: the content of the email
    :return: None
    '''

    # Connect to the SMTP server
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587) 
        server.ehlo()
        server.starttls()
        server.login(username, password)
    except smtplib.SMTPAuthenticationError:
        print("Error connecting to smtp server")

    # Send the email to all recipients
    for recipient in recipients_list:
        try:
            new_message = build_message(sender, recipient, subject)
            server.sendmail(sender, recipient, new_message.as_string())  
        except:
            print("Message to ", recipient, "failed to send.")

    # Close connection
    server.quit()

    return


if __name__ == '__main__':
    # Sender, recipients and message subject
    from_email = "djangotestemail31@gmail.com"
    to_list = [
        "djangotestemail31@gmail.com",
        "grosdino2003@gmail.com",
        "emailtest4626@gmail.com"
    ]
    msg_subject = "New challenge is out!"

    # Credentials
    username = 'djangotestemail31@gmail.com'  
    password = 'nrsrhztfmmwyqzey'

    # Send message
    send_email(from_email, username, password, to_list, msg_subject)
    print("email sent")