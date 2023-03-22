'''
Authors:
    ER
    LB
    TN
    OL
    JA
    OJ
'''

import datetime
import base64
import json

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt

from microsoft_authentication.auth.auth_decorators import microsoft_login_required

from projectGreen.models import ActiveChallenge, Friend, Profile, Submission, Upvote, Comment, StoreItem, OwnedItem

#region Pages

#region Initial Process


def signin(request):
    '''
    Displays the sign-in page
    '''
    context = {}
    template = loader.get_template('submit/sign-in.html')
    active_challenge = ActiveChallenge.get_last_active_challenge()
    context["active_challenge"] = active_challenge.get_challenge_description()
    return HttpResponse(template.render(context, request))

def challenge(request):
    '''
    Displays the page for the current challenge
    '''
    context = {}
    if request.user.is_authenticated:
        template = loader.get_template('submit/challenge.html')
        current_challenge =ActiveChallenge.get_last_active_challenge()
        if Submission.user_has_submitted(request.user.username):
            return redirect("/university-feed")
        context["active_challenge"] = current_challenge.get_challenge_description()
        user_profile = Profile.get_profile(request.user.username)
        user_points = str(user_profile.points)
        post_count= Friend.get_friend_post_count(user_profile.user.username,current_challenge)
        context["user_points"] = user_points
        context["post_count"] = post_count

        # Fetches user's profile picture
        item = OwnedItem.get_active_item_data(request.user.username)
        context["is_active"] = item["is_active"]
        context["profile_image"] = item["image"]
        context["text_colour"] = item["text"]

        return HttpResponse(template.render(context, request))
    else:
        return signin(request)

def submit(request):
    '''
    Displays the page where the user can submit a photo
    '''
    context = {}
    if request.user.is_authenticated:
        template = loader.get_template('submit/submit.html')

        active_challenge = ActiveChallenge.get_last_active_challenge()
        context["active_challenge"] = active_challenge.get_challenge_description()
        user_profile = Profile.get_profile(request.user.username)
        user_points = str(user_profile.points)
        post_count= Friend.get_friend_post_count(user_profile.user.username,active_challenge)
        context["user_points"] = user_points
        context["post_count"] = post_count

        # Fetches user's profile picture
        item = OwnedItem.get_active_item_data(request.user.username)
        context["is_active"] = item["is_active"]
        context["profile_image"] = item["image"]
        context["text_colour"] = item["text"]

        return HttpResponse(template.render(context, request))
    else:
        return signin(request)

#endregion

#region Feed

def university_feed(request):
    '''
    Displays the university-wide feed
    '''
    context = {}
    if request.user.is_authenticated:
        template = loader.get_template('feed/feed.html')

        submissions_info = {}
        user_profile = Profile.get_profile(request.user.username)
        user_points = str(user_profile.points)
        context["user_points"] = user_points
        # Fetches user's profile picture
        item = OwnedItem.get_active_item_data(request.user.username)
        context["is_active"] = item["is_active"]
        context["profile_image"] = item["image"]
        context["text_colour"] = item["text"]

        # List the submissions from most recent
        active_challenge = ActiveChallenge.get_last_active_challenge()
        context["active_challenge"] = active_challenge.get_challenge_description()
        if Submission.user_has_submitted(request.user.username):
            user_submission = Submission.objects.filter(active_challenge=active_challenge,username=request.user.username)
            submissions = Submission.objects.filter(active_challenge=active_challenge,reported=False).order_by('-sum_of_interactions').exclude(username=request.user.username)
            submissions = user_submission | submissions
        else:
            submissions = Submission.objects.filter(active_challenge=active_challenge,reported=False).order_by('-sum_of_interactions')

        for submission in submissions:
            submission_date = submission.submission_time.strftime("%d:%m:%Y")
            submission_year = submission.submission_time.strftime("%Y")
            current_date = datetime.date.today().strftime("%d:%m:%Y")
            current_year = datetime.date.today().strftime("%Y")

            # Only display submission year if different from current year
            if submission_year != current_year:
                submission_time_form = submission.submission_time.strftime("%B %d, %Y")
            # Only display submission date if different from current date
            elif submission_date != current_date:
                # Display "Yesterday" if submission is from previous day
                if current_date == (submission.submission_time + datetime.timedelta(days = 1)).strftime("%d:%m:%Y"):
                    submission_time_form = submission.submission_time.strftime("Yesterday, %H:%M")
                # Display actual date otherwise
                else:
                    submission_time_form = submission.submission_time.strftime("%B %d, %H:%M")
            else:
                submission_time_form = submission.submission_time.strftime("%H:%M")

            # Get the display name of the user who made the submission
            user = User.objects.get(username=submission.username)
            user_display_name = user.first_name
            if submission.photo_bytes is not None:
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
            Profile.recalculate_user_points_by_username(submission.username)
            # Not ideal but ensures points sync
            user_profile = Profile.objects.filter(id=request.user.id).first()
            has_reviewed = submission.reviewed
            # Fetches profile picture for submission user
            submission_user_item = OwnedItem.get_active_item_data(submission.username)
                
            submissions_info[submission.id] = {
                                               'submission_id': submission.id,
                                               'submission_user_displayname': user_display_name,
                                               'submission_user_profile_picture': {
                                                    'is_active': submission_user_item['is_active'],
                                                    'image': submission_user_item['image'],
                                                    'text': submission_user_item['text']
                                               },
                                               'submission_username': submission.username,
                                               'submission_time': submission_time_form,
                                               'submission_photo': photo_b64,
                                               'submission_comment_count': submission.get_comment_count(),
                                               'submission_has_liked': has_liked,
                                               'submission_has_reviewed': has_reviewed,
                                               'submission_upvote_count': submission.get_upvote_count()
                                            }

        context['submissions'] = submissions_info

        return HttpResponse(template.render(context, request))
    else:
        return signin(request)

def friends_feed(request):
    '''
    Displays the feed of friends' posts only
    '''
    context = {}
    if request.user.is_authenticated:
        template = loader.get_template('feed/feed.html')

        submissions_info = {}

        # List the user's friends' usernames
        user_friends = Friend.get_friend_usernames(request.user.username)

        user_profile = Profile.objects.filter(id=request.user.id).first()
        user_points = str(user_profile.points)
        context["user_points"] = user_points

        # Fetches user's profile picture
        item = OwnedItem.get_active_item_data(request.user.username)
        context["is_active"] = item["is_active"]
        context["profile_image"] = item["image"]
        context["text_colour"] = item["text"]

        # List the submissions from most recent
        active_challenge = ActiveChallenge.get_last_active_challenge()
        context["active_challenge"] = active_challenge.get_challenge_description()
        if Submission.user_has_submitted(request.user.username):
            user_submission = Submission.objects.filter(active_challenge=active_challenge,username=request.user.username)
            submissions = Submission.objects.filter(active_challenge=active_challenge,reported=False).order_by('-submission_time').exclude(username=request.user.username)
            submissions = user_submission | submissions
        else:
            submissions = Submission.objects.filter(active_challenge=active_challenge,reported=False).order_by('-submission_time')

        for submission in submissions:
            if submission.username in user_friends or submission.username == request.user.username:

                submission_date = submission.submission_time.strftime("%d:%m:%Y")
                submission_year = submission.submission_time.strftime("%Y")
                current_date = datetime.date.today().strftime("%d:%m:%Y")
                current_year = datetime.date.today().strftime("%Y")

                # Only display submission year if different from current year
                if submission_year != current_year:
                    submission_time_form = submission.submission_time.strftime("%B %d, %Y")
                # Only display submission date if different from current date
                elif submission_date != current_date:
                    # Display "Yesterday" if submission is from previous day
                    if current_date == (submission.submission_time + datetime.timedelta(days = 1)).strftime("%d:%m:%Y"):
                        submission_time_form = submission.submission_time.strftime("Yesterday, %H:%M")
                    # Display actual date otherwise
                    else:
                        submission_time_form = submission.submission_time.strftime("%B %d, %H:%M")
                else:
                    submission_time_form = submission.submission_time.strftime("%H:%M")

                # Get the display name of the user who made the submission
                user = User.objects.get(username=submission.username)
                user_display_name = user.first_name
                if submission.photo_bytes is not None:
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
                Profile.recalculate_user_points_by_username(submission.username)

                # Fetches profile picture for submission user
                submission_user_item = OwnedItem.get_active_item_data(submission.username)
                
                submissions_info[submission.id] = {
                                                'submission_id': submission.id,
                                                'submission_user_displayname': user_display_name,
                                                'submission_user_profile_picture': {
                                                    'is_active': submission_user_item["is_active"],
                                                    'image': submission_user_item["image"],
                                                    'text': submission_user_item["text"]
                                                },
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
  
#endregion

#region Account Management

def history(request):
    '''
    Displays the submission history page
    '''
    context = {}

    if request.user.is_authenticated:
        template = loader.get_template('account/history.html')

        # Get the user submissions from most recent
        submissions = Submission.objects.filter(username = request.user.username).order_by('-submission_time')

        # Display date joined
        user_join_date = request.user.date_joined
        current_date = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
        date_difference = current_date - user_join_date

        # Fetches user's profile picture
        item = OwnedItem.get_active_item_data(request.user.username)
        context["is_active"] = item["is_active"]
        context["profile_image"] = item["image"]
        context["text_colour"] = item["text"]

        if date_difference.days:
            display_date = str(date_difference.days) + " days"
        elif date_difference.seconds > 3600:
            display_date = str(date_difference.seconds // 3600) + " hours"
        elif date_difference.seconds > 60:
            display_date = str(date_difference.seconds // 60) + " minutes"
        else:
            display_date = "a few seconds"

        context["display_date"] = display_date

        # Display points
        user_profile = Profile.get_profile(request.user.username)
        user_points = str(user_profile.points)
        context["user_points"] = user_points
        context["is_subscribed"] = user_profile.subscribed_to_emails

        active_challenge = ActiveChallenge.get_last_active_challenge()
        context["active_challenge"] = active_challenge.get_challenge_description()

        try:
            start_month = int(submissions.first().submission_time.strftime("%m"))
            end_month = int(submissions.last().submission_time.strftime("%m"))
            total_months = end_month - start_month + 1
        except:
            total_months = 0

        # Initialise list of empty lists for each month
        submissions_by_month = [[]] * total_months

        for submission in submissions:

            # Get date
            submission_date = submission.submission_time.strftime("%d/%m/%Y")
            submission_month = int(submission.submission_time.strftime("%m"))

            submission_time_form = submission_date

            if submission.photo_bytes is not None:
                photo_b64 = "data:image/png;base64,"+base64.b64encode(submission.photo_bytes).decode("utf-8")
            else:
                photo_b64 = "data:image/png;base64,"

            # Nested list structure to pass to template
            submissions_by_month[submission_month - start_month].append({
                                                'id': submission.id,
                                                'username': submission.username,
                                                'time': submission_time_form,
                                                'photo': photo_b64,
                                                'upvote_count': submission.get_upvote_count(),
                                                'comment_count': submission.get_comment_count(),
                                                })
        context['months'] = submissions_by_month

        return HttpResponse(template.render(context, request))
    else:
        return signin(request)

def friends(request):
    '''
    Loads the friends management page
    '''
    context = {}

    if request.user.is_authenticated:
        template = loader.get_template('account/friends.html')

        # Fetches user's profile picture
        item = OwnedItem.get_active_item_data(request.user.username)
        context["is_active"] = item["is_active"]
        context["profile_image"] = item["image"]
        context["text_colour"] = item["text"]

        user_friends = Friend.get_friend_usernames(request.user.username)
        friend_items = []
        for friend_username in user_friends:
            friend_items.append(OwnedItem.get_active_item_data(friend_username))
        context['friends'] = zip(user_friends, friend_items)
            

        incoming = Friend.get_pending_friend_usernames(request.user.username)
        incoming_items = []
        for incoming_username in incoming:
            incoming_items.append(OwnedItem.get_active_item_data(incoming_username))
        context['incoming'] = zip(incoming, incoming_items)

        current_challenge =ActiveChallenge.get_last_active_challenge()
        context["active_challenge"] = current_challenge.get_challenge_description()

        user_profile = Profile.get_profile(request.user.username)
        user_points = str(user_profile.points)
        post_count= Friend.get_friend_post_count(user_profile.user.username,current_challenge)
        context["user_points"] = user_points
        context["post_count"] = post_count
        return HttpResponse(template.render(context, request))
    else:
        return signin(request)
    
def store(request):
    context = {}
    if request.user.is_authenticated:
        template = loader.get_template('account/store.html')

        CurrentChallenge = ActiveChallenge.get_last_active_challenge()
        context["active_challenge"] = CurrentChallenge.get_challenge_description()
        context["username"] = request.user.username
        Profile.calculate_spendable_points_by_username(request.user.username)
        profileObj = Profile.get_profile(request.user.username)
        user_points = str(profileObj.points)
        user_spendable_points = str(profileObj.spendable_points)
        context["user_points"] = user_points
        context["user_spendable_points"] = user_spendable_points

        # Fetches user's profile picture
        item = OwnedItem.get_active_item_data(request.user.username)
        context["is_active"] = item["is_active"]
        context["profile_image"] = item["image"]
        context["text_colour"] = item["text"]
        
        store_info = {}
        StoreItems = StoreItem.objects.all()
        for item in StoreItems:
            is_owned = OwnedItem.owns_item(item.item_name, request.user.username)
            if is_owned:
                is_active = OwnedItem.objects.get(item_name=item.item_name, username=request.user.username).is_active
            else:
                is_active = False

            profile_image = item.photo.url
            text_colour = '#'+item.text_colour

            store_info[item.id] = {
                'item_name': item.item_name,
                'item_cost':  item.cost,
                'is_owned': is_owned,
                'is_active': is_active,
                'image': profile_image,
                'text': text_colour
            }

        context['store'] = store_info

        return HttpResponse(template.render(context, request))
    else:
        print("Not signed in")
        template = loader.get_template('home/sign-in.html')
        return HttpResponse(template.render(context, request))

#endregion

#region Other

def post(request):
    '''
    Displays a speicifed post and its comments in further detail
    '''
    context = {}

    if request.method == "POST":
        if request.user.is_authenticated:
            active_challenge = ActiveChallenge.get_last_active_challenge()
            context["active_challenge"] = active_challenge.get_challenge_description()

            # Fetches user's profile picture
            item = OwnedItem.get_active_item_data(request.user.username)
            context["is_active"] = item["is_active"]
            context["profile_image"] = item["image"]
            context["text_colour"] = item["text"]

            submission_id = request.POST.get("submission_id", "")
            submission=Submission.objects.filter(id=submission_id).first()

            submission_date = submission.submission_time.strftime("%d:%m:%Y")
            submission_year = submission.submission_time.strftime("%Y")
            current_date = datetime.date.today().strftime("%d:%m:%Y")
            current_year = datetime.date.today().strftime("%Y")

            # Only display submission year if different from current year
            if submission_year != current_year:
                submission_time_form = submission.submission_time.strftime("%B %d, %Y")
            # Only display submission date if different from current date
            elif submission_date != current_date:
                # Display "Yesterday" if submission is from previous day
                if current_date == (submission.submission_time + datetime.timedelta(days = 1)).strftime("%d:%m:%Y"):
                    submission_time_form = submission.submission_time.strftime("Yesterday, %H:%M")
                # Display actual date otherwise
                else:
                    submission_time_form = submission.submission_time.strftime("%B %d, %H:%M")
            else:
                submission_time_form = submission.submission_time.strftime("%H:%M")

            # Get the display name of the user who made the submission
            user = User.objects.get(username=submission.username)
            user_display_name = user.first_name

            if submission.photo_bytes is not None:
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
            Profile.recalculate_user_points_by_username(submission.username)
            # Not ideal but ensures points sync
            has_reviewed = submission.reviewed

            user_profile = Profile.get_profile(request.user.username)
            user_points = str(user_profile.points)
            context["user_points"] = user_points

            # Fetches profile picture for submission user
            submission_user_item = OwnedItem.get_active_item_data(submission.username)

            context['submission'] = {
                                               'id': submission.id,
                                               'user_displayname': user_display_name,
                                               'user_profile_picture': {
                                                    'is_active': submission_user_item["is_active"],
                                                    'image': submission_user_item["image"],
                                                    'text': submission_user_item["text"]
                                                },
                                               'username': submission.username,
                                               'time': submission_time_form,
                                               'photo': photo_b64,
                                               'comment_count': submission.get_comment_count(),
                                               'comments' : submission.get_comments(),
                                               'has_liked': has_liked,
                                               'has_reviewed': has_reviewed,
                                               'upvote_count': submission.get_upvote_count(),
                                               'is_active': submission.is_for_active_challenge()
                                            }

            template = loader.get_template('misc/post.html')

            return HttpResponse(template.render(context, request))
        else:
            return signin(request)
    else:
        return redirect('/')

def leaderboard(request):
    '''
    Displays the leaderboard page
    '''
    context = {}

    if request.user.is_authenticated:
        template = loader.get_template('misc/leaderboard.html')

        user_profile = Profile.get_profile(request.user.username)

        # Fetches user's profile picture
        item = OwnedItem.get_active_item_data(request.user.username)
        context["is_active"] = item["is_active"]
        context["profile_image"] = item["image"]
        context["text_colour"] = item["text"]

        # Get overall leaders & user positon
        profiles = Profile.objects.order_by('-points')
        context["is_leader"] = False
        friend_usernames = Friend.get_friend_usernames(request.user.username)
        user_friends = []
        for index, profile in enumerate(profiles):
            if profile.user.username == request.user.username:
                if index < 20:
                    context["is_leader"] = True
                else:
                    context ["overall_position"] = index
            else:
                if profile.user.username in friend_usernames:
                    user_friends.append(profile)
        leaders = profiles[:20]
        leader_items = []
        for profile in leaders:
            leader_items.append(OwnedItem.get_active_item_data(profile.user.username))
        context["leaders"] = zip(leaders, leader_items)

        # Get friend leaders & user position
        user_friends.append(user_profile)
        friend_items = []
        for profile in user_friends:
            friend_items.append(OwnedItem.get_active_item_data(profile.user.username))
        friends_list = list(zip(user_friends, friend_items))
        friends_list.sort(key=lambda x: x[0].points, reverse=True)
        context["friends"] = friends_list[:20]

        for index, profile in enumerate(user_friends):
            if profile.user.username == request.user.username:
                if index < 20:
                    context["is_friend_leader"] = True
                else:
                    context["friends_position"] = index

        current_challenge = ActiveChallenge.get_last_active_challenge()
        context["active_challenge"] = current_challenge.get_challenge_description()

        user_points = str(user_profile.points)
        context["user_points"] = user_points

        return HttpResponse(template.render(context, request))
    else:
        return signin(request)

#endregion

#endregion

#region Functions

#region Posts

@csrf_exempt
def upload_photo(request):
    '''
    Uploads the specified photo to the database
    '''
    if request.method == "POST":
        if request.user.is_authenticated:
            try:
                upload=request.FILES["upload_pic"]
                lat = request.POST["latitude"]
                lon = request.POST["longitude"]
            except MultiValueDictKeyError:
                # Missing data
                return redirect('/submit/')

            picture_bytes = b""
            for data in upload:
                picture_bytes += data
            has_submitted = Submission.user_has_submitted(request.user.username)
            active_challenge = ActiveChallenge.objects.last()
            if has_submitted is True:
                replace_submission=Submission.objects.get(username=request.user.username, active_challenge=active_challenge)
                replace_submission.delete()
             ## ->
            current_date = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc)
            new_submission = Submission(username=request.user.username,
            active_challenge=active_challenge,
            reported=False,
            reviewed=False,
            photo_bytes=picture_bytes,
            submission_time=current_date)
            # Check location
            if active_challenge.challenge.allowed_distance == 0.0:
                new_submission.save()
                return redirect('/university-feed/')
            else:
                try:
                    if new_submission.location_is_valid():
                        new_submission.save()
                        return redirect('/university-feed/')
                except:
                    if new_submission.location_check_missing_metadata(latitude=lat, longitude=lon):
                        new_submission.save()
                        return redirect('/university-feed/')
                return redirect('/submit/')
    return redirect('submit/')

@csrf_exempt
def flag_submission(request):
    '''
    Flags the specified submission for manual review
    '''
    if request.method == "POST":
        if request.user.is_authenticated:
            data=json.loads(request.body)
            submission_id = data["submission_id"]
            submission = Submission.objects.filter(id=submission_id).first()
            submission.report_submission(request.user.username)
            return HttpResponse({"success":"true"})
    return redirect('/')

@csrf_exempt
def like_submission(request):
    '''
    Adds a like to the specified submission
    '''
    if request.method == "POST":
        if request.user.is_authenticated:
            data=json.loads(request.body)
            submission_id = data["submission_id"]
            checker = Upvote.objects.filter(voter_username=request.user.username,
                submission_id=submission_id)
            if len(checker) < 1:
                submission = Submission.objects.filter(id=submission_id).first()
                submission.create_upvote(request.user.username)
            else:
                checker.first().remove_upvote()
            return HttpResponse({"success":"true"})
    return redirect('/')

@csrf_exempt
def delete_post(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            submission_id = request.POST.get("submission_id")
            submission = Submission.objects.filter(id=submission_id).first()
            submission.remove_submission(True)
            if submission.active_challenge.get_challenge_description() == ActiveChallenge.get_last_active_challenge().get_challenge_description():
                return redirect('/submit/')
            else:
                return redirect('/history/')
    return redirect('/')

#endregion

#region Comments:

@csrf_exempt
def create_comment(request):
    '''
    Creates a new comment on the specified post
    '''
    if request.method == "POST":
        if request.user.is_authenticated:
            try:
                data=json.loads(request.body)

                submission_id = data["submission_id"]
                submission = Submission.objects.filter(id = submission_id).first()

                author = data["author"]
                content = data["content"]

                submission.create_comment(author, content)

                return HttpResponse({"success":"true"})
            except Exception as e:
                print(str(e))
                return HttpResponse({"success":"false"})
    return redirect('/')

@csrf_exempt
def flag_comment(request):
    '''
    Flags the specified comment for manual review
    '''
    if request.method == "POST":
        if request.user.is_authenticated:
            data=json.loads(request.body)

            comment_id = data["comment_id"]
            comment = Comment.objects.filter(id=comment_id).first()
            comment.report_comment(request.user.username)

            return HttpResponse({"success":"true"})
    return redirect('/')

#endregion

#region Friends

def add_friend(request):
    '''
    Creates a pending friend request
    '''
    if request.method == "POST":
        if request.user.is_authenticated:
            try:
                recipient = request.POST.get("friend_name")
                Friend.create_friend_request(request.user.username, recipient)
            finally:
                return redirect('/friends/')
    return redirect('/')

def remove_friend(request):
    '''
    Removes an existing friend
    '''
    if request.method == "POST":
        if request.user.is_authenticated:
            try:
                friend_username = request.POST.get("friend_name")
                Friend.remove_friend(request.user.username, friend_username)
            except Exception as e:
                print(str(e))
            finally:
                return redirect('/friends/')
    return redirect('/')

def accept_friend_request(request):
    '''
    Accepts a pending friend request
    '''
    if request.method == "POST":
        if request.user.is_authenticated:
            try:
                friend_username = request.POST.get("friend_name")
                Friend.accept_friend_request(friend_username, request.user.username)
            except Exception as e:
                print(str(e))
            finally:
                return redirect('/friends/')
    return redirect('/')

def decline_friend_request(request):
    '''
    Removes a pending friend request
    '''
    if request.method == "POST":
        if request.user.is_authenticated:
            try:
                friend_username = request.POST.get("friend_name")
                Friend.decline_friend_request(friend_username, request.user.username)
            except Exception as e:
                print(str(e))
            finally:
                return redirect('/friends/')
    return redirect('/')

#endregion

#region Store

@csrf_exempt
def buy_item(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            data=json.loads(request.body)
            username = data['username']
            item_name = data['item_name']
            spendable_points = data['spendable_points']
            item = StoreItem.objects.get(item_name=item_name)
            if int(spendable_points) >= item.cost:
                item_instance = OwnedItem(item_name=item_name, username=username, is_active=False)
                item_instance.save()
                p = Profile.get_profile(username)
                p.spendable_points -= item.cost
                p.save()
        return HttpResponse({"success":"true"})

@csrf_exempt
def activate_item(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            data=json.loads(request.body)
            username = data['username']
            item_name = data['item_name']
            OwnedItem.make_active(item_name, username)
        return HttpResponse({"success":"true"})

@csrf_exempt
def deactivate_item(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            data=json.loads(request.body)
            username = data['username']
            item_name = data['item_name']
            OwnedItem.make_inactive(item_name, username)
        return HttpResponse({"success":"true"})

#endregion

#region Accounts

def signout(request):
    '''
    Signs the user out
    '''
    if request.user.is_authenticated:
        logout(request)
    return redirect('/')

def delete_account(request):
    '''
    Deletes the specified account
    '''
    if request.method == "POST":
        if request.user.is_authenticated:
            try:
                user_account = Profile.objects.filter(user__username=request.user.username).first()
                user_account.user_data(fetch=False, delete=True)
                logout(request)
                return redirect('/')
            except Exception as e:
                print(str(e))
                return redirect('/account/')
    return redirect('/')

#endregion

#region Emails

def unsubscribe_from_emails(request):
    '''
    Unsubscribes a user from email notifiactions
    '''
    if request.user.is_authenticated:
        try:
            profile = Profile.get_profile(request.user.username)
            profile.subscribed_to_emails = False
            profile.save()
        except Exception as e:
            print(str(e))
        finally:
            return redirect('/account/')
    return redirect('/')

def resubscribe_to_emails(request):
    '''
    Resubscribes a user to email notifiactions
    '''
    if request.user.is_authenticated:
        try:
            profile = Profile.get_profile(request.user.username)
            profile.subscribed_to_emails = True
            profile.save()
        except Exception as e:
            print(str(e))
        finally:
            return redirect('/account/')
    return redirect('/')

#endregion

# If pages need to be restricted to certain groups of users.
@microsoft_login_required(groups=("SpecificGroup1", "SpecificGroup2"))  # Add here the list of Group names
def specific_group_access(request):
    return HttpResponse("You are accessing page which is accessible only to users belonging to SpecificGroup1 or SpecificGroup2")

#endregion
