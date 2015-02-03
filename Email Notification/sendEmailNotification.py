# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

# Open a plain text file for reading.  For this example, assume that
# the text file contains only ASCII characters.
fp = open("message.txt", 'rb')
# Create a text/plain message
msg = MIMEText(fp.read())
fp.close()

# me == the sender's email address (will need to get an email address from BPA)
# you == the recipient's email address
msg['Subject'] = 'Notification of Query Result'
msg['From'] = 'Zaynab'
msg['To'] = 'Zaynab'

# Will need to ask about this
# Send the message via our own SMTP server, but don't include the
# envelope header.
server = smtplib.SMTP('smtp.gmail.com', 587)
server.set_debuglevel(1)
server.ehlo()
server.starttls()
server.login('zalattar@pdx.edu', '')
server.sendmail('zalattar@pdx.edu', 'zalattar@frontier.com', msg.as_string())