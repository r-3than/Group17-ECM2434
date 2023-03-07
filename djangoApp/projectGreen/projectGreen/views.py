from sre_constants import SUCCESS
from django.http import HttpResponse
from microsoft_authentication.auth.auth_decorators import microsoft_login_required
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import base64 , json

from projectGreen.models import Submission



@csrf_exempt
def uploadphoto(request):
     if request.method == "POST":
        data=json.loads(request.body)
        print(data)
        img_data = data["img"]
        img_data = base64.b64decode(img_data.split(",")[1])
        with open(str(request.user)+".png", "wb") as fh:
            fh.write(img_data)
        return HttpResponse({"success":"true"})

def home(request):
    context = {}
    if request.user.is_authenticated:
        template = loader.get_template('home/home2.html')

        submissions_info = {}
        submissions = Submission.objects.all()
        for submission in submissions:
            submissions_info[submission.id] = {'submission_username': submission.username,
                                               'submission_minutes_late': submission.minutes_late,
                                               'submission_photo': submission.photo_bytes,
                                               'submission_upvote_count': submission.get_upvote_count()
                                            }
        
        context['submissions'] = submissions_info

        print(submissions_info)
        return HttpResponse(template.render(context, request))
    else:
        print("Not signed in")
        template = loader.get_template('home/sign-in.html')
        return HttpResponse(template.render(context, request))
    
def challenge(request):
    context = {}
    if request.user.is_authenticated:
        template = loader.get_template('home/challenge.html')
        return HttpResponse(template.render(context, request))
    else:
        print("Not signed in")
        template = loader.get_template('home/sign-in.html')
        return HttpResponse(template.render(context, request))
    

def camera(request):
    template = loader.get_template('camera/camera.html')
    context = {}
    return HttpResponse(template.render(context, request))

# If pages need to be restricted to certain groups of users.
@microsoft_login_required(groups=("SpecificGroup1", "SpecificGroup2"))  # Add here the list of Group names
def specific_group_access(request):
    return HttpResponse("You are accessing page which is accessible only to users belonging to SpecificGroup1 or SpecificGroup2")
