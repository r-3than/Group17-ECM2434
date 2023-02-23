from django.http import HttpResponse
from microsoft_authentication.auth.auth_decorators import microsoft_login_required
from django.template import loader





def home(request):
    template = loader.get_template('home/home.html')
    context = {}
    return HttpResponse(template.render(context, request))

# If pages need to be restricted to certain groups of users.
@microsoft_login_required(groups=("SpecificGroup1", "SpecificGroup2"))  # Add here the list of Group names
def specific_group_access(request):
    return HttpResponse("You are accessing page which is accessible only to users belonging to SpecificGroup1 or SpecificGroup2")
