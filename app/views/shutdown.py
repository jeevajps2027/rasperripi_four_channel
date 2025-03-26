from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import signal
import sys
import threading

# Use the same stop_event from PyQt5 code
from managetest import stop_event

@csrf_exempt
def shutdown(request):
    if request.method == 'POST':
        try:
            # Set the stop_event to trigger server shutdown
            stop_event.set()

            # Return success response
            return JsonResponse({'status': 'success', 'message': 'Server shutting down...'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)




