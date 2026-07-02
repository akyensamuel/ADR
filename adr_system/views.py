from django.shortcuts import render


def home(request):
    return render(request, 'adr_system/home.html')