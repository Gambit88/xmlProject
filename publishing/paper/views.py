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

from paper.models import Paper,Recension,Questionnaire,Schema

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
def uploadPage(request):#TOTALY DONE
    template = loader.get_template("writePaperPage.html")
    publisherList = User.objects.filter(groups__name='publisher')
    return HttpResponse(template.render({'publishers':publisherList,'rewrite':False, 'user':request.user}))

@login_required(login_url="/paper/loginPage")
@permission_required('paper.add_paper')
def rewritePage(request,paper_id):#TOTALY DONE
    paper = Paper.objects.get(id=paper_id,author__id=request.user.id)

    publisherList = []
    publisherList.append(paper.publisher)

    template = loader.get_template("writePaperPage.html")
    return HttpResponse(template.render({'publishers':publisherList, 'paper':paper,'rewrite':True, 'user':request.user}))

@login_required(login_url="/paper/loginPage")
@permission_required('paper.add_paper')
@csrf_exempt
def upload(request):#TOTALY DONE
    paperFile = request.FILES['paper']
    letterFile = request.FILES['letter']

    paper_id = request.POST.get('paper_id')

    sch = Schema.objects.get(name="paper")
    schema = sch.text
    schema_doc = etree.fromstring(schema)
    xmlschema = etree.XMLSchema(schema_doc)

    paperDoc = etree.parse(paperFile)
    if xmlschema.validate(paperDoc)==False:
        return redirect('/paper/writePaper/')#dokument ne odgovara semi
    
    sch = Schema.objects.get(name="letter")
    schema = sch.text
    schema_doc = etree.fromstring(schema)
    xmlschema = etree.XMLSchema(schema_doc)

    doc = etree.parse(letterFile)
    if xmlschema.validate(doc)==False:
        return redirect('/paper/writePaper/')#pismo ne odgovara semi
    
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

    if paper_id=="":
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
    return redirect('/paper/myPapers/') 

@login_required(login_url="/paper/loginPage")
@permission_required('paper.add_paper')
@csrf_exempt
def pullPaper(request,paper_id):#TOTALY DONE
    try:
        article = Paper.objects.get(id=paper_id)
        article.deleted = True
        article.save()
        return redirect('/paper/myPapers/')
    except :
        return redirect('/paper/myPapers/')

@login_required(login_url="/paper/loginPage")
@permission_required('paper.add_paper')
def myPapers(request):#TOTALY DONE
    template = loader.get_template("myPapersPage.html")
    try:
        searchType = request.GET.get('type')
        if searchType=="t":
            searchContent = request.GET.get('text')
            papers = Paper.objects.filter(author__id = request.user.id,deleted=False,text__contains=searchContent).defer("text")
            return HttpResponse(template.render({'papers':papers,'user':request.user,'types':Paper.Type_CHOICES}))
        else:
            searchTitle = request.GET.get('title',"")
            searchStatus = request.GET.get('status',"")
            searchPublisher = request.GET.get('publisher',"")
            searchPaper = request.GET.get('paperType',"")
            searchKeywords = request.GET.get('keywords',"")
            papers = Paper.objects.filter(author__id = request.user.id,deleted=False,title__iregex=searchTitle,status__iregex=searchStatus,publisher__last_name__iregex=searchPublisher,paper_type__iregex=searchPaper).defer("text")
            if searchKeywords!="":
                for keyword in str(searchKeywords).split(','):
                    papers = papers.filter(keywords__contains=keyword)
            return HttpResponse(template.render({'papers':papers,'user':request.user,'types':Paper.Type_CHOICES}))
    except:
        papers = Paper.objects.filter(author__id = request.user.id,deleted=False).defer("text")
        return HttpResponse(template.render({'papers':papers,'user':request.user,'types':Paper.Type_CHOICES}))

@login_required(login_url="/paper/loginPage")
def revision(request,paper_id):
    article = Paper.objects.get(id=paper_id)
    if article.author.id == request.user.id or article.publisher.id == request.user.id:
        root = etree.Element("allReviews")
        for rev in article.recension.all():
            root.append(etree.fromstring(rev.text))  
        return HttpResponse(content=etree.tostring(root),status=200, content_type="text/xml")
    else:
        return redirect('/paper/searchPapers/')
    
#######################################################################

#REVISION CCONTROL######################################
@login_required(login_url="/paper/loginPage")
@permission_required('paper.add_recension')
def pendingRevisions(request):#TOTALY DONE
    template = loader.get_template("pendingRevisionsPage.html")
    rev = Paper.objects.filter(reviewer__username=request.user.username)
    try:
        utest = User.objects.get(id=request.user.id,groups__name='publisher')
        a = False
    except:
        a = True
    return HttpResponse(template.render({'papers':rev, 'user':request.user, 'showPaper':a}))

@login_required(login_url="/paper/loginPage")
@permission_required('paper.add_recension')
@csrf_exempt
def refuseRevision(request,paper_id):#TOTALY DONE
    id = paper_id
    article = Paper.objects.get(id=id)
    article.rec_total = article.rec_total-1
    article.reviewer.remove(request.user)
    article.save()
    _thread.start_new_thread(sendEmail,(article.publisher.email,"User "+ request.user.first_name + " " + request.user.last_name +" has refused revision","Refused revision of " + str(article.title)))
    return redirect('/paper/pendingRevisions/')

@login_required(login_url="/paper/loginPage")
@permission_required('paper.add_recension')
def revisionPage(request,paper_id):#TOTALY DONE
    template = loader.get_template("revisionPage.html")
    id = paper_id
    article = Paper.objects.get(id=id, reviewer__id=request.user.id)
    try:
        utest = User.objects.get(id=request.user.id,groups__name='publisher')
        a = False
    except:
        a = True
    questionnaire = Questionnaire.objects.get(paper__id=article.id,reviewer__id=request.user.id)
    return HttpResponse(template.render({'paper':article, 'questionnaire':questionnaire, 'user':request.user, 'showPaper':a}))

@login_required(login_url="/paper/loginPage")
@permission_required('paper.add_recension')
@csrf_exempt
def uploadRevision(request):#TOTALY DONE
    revFile = request.FILES['rev']
    questFile = request.FILES['quest']
    letterFile = request.FILES['letter']
    
    paper_id = request.POST.get('paper_id')
    q_id = request.POST.get('q_id')
    
    sch = Schema.objects.get(name="revision")
    schema = sch.text
    schema_doc = etree.fromstring(schema)
    xmlschema = etree.XMLSchema(schema_doc)

    revDoc = etree.parse(revFile)
    if xmlschema.validate(revDoc)==False:
        return redirect('/paper/reviewPaper/'+paper_id)#revizija ne odgovara semi

    sch = Schema.objects.get(name="questionnaire")
    schema = sch.text
    schema_doc = etree.fromstring(schema)
    xmlschema = etree.XMLSchema(schema_doc)

    questDoc = etree.parse(questFile)
    if xmlschema.validate(questDoc)==False:
        return redirect('/paper/reviewPaper/'+paper_id)#upitnik ne odgovara semi
    
    sch = Schema.objects.get(name="letter")
    schema = sch.text
    schema_doc = etree.fromstring(schema)
    xmlschema = etree.XMLSchema(schema_doc)

    doc = etree.parse(letterFile)
    if xmlschema.validate(doc)==False:
        return redirect('/paper/reviewPaper/'+paper_id)#pismo ne odgovara semi
    
    q = etree.tostring(questDoc).decode('UTF-8')
    rev = etree.tostring(revDoc).decode('UTF-8')
    message = etree.tostring(doc).decode('UTF-8')
    
    article = Paper.objects.get(id=paper_id)
    questionnaire = Questionnaire.objects.get(id=q_id,reviewer__id=request.user.id,paper__id=paper_id)
    questionnaire.text=q
    questionnaire.save()
    rr = Recension()
    rr.text = rev
    rr.save()
    article.recension.add(rr)
    article.rec_completed = article.rec_completed+1
    article.reviewer.remove(request.user)
    article.save()
    return  redirect('/paper/pendingRevisions/')

@login_required(login_url="/paper/loginPage")
@permission_required('paper.add_recension')
def getQu(request,q_id):
    article = Questionnaire.objects.get(id=q_id,reviewer__id=request.user.id)
    text = article.text
    return HttpResponse(content=text,status=200, content_type="text/xml")

@login_required(login_url="/paper/loginPage")
def checkQu(request,paper_id):
    articles = Questionnaire.objects.filter(paper__id=paper_id)
    paper = Paper.objects.get(id=paper_id)
    if paper.publisher.id == request.user.id:
        root = etree.Element("allQuestionnaires")
        for rev in articles:
            root.append(etree.fromstring(rev.text))  
        return HttpResponse(content=etree.tostring(root),status=200, content_type="text/xml")
    else:
        return redirect('/paper/searchPapers/')
#######################################################

#PUBLISHER CONTROL##################
@login_required(login_url="/paper/loginPage")
@permission_required('paper.can_publish')
def submitedPapersPage(request):#TOTALY DONE
    template = loader.get_template("submitedPapersPage.html")
    articles = Paper.objects.filter(publisher__id = request.user.id,deleted=False)
    return HttpResponse(template.render({'papers':articles, 'user':request.user}))

@login_required(login_url="/paper/loginPage")
@permission_required('paper.can_publish')
def appointRevisionPage(request,paper_id):#TOTALY DONE, No time for suggested
    template = loader.get_template("appointRevisionPage.html")
    article = Paper.objects.get(id=paper_id)
    object_id_list = []
    object_id_list.append(request.user.id)
    object_id_list.append(article.author.id)
    for user in article.reviewer.all():
        object_id_list.append(user.id)
    reviewers = User.objects.filter(groups__name='reviewer').exclude(id__in=object_id_list)
    if article.publisher.id == request.user.id:
        return HttpResponse(template.render({'paper':article,'reviewers':reviewers, 'user':request.user}))
    return redirect("/paper/submitedPapers")

@login_required(login_url="/paper/loginPage")
@permission_required('paper.can_publish')
@csrf_exempt
def appointRevision(request):#TOTALY DONE
    questFile = request.FILES['quest']
    letterFile = request.FILES['letter']
    try:
        paper_id = request.POST.get('paper_id')
    except:
        paper_id = None
    sch = Schema.objects.get(name="questionnaire")
    schema = sch.text
    schema_doc = etree.fromstring(schema)
    xmlschema = etree.XMLSchema(schema_doc)

    questDoc = etree.parse(questFile)
    if xmlschema.validate(questDoc)==False:
        return redirect('/paper/writePaper/')#upitnik ne odgovara semi
    
    sch = Schema.objects.get(name="letter")
    schema = sch.text
    schema_doc = etree.fromstring(schema)
    xmlschema = etree.XMLSchema(schema_doc)

    doc = etree.parse(letterFile)
    if xmlschema.validate(doc)==False:
        return redirect('/paper/writePaper/')#pismo ne odgovara semi
    
    message = etree.tostring(doc).decode('UTF-8')
    content = etree.tostring(questDoc).decode('UTF-8')

    userId = request.POST.get('userId')
    user = User.objects.get(username=userId)
    paper_id = request.POST.get('paper_id')
    article = Paper.objects.get(id=paper_id)
    article.rec_total = article.rec_total+1
    article.reviewer.add(user)
    article.save()
    questionnaire = Questionnaire()
    questionnaire.paper = article
    questionnaire.reviewer = user
    questionnaire.text = content
    questionnaire.save()
    _thread.start_new_thread(sendEmail, (article.publisher.email,message,"Receved revision request for " + str(article.title)))
    return redirect("/paper/appointingRevisions/"+str(paper_id))

@login_required(login_url="/paper/loginPage")
@permission_required('paper.can_manage')
@csrf_exempt
def setAcceptedState(request,paper_id):#DONE
    article = Paper.objects.get(id=paper_id,publisher__id=request.user.id)
    article.status = '4'
    article.save()
    return redirect("/paper/submitedPapers")

@login_required(login_url="/paper/loginPage")
@permission_required('paper.can_manage')
@csrf_exempt
def setRefusedState(request,paper_id):#DONE
    article = Paper.objects.get(id=paper_id,publisher__id=request.user.id)
    article.status = '3'
    article.save()
    return redirect("/paper/submitedPapers")

@login_required(login_url="/paper/loginPage")
@permission_required('paper.can_manage')
@csrf_exempt
def setRevisionState(request,paper_id):#DONE
    article = Paper.objects.get(id=paper_id,publisher__id=request.user.id)
    article.status = '1'
    article.save()
    return redirect("/paper/submitedPapers")

@login_required(login_url="/paper/loginPage")
@permission_required('paper.can_manage')
@csrf_exempt
def setWritingState(request,paper_id):#DONE
    article = Paper.objects.get(id=paper_id,publisher__id=request.user.id)
    article.status = '2'
    article.save()
    return redirect("/paper/submitedPapers")
#######################################

#PUBLIC#################################
def searchPage(request):#TOTALY DONE (I HOPE)
    template = loader.get_template("searchPapersPage.html")
    try:
        utest = User.objects.get(id=request.user.id,groups__name='publisher')
        a = False
    except:
        a = True
    try:
        searchType = request.GET.get('type')
        if searchType=="t":
            searchContent = request.GET.get('text')
            papers = Paper.objects.filter(status='4',deleted=False,text__contains=searchContent).defer("text")
            return HttpResponse(template.render({'papers':papers,'user':request.user,'logedIn':request.user.is_authenticated, 'showPaper':a}))
        else:
            searchTitle = request.GET.get('title',"")
            searchAuthor = request.GET.get('author',"")
            searchPublisher = request.GET.get('publisher',"") 
            searchPaper = request.GET.get('paperType',"")
            searchKeywords = request.GET.get('keywords',"") 
            papers = Paper.objects.filter(status='4',deleted=False,title__iregex=searchTitle,author__last_name__iregex=searchAuthor,publisher__last_name__iregex=searchPublisher,paper_type__iregex=searchPaper).defer("text")
            if searchKeywords!="":
                for keyword in str(searchKeywords).split(','):
                    papers = papers.objects.filter(keywords__contains=keyword)
            return HttpResponse(template.render({'papers':papers,'user':request.user,'logedIn':request.user.is_authenticated, 'showPaper':a}))
    except:
        papers = Paper.objects.filter(status='4',deleted=False).defer("text")
        return HttpResponse(template.render({'papers':papers,'user':request.user,'logedIn':request.user.is_authenticated, 'showPaper':a}))
    

def getPaper(request,paper_id):
    template = loader.get_template("viewPaperPage.html")
    article = Paper.objects.get(id=paper_id, deleted=False,status='4')
    #convert to html

    return HttpResponse(template.render({}))

def getPaperXml(request,paper_id):#TOTALY DONE
    try:
        article = Paper.objects.get(id=paper_id, deleted=False,status='4')
        text = article.text
        return HttpResponse(content=text,status=200, content_type="text/xml")
    except:
        article = Paper.objects.get(id=paper_id, deleted=False)
        if article.status=='1':
            for user in article.reviewer.all():
                if user.id==request.user.id:
                    doc = etree.fromstring(article.text)
                    for el in doc.iter('{*}name'):
                        el.text = ""
                    for el in doc.iter('{*}institute'):
                        el.text = ""
                    text = etree.tostring(doc).decode('UTF-8')
                    return HttpResponse(content=text,status=200, content_type="text/xml")
        if article.author.id == request.user.id or article.publisher.id == request.user.id:
            text = article.text
            return HttpResponse(content=text,status=200, content_type="text/xml")
        return redirect('/paper/searchPapers/')
    

def getPaperPdf(request,paper_id):
    article = Paper.objects.get(id=paper_id, deleted=False,status='4')
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