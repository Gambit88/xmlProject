from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

# Create your views here.

def uploadPage(request):
    template = loader.get_template("writePaperPage.html")
    return HttpResponse(template.render({}))

def upload(request):
    pass

def revisionPage(request):
    template = loader.get_template("revisionPage.html")
    return HttpResponse(template.render({}))

def uploadRevision(request):
    pass

def pullPaper(request):
    pass

def searchPage(request):
    template = loader.get_template("searchPapersPage.html")
    return HttpResponse(template.render({}))

def myPapers(request):
    template = loader.get_template("myPapersPage.html")
    return HttpResponse(template.render({}))

def getPaper(request):
    template = loader.get_template("viewPaperPage.html")
    return HttpResponse(template.render({}))

def getPaperXml(request):
    pass

def getPaperPdf(request):
    pass

def pendingRevisions(request):
    template = loader.get_template("pendingRevisionsPage.html")
    return HttpResponse(template.render({}))

def acceptRevision(request):
    pass

def refuseRevision(request):
    pass

def submitedPapersPage(request):
    template = loader.get_template("submitedPapersPage.html")
    return HttpResponse(template.render({}))

def appointRevisionPage(request):
    template = loader.get_template("appointRevisionsPage.html")
    return HttpResponse(template.render({}))

def appointRevision(request):
    pass

def managePage(request):
    template = loader.get_template("managePublicationsPage.html")
    return HttpResponse(template.render({}))

def setAcceptedState(request):
    pass

def setRefusedState(request):
    pass

def setRevisionState(request):
    pass

def setWritingState(request):
    pass

def getPaperSchema(request):
    pass

def getRevisionSchema(request):
    pass

def getLetterSchema(request):
    pass
    
def getQuestionnaireSchema(request):
    pass