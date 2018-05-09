# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 15:22:00 2018

@author: Sezer
"""

import imaplib
import email
import getpass
import re
import base64
import smtplib
import ssl
import sys
from colors import *
from email.mime.text import MIMEText

user_email = 'networkprogramming.utm.sa@gmail.com'
user_password = 'network2018'
gmail_connected = False
menu_count = -1
mail = imaplib.IMAP4_SSL('imap.gmail.com')

def encoded_words_to_text(encoded_words):
    try:
        encoded_word_regex = r'=\?{1}(.+)\?{1}([B|Q])\?{1}(.+)\?{1}='
        charset, encoding, encoded_text = re.match(encoded_word_regex, encoded_words).groups()
        if encoding is 'B':
            byte_string = base64.b64decode(encoded_text)
        elif encoding is 'Q':
            byte_string = quopri.decodestring(encoded_text)
        return byte_string.decode(charset)
    except Exception:
        return encoded_words
            
############# GMAIL LOGİN AND CONNECTION VIA IMAP################

def input_user_credentials():
    global user_email, user_password
    sys.stdout.write(BOLD + BLUE)
    print "######### PLEASE INTRODUCE YOUR LOGIN INFO #########"
    sys.stdout.write(GREEN)
    print "YOUR GMAİL ADDRESS : "
    user_email = raw_input()
    sys.stdout.write(CYAN)
    print "YOUR GMAİL PASSWORD : "
    user_password = getpass.getpass()
    connect_gmail_imap()

def connect_gmail_imap():
    global mail, gmail_connected
    mail.login(user_email, user_password)
    mail.select("INBOX")
    result2, new_messages = mail.search(None, '(UNSEEN)')
    gmail_connected = True
    print 
    sys.stdout.write(RED)
    print "Hello, " + user_email
    sys.stdout.write(BLUE)
    print "You have  " + str(len(new_messages[0].split()))," unread messages."
   


############## SEND AN EMAIL #################


def send_simple_mail():
    global mail
    print 'YOUR EMAIL MESSAGE: '
    msg = MIMEText(raw_input())
    print 'YOUR EMAIL SUBJECT: '
    msg['Subject'] = raw_input()
    print 'RECEIVER ADDRESS : '
    to_email = raw_input()
    msg['To'] = to_email
    print 'CC (IF YOU DO NOT WANT TO SEND PLEASE LEAVE IT ALONE) : '
    msg['CC'] = raw_input()
    msg['From'] = user_email

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(user_email, user_password)
    server.sendmail(user_email, to_email, msg.as_string())
    server.quit()


############## OPEN AN EMAIL ##################

def open_an_email():
    global mail
    esult, data = mail.uid('search', 'CHARSET', 'UTF-8', "ALL")
    list_of_ids = data[0].split()
    last_count_of_email = len(list_of_ids) - 1
    print 'HOW MANY EMAIL DO YOU WANT TO OPEN? : '
    mail_number = int(input()) - 1
    current_email_uid = list_of_ids[last_count_of_email - mail_number]
    result2, message_fetch = mail.uid('fetch', current_email_uid, '(RFC822)')
    raw_email = message_fetch[0][1]
    email_message = email.message_from_string(raw_email)
    print 
    sys.stdout.write(CYAN)
    print 'SUBJECT: ' + encoded_words_to_text(email_message['subject'])
    print 'SENDER: ' + email_message['from']
    print 'DATE: ' + email_message['Date']

    attachment_count = 0

    for part in email_message.walk():
        if part.get('Content-Disposition') is None:
            continue
        attachment_count += 1

    if attachment_count != 0:
        print str(attachment_count) + ' ATTACHMENT FOUND'

    if email_message.is_multipart():
        for part in email_message.get_payload():

            text = None
            
            if part.get_content_charset() is None:
                # We cannot know the character set, so return decoded "something"
                text = part.get_payload(decode=True)
                continue

            charset = part.get_content_charset()

            if part.get_content_type() == 'text/plain':
                text = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')
            if part.get_content_type() == 'text/html':
                html = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')
            if text is not None:
                print
                print 'CONTENT: ' + text.strip()
                print
    else:
        text = unicode(email_message.get_payload(decode=True), email_message.get_content_charset(), 'ignore').encode('utf8', 'replace')
        print 'CONTENT: ' + text.strip()

############## GET LAST N EMAILS #################

def get_last_n_messages():
    global mail
    print 'HOW MANY EMAILS DO YOU WANT TO FETCH? : '
    n = int(input())
    result, data = mail.uid('search', 'CHARSET', 'UTF-8', "ALL")
    list_of_ids = data[0].split()
    last_count_of_email = len(list_of_ids) - 1
    for i in range(n):
        current_email_uid = list_of_ids[last_count_of_email - i]
        result2, message_fetch = mail.uid('fetch', current_email_uid, '(RFC822)')
        raw_email = message_fetch[0][1]
        email_message = email.message_from_string(raw_email)
        print 
        sys.stdout.write(RED)
        print 'SUBJECT: ' + encoded_words_to_text(email_message['subject'])
        print 'SENDER: ' + email_message['from']
        print 'DATE: ' + email_message['Date']

        attachment_count = 0

        for part in email_message.walk():
            if part.get('Content-Disposition') is None:
                continue
            attachment_count += 1
        
        if attachment_count != 0:
            print str(attachment_count) + ' attachments found'

        if email_message.is_multipart():
            for part in email_message.get_payload():

                text = None
            
                if part.get_content_charset() is None:
                    # We cannot know the character set, so return decoded "something"
                    text = part.get_payload(decode=True)
                    continue

                if part.get_content_type() == 'text/plain':
                    charset = part.get_content_charset()
                    text = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')
                if text is not None:
                    print
                    print 'First sentence: ' + text.strip().split('\n')[0]
                    print
        

##################### MENU #########################

while menu_count != 0:
    print 
    if gmail_connected == False:
        sys.stdout.write(BOLD + BLUE)
        print "######### WELCOME TO GMAIL LOGIN #########"
        sys.stdout.write(RED)
        print "DO YOU WANT TO CONNECT TO YOUR GMAİL ACCOUNT?(YES=1 / NO=0)"
    elif gmail_connected == True:
        sys.stdout.write(REVERSE)
        print "2. TO GET LAST EMAILS"
        print "3. TO SEND AN EMAIL"
        print "4. TO READ EMAIL"
    print
    print
    menu_count = int(input())

    if gmail_connected == False:
        if menu_count == 1:
            input_user_credentials()
    elif gmail_connected == True:
        if menu_count == 2:
            get_last_n_messages()
        elif menu_count == 3:
            send_simple_mail()
        elif menu_count == 4:
            open_an_email()