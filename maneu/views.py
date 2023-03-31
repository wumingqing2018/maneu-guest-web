from django.shortcuts import HttpResponseRedirect, reverse, render


def index(request):
    return render(request, 'maneu/index.html')
