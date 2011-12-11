# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext

from .models import Shortcut

from time import sleep

def index(request):
    context = RequestContext(request, {})
    return render_to_response('layout.html', context_instance = context)

def redirection(request, shortcut):
    shortcut = get_object_or_404(Shortcut, shortcut = shortcut)
    shortcut.bump_use_count()
    return redirect(shortcut.url, permanent = True)

