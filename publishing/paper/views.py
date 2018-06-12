from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth.models import User

from lxml import etree

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from models import Paper,Recension

def sendEmail(email,message,subject):
    fromaddr = "tp4restoranii@gmail.com"
    toaddr = email
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject
	
    body = message
    msg.attach(MIMEText(body, 'html'))
	
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "restorani")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

# Create your views here.
def uploadPage(request):
    template = loader.get_template("writePaperPage.html")
    publisherList = User.objects.filter(groups__name='publisher')
    return HttpResponse(template.render({'publishers':publisherList}))

def upload(request):
    #potrebne zastite za prenos
    content = request.POST.body
    model = etree.parse(content)
    title = model.findall('.//title').text_content()
    paper = Paper()
    paper.title = title
    paper.status = '0'
    paper.rec_total = 0
    paper.rec_completed = 0
    paper.author = request.user
    paper.publisher = User.objects.get(username = str(request.POST.get('publisher')))
    paper.deleted = False
    paper.location = "paper"+str(paper.id)+".xml" 
    paper.save()

    keywords = model.findall('.//keywords').text_content()
    paper_type = model.findall('.//classification').text_content()
    author = str(paper.author.surname)+" "+str(paper.author.name)
    publisher = str(paper.publisher.surname)+" "+str(paper.publisher.name)
    metadata = {'keywords':keywords,'paper_type':paper_type,'title':title,'author':author,'publisher':publisher}
    #upload to database

    #upload metadate to database

    message = request.POST.get('message')
    sendEmail(paper.publisher.email,message,"Publishing "+title)
    template = loader.get_template("static/completedPaper.html")
    return HttpResponse(template.render())    

def revisionPage(request):
    template = loader.get_template("revisionPage.html")
    #load article
    id = int(request.POST.get('articleId'))
    article = Paper.objects.get(id=id)
    paper = ""#
    #load questionnaire
    questionnairePath = "q"+article.publisher.username+".xml"
    questionnaire = ""#
    return HttpResponse(template.render({'paper':paper, 'questionnaire':questionnaire}))

def uploadRevision(request):
    id = int(request.POST.get('articleId'))
    article = Paper.objects.get(id=id)
    rr = Recension()
    #rr.reviewer = request.user
    rr.save()
    article.recension.add(rr)
    article.rec_completed = article.rec_completed+1
    article.reviewer.remove(request.user)
    article.save()
    #upload to database
    template = loader.get_template("static/completedPaper.html")
    return  HttpResponse(template.render())

def pullPaper(request):
    id = int(request.POST.get('articleId'))
    article = Paper.objects.get(id=id)
    article.deleted = True
    article.save()
    return HttpResponse(status_code=200)

def searchPage(request):#NOTDONE
    template = loader.get_template("searchPapersPage.html")
    #all the search shit
    #search database
    return HttpResponse(template.render({}))

def myPapers(request):
    template = loader.get_template("myPapersPage.html")
    articles = Paper.objects.filter(author__id = request.user.id,deleted=False)
    return HttpResponse(template.render({'articles':articles}))

def getPaper(request):
    template = loader.get_template("viewPaperPage.html")
    id = int(request.POST.get('articleId'))
    article = Paper.objects.get(id=id, deleted=False)
    #search database for paper
    
    #convert to html

    return HttpResponse(template.render({}))

def getPaperXml(request):
    id = int(request.POST.get('articleId'))
    article = Paper.objects.get(id=id, deleted=False)
    #serach databse for paper
    return HttpResponse()

def getPaperPdf(request):
    id = int(request.POST.get('articleId'))
    article = Paper.objects.get(id=id, deleted=False)
    #search database for paper
    #convert to pdf
    return HttpResponse()

def pendingRevisions(request):
    template = loader.get_template("pendingRevisionsPage.html")
    rev = Paper.objects.filter(reviewer__id=request.user.id)
    #papaers from model
    return HttpResponse(template.render({'revisions':rev}))

def refuseRevision(request):
    #change papaer max rev
    id = int(request.POST.get('articleId'))
    article = Paper.objects.get(id=id)
    article.rec_total = article.rec_total-1
    article.reviewer.remove(request.user)
    article.save()
    #send email
    message = request.POST.get('message')
    sendEmail(article.publisher.email,message,"Refused revision of " + str(article.title))
    return HttpResponse(status_code=200)

def submitedPapersPage(request):
    template = loader.get_template("submitedPapersPage.html")
    articles = Paper.objects.filter(publisher__id = request.user.id,deleted=False)
    return HttpResponse(template.render({'papers':articles}))

def appointRevisionPage(request):
    template = loader.get_template("appointRevisionsPage.html")
    #find suggested
    suggestedList = User.objects.all()
    #find article
    id = int(request.POST.get('articleId'))
    article = Paper.objects.get(id=id)
    return HttpResponse(template.render({'paper':article,'suggested':suggestedList}))

def appointRevision(request):
    id = int(request.POST.get('articleId'))
    userId = int(request.POST.get('userId'))
    user = User.objects.get(id=userId)
    article = Paper.objects.get(id=id)
    article.rec_total = article.rec_total+1
    article.reviewer.add(user)
    article.save()
    #send email odvojiti u sopstveni thread
    message = request.POST.get('message')
    sendEmail(article.publisher.email,message,"Receved revision request for " + str(article.title))
    return HttpResponse(status_code=200)

def setAcceptedState(request):
    id = int(request.POST.get('articleId'))
    article = Paper.objects.get(id=id)
    article.state = '4'
    article.save()

def setRefusedState(request):
    id = int(request.POST.get('articleId'))
    article = Paper.objects.get(id=id)
    article.state = '3'
    article.save()

def setRevisionState(request):
    id = int(request.POST.get('articleId'))
    article = Paper.objects.get(id=id)
    article.state = '1'
    article.save()

def setWritingState(request):
    id = int(request.POST.get('articleId'))
    article = Paper.objects.get(id=id)
    article.state = '2'
    article.save()

def getPaperSchema(request):
    pass

def getRevisionSchema(request):
    pass

def getLetterSchema(request):
    pass
    
def getQuestionnaireSchema(request):
    pass

def getUserInfo(request):
    pass