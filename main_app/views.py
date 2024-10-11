from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
import requests
from django.shortcuts import render, redirect
from .models import Coin
from django.http import HttpResponse, Http404
import os
from django.utils import timezone

API_KEY = os.environ["API_KEY"]

API_URL = f"https://api.coingecko.com/api/v3/coins/markets?order=market_cap_desc&per_page=20&vs_currency=usd&x_cg_api_key={API_KEY}"

API_FETCH_FREQ = 1  # minutes


class Home(LoginView):
    template_name = "home.html"


def about(request):
    return render(request, "about.html")


def fetch_coin_info():
    # Fetch data from CoinGecko API
    response = requests.get(API_URL)

    if response.status_code == 200:
        data = response.json()
        # Return the list of 15 coins
        coins = []
        curr_time = timezone.now()
        for coin_data in data:
            api_coin_data = {
                "name": coin_data["name"],
                "symbol": coin_data["symbol"].upper(),
                "price": coin_data["current_price"],
                "market_cap": coin_data["market_cap"],
                "volume": coin_data["total_volume"],
                "change": coin_data["price_change_percentage_24h"],
                "image": coin_data["image"],
                "updated_at": curr_time
            }

            # Append each coin's data to the coins list
            coins.append(api_coin_data)
        return coins

    else:
        return None


def coin_index(request):
    # Check if there are coins in database
    coins = Coin.objects.all().order_by("-market_cap")
    if len(coins) and coins[0].updated_at < timezone.now() - timezone.timedelta(minutes=API_FETCH_FREQ):
        print("Updating coins")
        coin_data = fetch_coin_info()
        curr_time = timezone.now()
        for coin in coins:
            for data in coin_data:
                if coin.symbol == data["symbol"]:
                    coin.price = data["price"]
                    coin.market_cap = data["market_cap"]
                    coin.volume = data["volume"]
                    coin.change = data["change"]
                    coin.updated_at = curr_time
        Coin.objects.bulk_update(coins, ["price", "market_cap", "volume", "change", "updated_at"])
    
    elif not len(coins):
        coin_data = fetch_coin_info()
        # Save the data to the database
        coin_objects = [Coin(**data) for data in coin_data]
        coins = Coin.objects.bulk_create(coin_objects)
        # Get all coins from the database
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
