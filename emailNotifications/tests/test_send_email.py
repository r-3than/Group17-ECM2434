import pytest
from email.mime.multipart import MIMEMultipart

from send_email import build_message, send_email

def test_build_message():
    test_sender = "example1@gmail.com"
    test_recipient = "example2@exeter.ac.uk"
    test_subject = "example subject"

    test_message = build_message(test_sender, test_recipient, test_subject)
    
    assert isinstance(test_message, MIMEMultipart)
    assert isinstance(test_message['From'], str)
    assert isinstance(test_message['To'], str)
    assert isinstance(test_message['Subject'], str)

    assert test_message['From'] == "example1@gmail.com"
    assert test_message['To'] == "example2@exeter.ac.uk"
    assert test_message['Subject'] == "example subject"


def test_send_message():
    test_sender = "example1@gmail.com"
    test_recipients = ["example2@gmail.com", "example3@gmail.com"]
    test_subject = "example subject"
    test_username_wrong = "notme"
    test_username = "djangotestemail31@gmail.com"
    test_password_wrong = "123"
    test_password = "nrsrhztfmmwyqzey"

    wrong_credentials = send_email(test_sender, test_username_wrong, test_password_wrong, test_recipients, test_subject)
    assert wrong_credentials == "Authentication failed"