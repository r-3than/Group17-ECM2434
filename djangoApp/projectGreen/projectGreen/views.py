from django.http import HttpResponse
from microsoft_authentication.auth.auth_decorators import microsoft_login_required
from django.template import loader
from django.views.generic.list import ListView

# Not sure why this import doesn't work
from .models import Notification





def home(request):
    template = loader.get_template('home/home.html')
    context = {}
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
    context["unread_notifications"] = unread_notifications
    return HttpResponse(template.render(context, request))
    

# If pages need to be restricted to certain groups of users.
@microsoft_login_required(groups=("SpecificGroup1", "SpecificGroup2"))  # Add here the list of Group names
def specific_group_access(request):
    return HttpResponse("You are accessing page which is accessible only to users belonging to SpecificGroup1 or SpecificGroup2")

# Need to create a view to show notifications

# Page to list all notifications for a user
class NotificationListView(ListView):
    model = Notification

    def get_queryset(self):
        return Notifications.objects.filter(user=self.request.user).order_by("-timestamp")


#
