from django import shortcuts
from django.shortcuts import render
from django.conf import settings


def index(request):
    return shortcuts.redirect(settings.WEBROOT)
