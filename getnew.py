#!/usr/bin/env python
# author: jessinio
# version: v0.1
# changelog:
#  * compose by muitl code files
# changed by boj to automate the process

import os, sys
import traceback
import re
import subprocess
import time
import email as emaillib
import getpass, imaplib


# change email date to float time
# Target: sort email by exist time
def getEmailTime(TimeStr):
    #format : Fri, 10 Oct 2008 07:50:52
     try:
         FloatTime = time.mktime(time.strptime(TimeStr, "%a, %d %b %Y %H:%M:%S"))
     except:
         #other condition: by 10.114.170.12 with HTTP; Wed, 30 Jul 2008 20:44:36 -0700 (PDT)
         TimeStr = TimeStr.split(";")[1].strip()
         FloatTime = time.mktime(time.strptime(TimeStr, "%a, %d %b %Y %H:%M:%S"))
         assert FloatTime
     return FloatTime

 

##############################################################
#          main function: send email file to MDA
##############################################################

# send email (format) to MDA program
def sendMbox():
    try:
        GroupName = raw_input("which group will be send to?")
    except:
        print "Can't get group name!"
        sys.exit()
    if GroupName == "\n":
        print "Can't get group name!"
        sys.exit()

    MDAPath = "/usr/local/mailman/mail/mailman"
    try:
        raw_input("which MDA do you want?[return to %s]" % MDAPath)
    except:
        pass
    if not os.path.exists(MDAPath):
        print "no MDA! stupid"
        sys.exit()
    try:
        raw_input("where is the mbox file?")
    except:
        print "Can't get mbox file"
        sys.exit()
    if not os.path.exists( GoogleMailFile):
        print "Can't get mbox file"
        sys.exit()
    email_file = open(GoogleMailFile, "r")
    email_context = email_file.read()
    email_file.close()


    EmailMemory = []
    for EmailStr in email_context.split("#" * 20 + "\n"):
        # maybe match blank string, so continue
        if len(EmailStr) == 0:
            continue
        # get email time from mail message object
        emsg =  emaillib.message_from_string(EmailStr)
        FloatTime = getEmailTime(emsg["Received"].split("\n")[-1][:-12].strip())
        EmailMemory.append((FloatTime, EmailStr))

    # sort!
    EmailMemory.sort()

    # call MDA program
    def sendToMDA(GName):
            os.system("cat /tmp/temp_email_file.eml |%s post %s" % (MDAPath, GroupName))
            print "do one....."
    # save each email (format) file to disk, it will be read by MDA
    def saveToFile(EmailStr):
         temp_file = open("/tmp/temp_email_file.eml","w")
         temp_file.write(EmailStr)
         temp_file.close()

    for EmailStr in EmailMemory:
        #print EmailStr[0]
        saveToFile(EmailStr[1])
        sendToMDA(GName)
        time.sleep(3)

##############################################################
#            main function: download file
##############################################################

# download gmail email (format) to localhost file
def downMail(UserName, PassWord, LabelName, MboxFileDelta, MboxFileFull):
    ImapServerName = "imap.gmail.com"
    ImapServerPort = 993
    M = imaplib.IMAP4_SSL(ImapServerName, ImapServerPort)
    try:
        M.login(UserName, PassWord)
    except:
        print "Cant't login %s" % ImapServerName
        print "Please check user name and password, or network"
        sys.exit()

    # get label emails' ID
    M.select(LabelName)

    from datetime import datetime, date, timedelta
    #today = date.today().strftime("%d-%b-%Y")
    #yesterday = (date.today() - timedelta(1)).strftime("%d-%b-%Y")
    #tomorrow = (date.today() + timedelta(1)).strftime("%d-%b-%Y")
    #now = datetime.now().strftime("%d-%b-%Y %X")
    # timedelta 15 minutes (900 s)
    #last = (datetime.now() - timedelta(0, 900)).strftime("%d-%b-%Y %X")

    #condition = '(since "%s" before "%s")' % (last,now)
    #print condition

    try:
        #typ, data = M.search(None, condition)
        typ, data = M.search(None, 'all')
    except:
        print "Can't search this label"
        sys.exit()
    
    # create output file
    try:
        OutDelta = open(MboxFileDelta,"w+")
        OutFull = open(MboxFileFull,"a")
    except:
        print "Can't create file: %s" % MboxFileDelta
        print "Please check permission"
        sys.exit()
    
    # write emails to file though emails' ID
    for num in data[0].split():
        typ, data = M.fetch(num, '(RFC822)')
        print "writing.... %s" % data[0][0]
        OutDelta.write('%s\n%s\n' % ("#" * 20, data[0][1]))
        OutFull.write('%s\n%s\n' % ("#" * 20, data[0][1]))
        M.store(num, '+FLAGS', '\\Deleted')

    # exit program
    OutDelta.close()
    OutFull.close()
    M.expunge()
    M.close()
    M.logout()

##############################################################
#     main function:
#     make mbox file
##############################################################

def makeMbox(OldMboxFileStr, NewMboxFileStr):
    try:
        NewMboxFile = open(NewMboxFileStr, "w")
        OldMboxFile = open(OldMboxFileStr, "r")
        email_context = OldMboxFile.read()
        OldMboxFile.close()
        EmailMemory = []
        for EmailStr in email_context.split("#" * 20 + "\n")[1:]:
            # get email time from mail message object
            emsg =  emaillib.message_from_string(EmailStr)
            Sender = emsg["From"]
            FloatTime = getEmailTime(emsg["Received"].split("\n")[-1][:-12].strip())
            EmailMemory.append((FloatTime, emsg))
        EmailMemory.sort()
        
        patten = re.compile("<(.*?@.*?)>")
        for FloatTime, emsg in EmailMemory:
            FromStr = emsg["From"]
            try:
                FromStr = patten.search(FromStr).group(1) 
            except:
                pass
            emsgStr = "From " + FromStr + " " + time.strftime("%a %b %d %H:%M:%S %Y", time.localtime(FloatTime)) + "\n" + emsg.as_string()
            NewMboxFile.write(emsgStr)
        NewMboxFile.close()
    except:
        traceback.print_exc()
        sys.exit()

##############################################################
#     interview code:
#     choice: call main function
##############################################################

if __name__ == "__main__":
    UserName = sys.argv[1]
    PassWord = sys.argv[2]
    Labels = sys.argv[3:]
    MboxSaveDir = "/tmp/"
    for label in Labels:
        print "Saving " + label
        DeltaMbox = MboxSaveDir + label + "-delta.box"
        FullMbox = MboxSaveDir + label + "-full.box"
        NewMbox = MboxSaveDir + label + "-delta.mbox"
        downMail(UserName, PassWord, label, DeltaMbox, FullMbox)
        makeMbox(DeltaMbox, NewMbox)
