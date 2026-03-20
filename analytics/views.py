from django.shortcuts import render
from django.http import JsonResponse
from .services.calculator import AnalyticsService
from .models import Commodity

def dashboard_view(request):
    # Pasamos la lista de commodities para el menú
    commodities = Commodity.objects.all()
    return render(request, 'analytics/dashboard.html', {'commodities': commodities})

def commodity_chart_api(request, symbol):
    # Esta es la API que alimentará a Plotly
    data = AnalyticsService.get_technical_indicators(symbol)
    return JsonResponse({'data': data}, safe=False)