from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileForm, UserForm


@login_required
def profile_view(request):
    user = request.user
    profile = user.profile

    if request.method == "POST":
        u_form = UserForm(request.POST, instance=user)
        p_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("accounts:profile")
    else:
        u_form = UserForm(instance=user)
        p_form = ProfileForm(instance=profile)

    return render(
        request,
        "accounts/profile.html",
        {
            "u_form": u_form,
            "p_form": p_form,
        },
    )
