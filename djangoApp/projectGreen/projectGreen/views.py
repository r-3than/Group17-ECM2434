import datetime
import os
from sre_constants import SUCCESS
import time
from django.http import HttpResponse
from django.shortcuts import redirect

from microsoft_authentication.auth.auth_decorators import microsoft_login_required
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import base64 , json
from datetime import date, timedelta

from projectGreen.models import ActiveChallenge, Profile, Submission, Upvote



@csrf_exempt
def uploadphoto(request):
     if request.method == "POST":
        if request.user.is_authenticated:
            upload=request.FILES["upload_pic"]
            picture_bytes = b""
            for data in upload:
                picture_bytes += data
            active_challenge = ActiveChallenge.objects.last() ## -> 
            newSubmission = Submission(username=request.user.username,
            active_challenge=active_challenge,
            reported=False,
            reviewed=False,
            photo_bytes=picture_bytes,
            submission_time=datetime.datetime.now())
            newSubmission.save()
        return redirect('/home/')
        """
        data=json.loads(request.body)
        print(data)
        img_data = data["img"]
        img_data = base64.b64decode(img_data.split(",")[1])
        with open(str(request.user)+".png", "wb") as fh:
            fh.write(img_data)
        return HttpResponse({"success":"true"})
        """

@csrf_exempt
def like_submission(request):
     if request.method == "POST":
        if request.user.is_authenticated:
            data=json.loads(request.body)
            submission_id = data["submission_id"]
            checker = Upvote.objects.filter(voter_username=request.user.username,
                submission_id=submission_id)
            if len(checker) < 1:
                SubmissionObj = Submission.objects.filter(id=submission_id).first()
                SubmissionObj.create_upvote(request.user.username)
            else:
                checker.first().remove_upvote()
        return HttpResponse({"success":"true"})


def home(request):
    context = {}
    if request.user.is_authenticated:
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
            if submission.photo_bytes != None:
                photo_b64 = "data:image/png;base64,"+base64.b64encode(submission.photo_bytes).decode("utf-8")
            else:
                photo_b64 = "data:image/png;base64,"
            # Dictionary structure to pass to template 
            checker = Upvote.objects.filter(voter_username=request.user.username,
                submission_id=submission.id)
            if len(checker) >= 1:
                has_liked = 1
            else:
                has_liked = 0
            profileObj = Profile.objects.filter(id=request.user.id).first()
            user_points = str(profileObj.points)
            context["user_points"] = user_points
            submissions_info[submission.id] = {
                                               'submission_id' :submission.id,
                                               'submission_username': submission.username,
                                               'submission_time': submission_time_form,
                                               'submission_photo': photo_b64,
                                               'submission_upvote_count': submission.get_upvote_count(),
                                               'submission_comment_count': submission.get_comment_count(),
                                               'submission_has_liked': has_liked,
                                            }
        
        context['submissions'] = submissions_info

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


def submit(request):
    context = {}
    if request.user.is_authenticated:
        template = loader.get_template('camera/submit.html')  
        return HttpResponse(template.render(context, request))
    else:
        print("Not signed in")
        template = loader.get_template('home/sign-in.html')
        return HttpResponse(template.render(context, request))
    

def is_mobile(request):
    MOBILE_AGENT_RE=re.compile(r".*(iphone|mobile|androidtouch)",re.IGNORECASE)

    if MOBILE_AGENT_RE.match(request.META['HTTP_USER_AGENT']):
        return True
    else:
        return False

# If pages need to be restricted to certain groups of users.
@microsoft_login_required(groups=("SpecificGroup1", "SpecificGroup2"))  # Add here the list of Group names
def specific_group_access(request):
    return HttpResponse("You are accessing page which is accessible only to users belonging to SpecificGroup1 or SpecificGroup2")
