from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View

class FusionView(LoginRequiredMixin, View):
    template_name = 'fusion/fusion_home.html'  # Assuming your template is in templates/fusion/fusion_home.html
    login_url = '/login/'  # Redirect URL if user is not authenticated

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        # Your POST request handling code here
        return render(request, self.template_name)

