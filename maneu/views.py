from django.shortcuts import render


def index(request):
    index_id = request.GET.get('index_id')
    return render(request, 'index.html', {'index_id': index_id})


def verify_order(request):
    index_id = request.GET.get('index_id')
    return render(request, 'order.html', {'index_id': index_id})


def verify_store(request):
    index_id = request.GET.get('index_id')
    return render(request, 'store.html', {'index_id': index_id})


def verify_report(request):
    index_id = request.GET.get('index_id')
    return render(request, 'report.html', {'index_id': index_id})
