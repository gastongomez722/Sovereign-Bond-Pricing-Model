def get_distance_days_360(first_date, second_date):
    '''this function was created to get the distance between any two days in days 360'''
    distance_years = (second_date.year - first_date.year)
    distance_months = (second_date.month - first_date.month)
    distance_days = (second_date.day - first_date.day)
    return distance_years * 360 + distance_months * 30 + distance_days

def get_distance_days_252(first_date, second_date):
    '''this function was created to get the distance between any two days in days 252. it uses the argentinian holidays dictionary for precision
    args: first date in 'year-month-day
    second date in 'year-mmonth-day
    return the distance between the provided days as an integer, uses the argentinian business days library defined in the code'''
    distance_days_252 = pd.bdate_range(first_date, second_date, freq=ARG_BD).size - 1 #minus 1 since distance in days is inclusive
    return distance_days_252