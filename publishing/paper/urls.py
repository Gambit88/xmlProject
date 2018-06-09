"""publishing URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^writePaper', views.uploadPage, name = "writePaperPage"),
    url(r'^submitPaper', views.upload, name = "submitPaper"),
    url(r'^reviewPaper', views.revisionPage, name = "revisionPage"),
    url(r'^submitReview', views.uploadRevision, name = "submitReview"),
    url(r'^pullPaper', views.pullPaper, name = "pullPaper"),
    url(r'^searchPapers', views.searchPage, name = "searchPapersPage"),
    url(r'^myPapers', views.myPapers, name = "myPapersPage"),
    url(r'^viewPaper', views.getPaper, name = "viewPaperPage"),
    url(r'^getPaperXml', views.getPaperXml, name = "getPaperXml"),
    url(r'^getPaperPdf', views.getPaperPdf, name = "getPaperPdf"),
    url(r'^pendingRevisions', views.pendingRevisions, name = "pendingRevisionsPage"),
    url(r'^acceptRevision', views.acceptRevision, name = "acceptRevision"),
    url(r'^refuseRevision', views.refuseRevision, name = "refuseRevision"),
    url(r'^submitedPapers', views.submitedPapersPage, name = "sumbitedPapersPage"),
    url(r'^appointingRevisions', views.appointRevisionPage, name = "appointRevisionPage"),
    url(r'^appointRevision', views.appointRevision, name = "appointRevision"),
    url(r'^managePublications', views.managePage, name = "managePublicationsPage"),
    url(r'^setAcceptedState', views.setAcceptedState, name = "setAcceptedState"),
    url(r'^setRefusedState', views.setRefusedState, name = "setRefusedState"),
    url(r'^setRevisionState', views.setRevisionState, name = "setRevisionState"),
    url(r'^setWritingState', views.setWritingState, name = "setWritingState"),
    url(r'^ArticleSchema', views.getPaperSchema, name = "ArticleSchema"),
    url(r'^RevisionSchema', views.getRevisionSchema, name = "RevisionSchema"),
    url(r'^LetterSchema', views.getLetterSchema, name = "LetterSchema"),
    url(r'^QuestionnaireSchema', views.getQuestionnaireSchema, name = "QuestionnaireSchema"),
]
