from django.shortcuts import render,redirect
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth.models import User,Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.csrf import csrf_exempt

from io import StringIO,BytesIO
from lxml import etree
import _thread

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from paper.models import Paper,Recension,Questionnaire,Schema,Qlog

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
def rewritePage(request,paper_id):#DONE
    paper = Paper.objects.get(id=paper_id,author__id=request.user.id)
    text = paper.text
    template = loader.get_template("writePaperPage.html")
    publisherList = User.objects.filter(groups__name='publisher')
    return HttpResponse(template.render({'text':text}))

@login_required(login_url="/paper/loginPage")
@permission_required('paper.add_paper')
@csrf_exempt
def upload(request):#TOTALY DONE
    paperFile = request.FILES['paper']
    letterFile = request.FILES['letter']
    try:
        paper_id = request.POST.get('paper_id')
    except:
        paper_id = None
    sch = Schema.objects.get(name="paper")
    schema = sch.text
    schema_doc = etree.fromstring(schema)
    xmlschema = etree.XMLSchema(schema_doc)

    paperDoc = etree.parse(paperFile)
    if xmlschema.validate(paperDoc)==False:
        return HttpResponse(status=400)#dokument ne odgovara semi
    
    sch = Schema.objects.get(name="letter")
    schema = sch.text
    schema_doc = etree.fromstring(schema)
    xmlschema = etree.XMLSchema(schema_doc)

    doc = etree.parse(letterFile)
    if xmlschema.validate(doc)==False:
        return HttpResponse(status=400)#pismo ne odgovara semi
    
    message = etree.tostring(doc).decode('UTF-8')
    content = etree.tostring(paperDoc).decode('UTF-8')

    titles = ""
    for el in paperDoc.iter('{*}title'):
        titles = titles + '-' + el.text 
    title = titles.split('-')[1]

    keywords = ""
    for el in paperDoc.iter('{*}keyword'):
        keywords = keywords + ' ' + el.text 
    keywords = keywords.strip()
    
    paper_type = ""
    for el in paperDoc.iter('{*}article'):
        paper_type = el.attrib['classification']

    if paper_id==None:
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
    else:
        paper = Paper.objects.get(id=paper_id)
        paper.title = title
        paper.status = '0'
        paper.text = content
        paper.paper_type = paper_type
        paper.keywords = keywords
        paper.save()
        _thread.start_new_thread(sendEmail,(paper.publisher.email,message,"Rewriting "+title))
    
    template = loader.get_template("static/completedPaper.html")
    return HttpResponse(template.render())    

@login_required(login_url="/paper/loginPage")
@permission_required('paper.add_paper')
@csrf_exempt
def pullPaper(request,paper_id):#DONE
    try:
        article = Paper.objects.get(id=paper_id)
        article.deleted = True
        article.save()
        return HttpResponse(status=200)
    except :
        return HttpResponse(status=400)

@login_required(login_url="/paper/loginPage")
@permission_required('paper.add_paper')
def myPapers(request):#DONE
    template = loader.get_template("myPapersPage.html")
    try:
        searchType = request.GET.get('type')
        if searchType=="t":
            searchContent = request.GET.get('text')
            papers = Paper.objects.filter(author__id = request.user.id,deleted=False,text__contains=searchContent).defer("text")
            return HttpResponse(template.render({'papers':papers,'user':request.user,'types':Paper.Type_CHOICES}))
        else:
            searchTitle = request.GET.get('title')
            searchStatus = request.GET.get('status')
            searchPublisher = request.GET.get('publisher')
            searchPaper = request.GET.get('paperType')
            searchKeywords = request.GET.get('keywords')
            papers = Paper.objects.filter(author__id = request.user.id,deleted=False,title__iregex=searchTitle,status__iregex=searchStatus,publisher__last_name__iregex=searchPublisher,paper_type=searchPaper).defer("text")
            for keyword in str(searchKeywords).split(','):
                papers = papers.objects.filter(keywords__contains=keyword)
            return HttpResponse(template.render({'papers':papers,'user':request.user,'types':Paper.Type_CHOICES}))
    except:
        papers = Paper.objects.filter(author__id = request.user.id,deleted=False).defer("text")
        return HttpResponse(template.render({'papers':papers,'user':request.user,'types':Paper.Type_CHOICES}))
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
        return HttpResponse(status=400)#poruka ne odgovara semi
    id = int(request.POST.get('articleId'))
    article = Paper.objects.get(id=id)
    article.rec_total = article.rec_total-1
    article.reviewer.remove(request.user)
    article.save()
    _thread.start_new_thread(sendEmail,(article.publisher.email,message,"Refused revision of " + str(article.title)))
    return HttpResponse(status=200)

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
        return HttpResponse(status=400)#revizija ne odgovara semi
    sch = Schema.objects.get(name="questionnaire")
    schema = StringIO(sch.text)
    schema_doc = etree.parse(schema)
    xmlschema = etree.XMLSchema(schema_doc)
    message = request.POST.get('questionnaire')
    doc = etree.parse(message)
    if xmlschema.validate(doc)==False:
        return HttpResponse(status=400)#upitinik ne odgovara semi
    
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
        return HttpResponse(status=400)#poruka ne odgovara semi
    id = int(request.POST.get('articleId'))
    userId = int(request.POST.get('userId'))
    user = User.objects.get(id=userId)
    article = Paper.objects.get(id=id).defer("text")
    article.rec_total = article.rec_total+1
    article.reviewer.add(user)
    article.save()
    _thread.start_new_thread(sendEmail, (article.publisher.email,message,"Receved revision request for " + str(article.title)))
    return HttpResponse(status=200)


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
    try:
        searchType = request.GET.get('type')
        if searchType=="t":
            searchContent = request.GET.get('text')
            papers = Paper.objects.filter(status='4',deleted=False,text__contains=searchContent).defer("text")
            return HttpResponse(template.render({'papers':papers,'user':request.user,'logedIn':request.user.is_authenticated}))
        else:
            searchTitle = request.GET.get('title')
            searchAuthor = request.GET.get('author')
            searchPublisher = request.GET.get('publisher')
            searchPaper = request.GET.get('paperType')
            searchKeywords = request.GET.get('keywords')
            papers = Paper.objects.filter(status='4',deleted=False,title__iregex=searchTitle,author__last_name__iregex=searchAuthor,publisher__last_name__iregex=searchPublisher,paper_type=searchPaper).defer("text")
            for keyword in str(searchKeywords).split(','):
                papers = papers.objects.filter(keywords__contains=keyword)
            return HttpResponse(template.render({'papers':papers,'user':request.user,'logedIn':request.user.is_authenticated}))
    except:
        papers = Paper.objects.filter(status='4',deleted=False).defer("text")
        return HttpResponse(template.render({'papers':papers,'user':request.user,'logedIn':request.user.is_authenticated}))
    

def getPaper(request,paper_id):
    template = loader.get_template("viewPaperPage.html")
    article = Paper.objects.get(id=paper_id, deleted=False,status='4')
    #convert to html

    return HttpResponse(template.render({}))

def getPaperXml(request,paper_id):#DONE
    id = int(request.GET.get('articleId'))
    article = Paper.objects.get(id=id, deleted=False,status='4')
    text = article.text
    return HttpResponse(content=text,status=200, content_type="text/xml")

def getPaperPdf(request,paper_id):
    id = int(request.GET.get('articleId'))
    article = Paper.objects.get(id=id, deleted=False,status='4')
    #convert to pdf
    return HttpResponse()
#####################################


#SCHEMAS###############
def getPaperSchema(request):#TOTALY DONE
    sch = Schema.objects.get(name="paper")
    return HttpResponse(content='<?xml version="1.0" encoding="UTF-8"?>\n' + sch.text, status=200, content_type="text/xml")

def getRevisionSchema(request):#TOTALY DONE
    sch = Schema.objects.get(name="revision")
    return HttpResponse(content='<?xml version="1.0" encoding="UTF-8"?>\n' + sch.text, status=200, content_type="text/xml")

def getLetterSchema(request):#TOTALY DONE
    sch = Schema.objects.get(name="letter")
    return HttpResponse(content='<?xml version="1.0" encoding="UTF-8"?>\n' + sch.text, status=200, content_type="text/xml")
    
def getQuestionnaireSchema(request):#TOTALY DONE
    sch = Schema.objects.get(name="questionnaire")
    return HttpResponse(content='<?xml version="1.0" encoding="UTF-8"?>\n' + sch.text, status=200, content_type="text/xml")
######################

#LOGIN/REGISTER##########
@csrf_exempt
def loginF(request):#TOTALY DONE
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('/paper/searchPapers/')
    else:
        return redirect('/paper/loginPage/')

@csrf_exempt
def registerF(request):#TOTALY DONE
    username = request.POST['username']
    password = request.POST['password']
    password2 = request.POST['password2']
    if(password!=password2):
        return redirect('/paper/registerPage')
    email = request.POST['email']
    name = request.POST['name']
    surname = request.POST['surname']
    if User.objects.filter(username=username).exists():
        return redirect('/paper/registerPage')
    ser = User.objects.create_user(username, email, password, first_name=name, last_name =surname)
    groupR, created = Group.objects.get_or_create(name='reviewer')
    groupA, created = Group.objects.get_or_create(name='author')
    ser.groups.add(groupA)
    ser.groups.add(groupR)
    ser.save()
    return redirect('/paper/loginPage')
    
def logoutF(request):#TOTALY DONE
    logout(request)
    return redirect('/paper/searchPapers')

def loginP(request):#TOTALY DONE
    template = loader.get_template("static/login.html")
    return HttpResponse(template.render())

def registerP(request):#TOTALY DONE
    template = loader.get_template("static/register.html")
    return HttpResponse(template.render())
##########################