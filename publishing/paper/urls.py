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
    url(r'^writePaper/', views.uploadPage, name="writePaperPage"),
    url(r'^rewritePaper/(?P<paper_id>\d+)',
        views.rewritePage, name="reWritePaperPage"),
    url(r'^submitPaper/', views.upload, name="submitPaper"),
    url(r'^submitReview/', views.uploadRevision, name="submitReview"),
    url(r'^pullPaper/(?P<paper_id>\d+)', views.pullPaper, name="pullPaper"),
    url(r'^searchPapers/', views.searchPage, name="searchPapersPage"),
    url(r'^myPapers/', views.myPapers, name="myPapersPage"),
    url(r'^viewPaper/(?P<paper_id>\d+)', views.getPaper, name="viewPaperPage"),
    url(r'^getPaperXml/(?P<paper_id>\d+)',
        views.getPaperXml, name="getPaperXml"),
    url(r'^getPaperPdf/(?P<paper_id>\d+)',
        views.getPaperPdf, name="getPaperPdf"),
    url(r'^pendingRevisions/', views.pendingRevisions, name="pendingRevisionsPage"),
    url(r'^reviewPaper/(?P<paper_id>\d+)',
        views.revisionPage, name="revisionPage"),
    url(r'^refuseRevision/', views.refuseRevision, name="refuseRevision"),

    url(r'^submitedPapers/', views.submitedPapersPage, name="sumbitedPapersPage"),
    url(r'^appointingRevisions/(?P<paper_id>\d+)', views.appointRevisionPage,
        name="appointRevisionPage"),
    url(r'^appointRevision/', views.appointRevision, name="appointRevision"),
    url(r'^setAcceptedState/(?P<paper_id>\d+)', views.setAcceptedState, name="setAcceptedState"),
    url(r'^setRefusedState/(?P<paper_id>\d+)', views.setRefusedState, name="setRefusedState"),
    url(r'^setRevisionState/(?P<paper_id>\d+)', views.setRevisionState, name="setRevisionState"),
    url(r'^setWritingState/(?P<paper_id>\d+)', views.setWritingState, name="setWritingState"),

    url(r'^ArticleSchema/', views.getPaperSchema, name="ArticleSchema"),
    url(r'^RevisionSchema/', views.getRevisionSchema, name="RevisionSchema"),
    url(r'^LetterSchema/', views.getLetterSchema, name="LetterSchema"),
    url(r'^QuestionnaireSchema/', views.getQuestionnaireSchema,
        name="QuestionnaireSchema"),

    url(r'^login/', views.loginF, name="login"),
    url(r'^register/', views.registerF, name="register"),
    url(r'^logout/', views.logoutF, name="logout"),
    url(r'^loginPage/', views.loginP, name="loginP"),
    url(r'^registerPage/', views.registerP, name="registerP"),
]
