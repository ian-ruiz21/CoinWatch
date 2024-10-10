from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
import requests
from django.shortcuts import render, redirect
from .models import Coin
from django.http import HttpResponse, Http404


class Home(LoginView):
    template_name = "home.html"


def about(request):
    return render(request, "about.html")


def fetch_coin_info():
    # Fetch data from CoinGecko API
    response = requests.get(
        "https://api.coingecko.com/api/v3/coins/markets",
        params={
            "vs_currency": "usd",  # You can adjust this to the currency you want to track
            "order": "market_cap_desc",
            "per_page": 15,  # Limit to 15 coins
            "page": 1,
            "sparkline": False,
        },
    )

    if response.status_code == 200:
        data = response.json()
        # Return the list of 15 coins
        coins = []
        for coin_data in data:
            coin_id = coin_data["id"]
            name = coin_data["name"]
            symbol = coin_data["symbol"].upper()
            price = coin_data["current_price"]
            market_cap = coin_data["market_cap"]
            volume = coin_data["total_volume"]
            change = coin_data["price_change_percentage_24h"]
            image_url = coin_data["image"]

        # Append each coin's data to the coins list
        coins.append(
            {
                "id": coin_id,
                "name": name,
                "symbol": symbol,
                "price": price,
                "market_cap": market_cap,
                "volume": volume,
                "change": change,
                "image_url": image_url,
            }
        )
        return coins

    else:
        return None


def coin_index(request):
    coins = fetch_coin_info()  # Get coin data
    return render(request, "coins/index.html", {"coins": coins})


def coin_detail(request, coin_id):
    # Adjust the API endpoint to fetch data for a specific coin
    url = "https://api.coingecko.com/api/v3/coins/{coin_id}]"
    response = requests.get(url)
    if response.status_code == 200:
        coin = response.json()  # Fetch the single coin’s details
        return render(request, "coins/detail.html", {"coin_id": coin_id, "coin": coin})


    else:
    # Handle the case where the API does not return data (404, 500, etc.)
        raise Http404("Coin not found")


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
