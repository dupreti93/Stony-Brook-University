import mailbox
from fpdf import FPDF
import re
import socket
import pygeoip
import numpy as np
import matplotlib.pyplot as plt
from PyPDF2 import PdfFileMerger
import webbrowser
import os




class PDF(FPDF):

    def printContent(self,domains,mails,words,labels,ip,loc):

        self.add_page()
        self.set_font('Helvetica', 'B', 20)
        title = 'YOUR SPAM REPORT'
        w = self.get_string_width(title) + 6
        self.set_x((210 - w) / 2)
        self.set_fill_color(200, 220, 255)
        self.set_font('', 'I')
        self.cell(w, 9, title)
        self.ln(70)
        txt = "Number of spams received: "
        self.set_font('Times', '', 12)
        self.multi_cell(0, 5, txt)
        self.ln()
        txt = str(mails)
        self.set_font('Times', 'I', 18)
        self.multi_cell(0, 5, txt)

        self.ln(15)

        txt = "Number of unique spammers: "
        self.set_font('Times', '', 12)
        self.multi_cell(0, 5, txt)
        self.ln()
        txt =  str(len(domains))
        self.set_font('Times', 'I', 18)
        self.multi_cell(0, 5, txt)


        self.ln(15)


        a,b=words[0]
        txt = "Word that appears most frequently in your spam: "
        self.set_font('Times', '', 12)
        self.multi_cell(0, 5, txt)
        self.ln()
        txt = '\'' + b + '\''
        self.set_font('Times', 'I', 18)
        self.multi_cell(0, 5, txt)

        self.ln(15)

        txt = "Top spammer: "
        self.set_font('Times', '', 12)
        self.multi_cell(0, 5, txt)
        self.ln()
        txt = '\'' + labels[0] + '\''
        self.set_font('Times', 'I', 18)
        self.multi_cell(0, 5, txt)

        self.ln(15)
        txt = "Top spammer's IP address:"
        self.set_font('Times', '', 12)
        self.multi_cell(0, 5, txt)
        self.ln()
        txt = '\'' + ip[0] + '\''
        self.set_font('Times', 'I', 18)
        self.multi_cell(0, 5, txt)

        self.ln(15)
        txt = "Top spammer's location:"
        self.set_font('Times', '', 12)
        self.multi_cell(0, 5, txt)
        self.ln()
        txt = '\'' + loc[0] + '\''
        self.set_font('Times', 'I', 18)
        self.multi_cell(0, 5, txt)


class SpamManager():

    def __init__(self):
        self.domains = {}
        self.emails={}
        self.sender=""
        self.domainWriter=None
        self.emailWriter=None
        self.senderemail= ""
        self.domain=""
        self.ip={}
        self.exp_labels=[]
        self.exp_val=[]
        self.exp_ip=[]
        self.exp_loc=[]
        self.clus_data=[]


        self.stdWords = []
        self.totalmails=0
        self.totalwords=0
        self.reader = None
        self.writer = None
        self.words={}
        self.count=0

    def getArray(self):

        for k in self.domains:
            self.clus_data.append((self.domains[k][0],k,self.domains[k][1],self.domains[k][2]))
        self.clus_data.sort(reverse=True)
        for i in range(10):
            a,b,c,d = self.clus_data[i][0],self.clus_data[i][1],self.clus_data[i][2],self.clus_data[i][3]
            self.exp_labels.append(b)
            self.exp_val.append(a)
            self.exp_ip.append(c)
            self.exp_loc.append(d)

    def mergePdfs(self):
        merger = PdfFileMerger()

        for i in range(self.count):
            merger.append(str(i) + '.pdf')
        merger.write('result.pdf')
        merger.close()
        cwd = os.getcwd()
        webbrowser.open("file://"+cwd+"/result.pdf")

    def getExplodeVals(self):
        array=[0.3,0.3,0.3]
        for i in range(3,10):
            array.append(0)
        return array

    def getbodyfromemail(self,msg):
        body = None
        # Walk through the parts of the email to find the text body.
        if msg.is_multipart():
            for part in msg.walk():

                # If part is multipart, walk through the subparts.
                if part.is_multipart():

                    for subpart in part.walk():
                        if subpart.get_content_type() == 'text/plain':
                            # Get the subpart payload (i.e the message body)
                            body = subpart.get_payload(decode=True)
                            # charset = subpart.get_charset()

                # Part isn't multipart so get the email body
                elif part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True)
                    # charset = part.get_charset()

        # If this isn't a multi-part message then get the payload (i.e the message body)
        if msg.get_content_type() == 'text/plain':
            body = msg.get_payload(decode=True)

        charsets = set({})
        for c in msg.get_charsets():
            if c is not None:
                charsets.update([c])

        for charset in charsets:
            try:
                body = body.decode(charset)
            except:
                pass

        return body


    def wordSheet(self):

        self.stdWords = ['the','be','to','of','and','a','in','that','have','I','it','for','not','on','with','he','as','you','do','at','this','but','his','by','from','they','we','say','her','she','or','an','will','my','one','all','would','there','their','what','so','up','out','if','about','who','get','which','go','me','when','make','can','like','time','no','just','him','know','take','people','into','year','your','good','some','could','them','see','other','than','then','now','look','only','come','its','over','think','also','back','after','use','two','how','our','work','first','well','way','even','new','want','because','any','these','give','day','most','us','subject','list','message','cause','email','please','post','mailing','more','sent','members','nonmembers','wrote','requests','information','link','call','view','thanks','received','error','pending','receive','account','mail','waiting','unsubscribe','follow','recipients','following','implicit','destination','deadline','here','dont','many','reply','below','emails','using','address','envelope','help','esmtp','need','date','localhost','question','find','visit','based','read','attend','been','including','contact','body','copy','should','notice','click','daily','commented','change','limit','search','posts','post','earliest','delivery','sender','created','remote','smtp','were','says','recipient','thank','researchers','rcpt','page','status','left','receiving','messageid','textplain','failed','addresses','youre','delivered','sign','consideration','host','convenience','application','today','center','tomorrow','call','made','update','image','very','great','being','settings','setting','right','left','width','height','content','type','hello','hi','hey','spam']

        for message in mailbox.mbox('mail.mbox'):
            self.totalmails+=1
            # body contains lowercase only, no numbers either
            body = self.getbodyfromemail(message)
            # No checking done to match the charset with the correct part.

            if body is None:
                    body = "None"

            body = re.sub("http:\/\/[^ ]","",body)
            body = body.lower()
            body = re.sub("[A-Za-z0-9]+[^a-zA-Z0-9 \n\']+[a-zA-z0-9]+","",body)
            body = re.sub("[^a-zA-Z0-9\n ]+[a-zA-z0-9]+|[a-zA-z0-9]+[^a-zA-Z0-9\n ,?.!:\-\']+","",body)
            body = re.sub("[^a-zA-z0-9\n ]+","",body)
            body = re.sub("\d+","",body)
            body = re.findall("[\w]+", body)


            # Count for each word
            for word in body:
                if len(word) < 21 and len(word) > 3:
                    self.totalwords+=1
                    if word not in self.words and word not in self.stdWords:
                        self.words[word] = 1
                    elif word not in self.stdWords:
                        self.words[word] += 1

        words=[]
        for k in self.words:
            words.append((self.words[k],k))

        words.sort(reverse=True)

        #PRINT THE MOST FREQUENTLY RECIEVED WORD:
        # Printing to PDF begins:
        pdf = PDF()
        pdf.printContent(self.domains, self.totalmails, words,self.exp_labels,self.exp_ip,self.exp_loc)
        pdf.output('0.pdf', 'F')

    def domainFile(self):

        for message in mailbox.mbox('mail.mbox'):
            self.sender = message['from']

            if self.sender is None:
                self.sender = "None"


            self.sender = self.sender.replace('\"', "")
            self.sender = self.sender.split("=")
            self.sender = self.sender[0]




            self.senderemail = self.sender.lower().split("<")
            if len(self.senderemail) > 1:
                self.senderemail = self.senderemail[1].split(">")[0]
            else:
                self.senderemail = self.senderemail[0]

            if self.senderemail not in self.emails:
                self.emails[self.senderemail] = 1
            else:
                self.emails[self.senderemail] +=1

            self.domain = self.senderemail.split("@")
            if len(self.domain) > 1:
                self.domain = self.domain[1]
            else:
                self.domain = self.domain[0]


            try:
                ip = socket.gethostbyname(self.domain)
                if ip not in self.ip:
                    self.ip[ip] = 1
                else:
                    self.ip[ip] +=1
            except:
                ip = None
            if ip:
                gi = pygeoip.GeoIP('GeoLiteCity.dat')
                rec = gi.record_by_addr(ip)
                s=""
                if rec is not None:
                    if rec['city']:
                        s+=rec['city']+", "
                    if rec['country_name']:
                        s+=rec['country_name']
                    else:
                        s += "Unavailable"
                else:
                    s+="Unavailable"
            else:
                ip="Unavailable"





            # Count domains
            if len(self.domain)>24:
                self.domain = self.domain[:9]+"..."+self.domain[len(self.domain)-9:len(self.domain)]
            if self.domain not in self.domains:
                self.domains[self.domain]=[1,ip,s]
            else:
                self.domains[self.domain][0] += 1




        #Data for top 10
        self.getArray()
        plt.axis("equal")
        plt.pie(self.exp_val,labels = self.exp_labels,radius =0.65,autopct='%0.1f%%',shadow=True,explode=self.getExplodeVals())
        #plt.show()
        plt.savefig('1.pdf')
        plt.clf()
        plt.cla()
        plt.close()

        for i in range(len(self.clus_data)):
            self.clus_data[i]=tuple([i+1]+list(self.clus_data[i]))
        count=2
        lo,hi=0,20
        flag=True
        while(flag):
            if hi>len(self.clus_data):
                flag=False
                hi = lo+len(self.clus_data)%20
            #Table data for top 10 with locations and ip
            fig, ax = plt.subplots()
            # Hide axes
            ax.xaxis.set_visible(False)
            ax.yaxis.set_visible(False)

            # Table from Ed Smith answer
            #Tuple of columns
            collabel = ("Rank","Count", "Domain", "IP Address","Location")
            colors = plt.cm.BuPu(np.linspace(0, 0.5, 5))
            table = ax.table(cellText=self.clus_data[lo:hi], colLabels=collabel, colColours=colors, loc='center',cellLoc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(5)
            table.scale(1, 1)

            #plt.show()
            plt.savefig(str(count)+'.pdf')
            plt.clf()
            plt.cla()
            plt.close()
            lo=hi-1
            hi=lo+20
            count+=1
        self.count=count




sMan = SpamManager()
sMan.domainFile()
sMan.wordSheet()
sMan.mergePdfs()



