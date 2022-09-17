import datetime as dt

def year(request):
    """
    Добавляет переменную с текущим годом.
    """
    year = dt.date.today()
    year = year.strftime('%Y')
    return {
        'year':year
    }
