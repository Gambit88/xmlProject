from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth.models import User,Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required, csrf_exempt

from io import StringIO
from lxml import etree
import _thread

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from models import Paper,Recension,Questionnaire,Schema,Qlog

import requests
from requests.auth import HTTPDigestAuth

def sendEmail(email,message,subject):#DONE
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
#AUTHOR##############################
@login_required(login_url="/paper/loginPage")
@permission_required('paper.add_paper')
def uploadPage(request):#DONE
    template = loader.get_template("writePaperPage.html")
    publisherList = User.objects.filter(groups__name='publisher')
    return HttpResponse(template.render({'publishers':publisherList}))

@login_required(login_url="/paper/loginPage")
@permission_required('paper.add_paper')
@csrf_exempt
def upload(request):#DONE
    #prvo parsirati uz proveru seme
    sch = Schema.objects.get(name="paper")
    schema = StringIO(sch.text)
    schema_doc = etree.parse(schema)
    xmlschema = etree.XMLSchema(schema_doc)
    message = request.POST.body
    doc = etree.parse(message)
    if xmlschema.validate(doc)==False:
        return HttpResponse(status_code=400)#dokument ne odgovara semi
    
    sch = Schema.objects.get(name="letter")
    schema = StringIO(sch.text)
    schema_doc = etree.parse(schema)
    xmlschema = etree.XMLSchema(schema_doc)
    message = request.POST.get('message')
    doc = etree.parse(message)
    if xmlschema.validate(doc)==False:
        return HttpResponse(status_code=400)#pismo ne odgovara semi
    
    content = request.POST.body
    model = etree.parse(content)
    title = model.findall('.//title').text_content()
    keywords = model.findall('.//keywords').text_content()
    paper_type = model.findall('.//classification').text_content()
    paper = Paper()
    paper.title = title
    paper.status = '0'
    paper.rec_total = 0
    paper.rec_completed = 0
    paper.author = request.user
    paper.publisher = User.objects.get(username = str(request.POST.get('publisher')))
    paper.deleted = False
    paper.text = content
    paper.paper_type = paper_type
    paper.keywords = keywords
    paper.save()
    
    _thread.start_new_thread(sendEmail,(paper.publisher.email,message,"Publishing "+title))
    template = loader.get_template("static/completedPaper.html")
    return HttpResponse(template.render())    

@login_required(login_url="/paper/loginPage")
@permission_required('paper.add_paper')
@csrf_exempt
def pullPaper(request):#DONE
    id = int(request.POST.get('articleId'))
    article = Paper.objects.get(id=id)
    article.deleted = True
    article.save()
    return HttpResponse(status_code=200)

@login_required(login_url="/paper/loginPage")
@permission_required('paper.add_paper')
def myPapers(request):#DONE
    template = loader.get_template("myPapersPage.html")
    articles = Paper.objects.filter(author__id = request.user.id,deleted=False)
    return HttpResponse(template.render({'articles':articles}))
#######################################################################

#REVISION CCONTROL######################################
@login_required(login_url="/paper/loginPage")
@permission_required('paper.add_recension')
def pendingRevisions(request):#DONE
    template = loader.get_template("pendingRevisionsPage.html")
    rev = Paper.objects.filter(reviewer__id=request.user.id)
    return HttpResponse(template.render({'revisions':rev}))

@login_required(login_url="/paper/loginPage")
@permission_required('paper.add_recension')
@csrf_exempt
def refuseRevision(request):#DONE
    #proveriti validaciju poruke
    sch = Schema.objects.get(name="letter")
    schema = StringIO(sch.text)
    schema_doc = etree.parse(schema)
    xmlschema = etree.XMLSchema(schema_doc)
    message = request.POST.get('message')
    doc = etree.parse(message)
    if xmlschema.validate(doc)==False:
        return HttpResponse(status_code=400)#poruka ne odgovara semi
    id = int(request.POST.get('articleId'))
    article = Paper.objects.get(id=id)
    article.rec_total = article.rec_total-1
    article.reviewer.remove(request.user)
    article.save()
    _thread.start_new_thread(sendEmail,(article.publisher.email,message,"Refused revision of " + str(article.title)))
    return HttpResponse(status_code=200)

@login_required(login_url="/paper/loginPage")
@permission_required('paper.add_recension')
def revisionPage(request):#DONE
    template = loader.get_template("revisionPage.html")
    id = int(request.GET.get('articleId'))
    article = Paper.objects.get(id=id, reviewer__id=request.user.id)
    paper = article.text
    questionnaire = (Questionnaire.objects.get(paper__id=article.id)).text
    return HttpResponse(template.render({'paper':paper, 'questionnaire':questionnaire}))

@login_required(login_url="/paper/loginPage")
@permission_required('paper.add_recension')
@csrf_exempt
def uploadRevision(request):#DONE
    #prvo parsirati
    sch = Schema.objects.get(name="revision")
    schema = StringIO(sch.text)
    schema_doc = etree.parse(schema)
    xmlschema = etree.XMLSchema(schema_doc)
    message = request.POST.body
    doc = etree.parse(message)
    if xmlschema.validate(doc)==False:
        return HttpResponse(status_code=400)#revizija ne odgovara semi
    sch = Schema.objects.get(name="questionnaire")
    schema = StringIO(sch.text)
    schema_doc = etree.parse(schema)
    xmlschema = etree.XMLSchema(schema_doc)
    message = request.POST.get('questionnaire')
    doc = etree.parse(message)
    if xmlschema.validate(doc)==False:
        return HttpResponse(status_code=400)#upitinik ne odgovara semi
    
    id = int(request.POST.get('articleId'))
    article = Paper.objects.get(id=id)
    questionnaire = Qlog()
    questionnaire.text=message
    questionnaire.save()
    rr = Recension()
    rr.text = request.POST.body
    rr.qlog = questionnaire
    rr.save()
    article.recension.add(rr)
    article.rec_completed = article.rec_completed+1
    article.reviewer.remove(request.user)
    article.save()
    template = loader.get_template("static/completedPaper.html")
    return  HttpResponse(template.render())
#######################################################

#PUBLISHER CONTROL##################
@login_required(login_url="/paper/loginPage")
@permission_required('paper.can_publish')
def submitedPapersPage(request):#DONE
    template = loader.get_template("submitedPapersPage.html")
    articles = Paper.objects.filter(publisher__id = request.user.id,deleted=False)
    return HttpResponse(template.render({'papers':articles}))

@login_required(login_url="/paper/loginPage")
@permission_required('paper.can_publish')
def appointRevisionPage(request):#DONE
    template = loader.get_template("appointRevisionsPage.html")
    suggestedList = User.objects.filter(groups__name='reviewer')
    id = int(request.GET.get('articleId'))
    article = Paper.objects.get(id=id).defer("text")
    return HttpResponse(template.render({'paper':article,'suggested':suggestedList}))

@login_required(login_url="/paper/loginPage")
@permission_required('paper.can_publish')
@csrf_exempt
def appointRevision(request):#DONE
    #proveriti validaciju poruke
    sch = Schema.objects.get(name="letter")
    schema = StringIO(sch.text)
    schema_doc = etree.parse(schema)
    xmlschema = etree.XMLSchema(schema_doc)
    message = request.POST.get('message')
    doc = etree.parse(message)
    if xmlschema.validate(doc)==False:
        return HttpResponse(status_code=400)#poruka ne odgovara semi
    id = int(request.POST.get('articleId'))
    userId = int(request.POST.get('userId'))
    user = User.objects.get(id=userId)
    article = Paper.objects.get(id=id).defer("text")
    article.rec_total = article.rec_total+1
    article.reviewer.add(user)
    article.save()
    _thread.start_new_thread(sendEmail, (article.publisher.email,message,"Receved revision request for " + str(article.title)))
    return HttpResponse(status_code=200)


@login_required(login_url="/paper/loginPage")
@permission_required('paper.can_manage')
@csrf_exempt
def setAcceptedState(request):#DONE
    id = int(request.POST.get('articleId'))
    article = Paper.objects.get(id=id)
    article.state = '4'
    article.save()

@login_required(login_url="/paper/loginPage")
@permission_required('paper.can_manage')
@csrf_exempt
def setRefusedState(request):#DONE
    id = int(request.POST.get('articleId'))
    article = Paper.objects.get(id=id)
    article.state = '3'
    article.save()

@login_required(login_url="/paper/loginPage")
@permission_required('paper.can_manage')
@csrf_exempt
def setRevisionState(request):#DONE
    id = int(request.POST.get('articleId'))
    article = Paper.objects.get(id=id)
    article.state = '1'
    article.save()

@login_required(login_url="/paper/loginPage")
@permission_required('paper.can_manage')
@csrf_exempt
def setWritingState(request):#DONE
    id = int(request.POST.get('articleId'))
    article = Paper.objects.get(id=id)
    article.state = '2'
    article.save()
#######################################

#PUBLIC#################################
def searchPage(request):
    template = loader.get_template("searchPapersPage.html")
    #all the search regex based
    return HttpResponse(template.render({}))

def getPaper(request,paper_id):
    template = loader.get_template("viewPaperPage.html")
    article = Paper.objects.get(id=paper_id, deleted=False,status='4')
    #convert to html

    return HttpResponse(template.render({}))

def getPaperXml(request):#DONE
    id = int(request.GET.get('articleId'))
    article = Paper.objects.get(id=id, deleted=False,status='4')
    text = article.text
    return HttpResponse(content=text,status_code=200, content_type="text/xml")

def getPaperPdf(request):
    id = int(request.GET.get('articleId'))
    article = Paper.objects.get(id=id, deleted=False,status='4')
    #convert to pdf
    return HttpResponse()
#####################################


#SCHEMAS###############
def getPaperSchema(request):#DONE
    sch = Schema.objects.get(name="paper")
    return HttpResponse(content=sch.text, status_code=200, content_type="text/xml")

def getRevisionSchema(request):#DONE
    sch = Schema.objects.get(name="revision")
    return HttpResponse(content=sch.text, status_code=200, content_type="text/xml")

def getLetterSchema(request):#DONE
    sch = Schema.objects.get(name="letter")
    return HttpResponse(content=sch.text, status_code=200, content_type="text/xml")
    
def getQuestionnaireSchema(request):#DONE
    sch = Schema.objects.get(name="questionnaire")
    return HttpResponse(content=sch.text, status_code=200, content_type="text/xml")
######################

#LOGIN/REGISTER##########
def loginF(request):#DONE
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
    else:
        return HttpResponse(status_code=400)

@csrf_exempt
def registerF(request):#DONE
    username = request.POST['username']
    password = request.POST['password']
    email = request.POST['email']
    name = request.POST['name']
    surname = request.POST['surname']
    ser = User.objects.create_user(username, email, password, first_name=name, last_name =surname)
    groupR, created = Group.objects.get_or_create(name='reviewer')
    groupA, created = Group.objects.get_or_create(name='author')
    ser.groups.add(groupA)
    ser.groups.add(groupR)
    ser.save()
    
def logoutF(request):#DONE
    logout(request)

def loginP(request):#DONE
    template = loader.get_template("static/login.html")
    return HttpResponse(template.render())

def registerP(request):#DONE
    template = loader.get_template("static/register.html")
    return HttpResponse(template.render())
##########################