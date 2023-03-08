from sre_constants import SUCCESS
from django.http import HttpResponse
from microsoft_authentication.auth.auth_decorators import microsoft_login_required
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import base64 , json
from datetime import date, timedelta

from projectGreen.models import Submission

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
<<<<<<< HEAD
        template = loader.get_template('home/home2.html')

        submissions_info = {}
        submissions = Submission.objects.all()
        for submission in submissions:
            submissions_info[submission.id] = {'submission_username': submission.username,
                                               'submission_minutes_late': submission.minutes_late,
=======
        template = loader.get_template('home/home.html')

        submissions_info = {}

        # List the submissions from most recent
        submissions = Submission.objects.all().order_by('-submission_time')
        for submission in submissions:
            submission_date = submission.submission_time.strftime("%d:%m:%Y")
            submission_year = submission.submission_time.strftime("%Y")
            current_date = date.today().strftime("%d:%m:%Y")
            current_year = date.today().strftime("%Y")

            # Only display submission year if different from current year
            if submission_year != current_year:
                submission_time_form = submission.submission_time.strftime("%B %d, %Y")
            # Only display submission date if different from current date
            elif submission_date != current_date:
                # Display "Yesterday" if submission is from previous day
                if current_date == (submission.submission_time + timedelta(days = 1)).strftime("%d:%m:%Y"):
                    submission_time_form = submission.submission_time.strftime("Yesterday, %H:%M")
                # Display actual date otherwise
                else:
                    submission_time_form = submission.submission_time.strftime("%B %d, %H:%M")
            else:
                submission_time_form = submission.submission_time.strftime("%H:%M")

            # Dictionary structure to pass to template 
            submissions_info[submission.id] = {'submission_username': submission.username,
                                               'submission_time': submission_time_form,
>>>>>>> a435eef25957e24b02fcb45b6477a2dd4c12d10a
                                               'submission_photo': submission.photo_bytes,
                                               'submission_upvote_count': submission.get_upvote_count()
                                            }
        
        context['submissions'] = submissions_info

<<<<<<< HEAD
        print(submissions_info)
=======
>>>>>>> a435eef25957e24b02fcb45b6477a2dd4c12d10a
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
