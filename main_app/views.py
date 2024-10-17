from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from .models import Coin, WatchList
import requests
import os


API_KEY = os.environ["API_KEY"]

API_URL = f"https://api.coingecko.com/api/v3/coins/markets?order=market_cap_desc&per_page=100&vs_currency=usd&x_cg_api_key={API_KEY}"

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
                "api_key": coin_data["id"],
                "updated_at": curr_time
            }

            coins.append(api_coin_data)
        return coins

    else:
        return None

@login_required
def coin_index(request):
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
        coin_objects = [Coin(**data) for data in coin_data]
        coins = Coin.objects.bulk_create(coin_objects)
    return render(request, "coins/index.html", {"coins": coins})

@login_required
def coin_detail(request, symbol):
    try:
        coin = Coin.objects.get(symbol=symbol)
    except Coin.DoesNotExist:
        return HttpResponseNotFound("Coin not found")
    
    return render(request,"coins/detail.html", {"coin": coin})

@login_required
def historical_data(request, symbol):
    coin = get_object_or_404(Coin, symbol=symbol)

    api_url = f"https://api.coingecko.com/api/v3/coins/{coin.api_key}/market_chart"

    params = {
        'vs_currency': 'usd',
        'days': '30',
        'interval': 'daily',
    }

    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        data = response.json()
        prices = data.get('prices', [])
        dates = [item[0] for item in prices]
        values = [item[1] for item in prices]

        context = {
            'coin': coin,
            'dates': dates,
            'values': values,
        }
    else:
        context = {
            'coin': coin,
            'error': 'Failed to retrieve historical data'
        }

    return render(request, 'coins/historical_data.html', context)

@login_required
def watchlist_view(request):
    watchlist = WatchList.objects.filter(user=request.user).first()
    if not watchlist:
        watchlist = WatchList.objects.create(user=request.user)
    return render(request, 'coins/watchlist.html', {'watchlist': watchlist})

@login_required
def add_to_watchlist(request, symbol):
    coin = Coin.objects.get(symbol=symbol)
    watchlist = WatchList.objects.filter(user=request.user).first()

    if not watchlist:
        watchlist = WatchList.objects.create(user=request.user)

    watchlist.coin.add(coin) 
    print(coin)
    return redirect('/watchlist')

@login_required
def remove_from_watchlist(request, symbol):
    coin = get_object_or_404(Coin, symbol=symbol)
    watchlist = WatchList.objects.filter(user=request.user).first()

    if watchlist:
        watchlist.coin.remove(coin)

    return redirect('/watchlist')

@login_required
def live_search(request):
    query = request.GET.get('q', '')
    if query:
        results = Coin.objects.filter(
            Q(name__icontains=query) | Q(symbol__icontains=query)
        )
    else:
        results = Coin.objects.none()

    data = list(results.values('name', 'symbol', 'price'))

    return JsonResponse({'results': data})


def signup(request):
    error_message = ""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
        else:
            error_message = "Invalid sign up - try again"
    form = UserCreationForm()
    context = {"form": form, "error_message": error_message}
    return render(request, "signup.html", context)
 