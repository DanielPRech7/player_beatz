from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView
from beats.profiles.forms import SignUpForm, SignInForm, ProfileEditForm
from beats.profiles.models import Profile


class SignUpView(CreateView):
    template_name = "profile/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("profiles:detail")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Conta criada com sucesso!")

        return response


class SignInView(View):
    template_name = "profile/signin.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("profiles:detail")
        return render(request, self.template_name, {"form": SignInForm()})

    def post(self, request):
        form = SignInForm(request.POST)

        if not form.is_valid():
            messages.error(request, "Preencha os campos corretamente.")
            return render(request, self.template_name, {"form": form})

        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        remember = form.cleaned_data.get("remember")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if not remember:
                request.session.set_expiry(0)  # expira ao fechar o navegador
                
            messages.success(request, "Login realizado com sucesso!")
            return redirect("profiles:detail")

        messages.error(request, "Usuário ou senha inválidos.")
        return render(request, self.template_name, {"form": form})



# class ProfileDetailView(LoginRequiredMixin, DetailView):
#     template_name = "profile/profile_detail.html"
#     context_object_name = "profile"

#     def get_object(self, queryset=None):
#         user = self.request.user

#         return user.profile

class ProfileDetailView(LoginRequiredMixin, DetailView):
    template_name = "profile/profile_detail.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        user = self.request.user
        # Cria o perfil se não existir
        profile, created = Profile.objects.get_or_create(user=user)
        return profile

# class ProfileEditView(LoginRequiredMixin, UpdateView):
#     template_name = "profile/profile_edit.html"
#     form_class = ProfileEditForm
#     success_url = reverse_lazy("profiles:detail")

#     def get_object(self, queryset=None):
#         profile, created = Profile.objects.get_or_create(user=self.request.user)
#         return profile

#     def form_valid(self, form):
#         messages.success(self.request, "Perfil atualizado com sucesso!")
#         return super().form_valid(form)

class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = "profile/profile_edit.html"
    form_class = ProfileEditForm
    success_url = reverse_lazy("profiles:detail")

    def get_object(self, queryset=None):
        # Edita SEMPRE o perfil do usuário logado
        return self.request.user.profile

    def form_valid(self, form):
        messages.success(self.request, "Perfil atualizado com sucesso!")
        return super().form_valid(form)
    

def signout_view(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect("profiles:signin")