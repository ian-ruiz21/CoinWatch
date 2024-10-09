from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
import requests
from django.shortcuts import render, redirect

# from django.http import HttpResponse


class Home(LoginView):
    template_name = "home.html"


def about(request):
    return render(request, "about.html")


def coin_index(request):
    def fetch_coin_info():
        response = requests.get("https://api.coingecko.com/api/v3/coins/categories")
        if response.status_code == 200:
            data = response.json()
            name = data["name"].capitalize()
            poke_id = data["id"]
            xp = data["base_experience"]
            poke_type = data["types"][0]["type"]["name"]
            abilities = ", ".join(
                [ability["ability"]["name"] for ability in data["abilities"]]
            )
            image_url = data["sprites"]["other"]["official-artwork"]["front_default"]
            return {
                "name": name,
                "poke_id": poke_id,
                "xp": xp,
                "type": poke_type,
                "abilities": abilities,
                "image_url": image_url,
            }

        else:
            return None

    return render(request, "coins/coin_index.html", {'coin': fetch_coin_info})


def signup(request):
    error_message = ""
    if request.method == "POST":
        # This is how to create a 'user' form object
        # that includes the data from the browser
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # This will add the user to the database
            user = form.save()
            # This is how we log a user in
            login(request, user)
            return redirect("home")
        else:
            error_message = "Invalid sign up - try again"
    # A bad POST or a GET request, so render signup.html with an empty form
    form = UserCreationForm()
    context = {"form": form, "error_message": error_message}
    return render(request, "signup.html", context)
    # Same as:
    # return render(
    #     request,
    #     'signup.html',
    #     {'form': form, 'error_message': error_message}
    # )


# def login(request):
#     return render(request, 'registration/login.html')
