from django.shortcuts import render


def index(request):
    """
    Returns the index page of the React front end, serving the Django backend and React frontend together
    """
    return render(request, "build/index.html")
