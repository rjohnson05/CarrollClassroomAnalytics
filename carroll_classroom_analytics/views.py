import logging

from django.shortcuts import render
from rest_framework.request import Request
from rest_framework.response import Response

logger = logging.getLogger("index_views")

"""
Contains the frontend views for the Carroll College analytics software. None of these views contain any logic. These 
methods receive HTTP requests and then pass the request to the front end router for display.

Author: Ryan Johnson
"""


def index(request: Request) -> Response:
    """
    Forwards the request to the React router, displaying the correct page.
    """
    logger.debug(f"index - Request: {request}")
    return render(request, "build/index.html")


def index_with_classroom(request: Request, classroom) -> Response:
    """
    Forwards the request to the React router, passing the classroom variable along.
    """
    logger.debug(f"index_with_classroom - Classroom: {classroom}, Request: {request}")
    return render(request, "build/index.html", {"classroom": classroom})
