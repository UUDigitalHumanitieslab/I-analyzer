from datetime import datetime
import api.query as query

def test_date_manipulation(basic_query):
    assert query.get_filters(basic_query) == []

    # add date filter
    min_date = datetime(year = 1850, month = 1, day = 1)
    max_date = datetime(year = 1859, month = 12, day = 31)
    date_filter = query.make_date_filter(min_date, max_date)

    filtered_query = query.add_filter(basic_query, date_filter)
    assert query.get_filters(filtered_query) == [date_filter]
    query_min_date, query_max_date = query.get_date_range(filtered_query)
    assert query_min_date == min_date
    assert query_max_date == max_date

    # check old query is intact
    assert query.get_filters(basic_query) == []

    # add a more narrow date filter
    narrow_min_date = datetime(year = 1852, month = 1, day = 1)
    narrow_max_date = datetime(year = 1856, month = 12, day = 31)
    date_filter = query.make_date_filter(narrow_min_date, narrow_max_date)
    narrow_query = query.add_filter(filtered_query, date_filter)
    query_min_date, query_max_date = query.get_date_range(narrow_query)
    assert query_min_date == narrow_min_date
    assert query_max_date == narrow_max_date

    # add a wider date filter
    wide_min_date = datetime(year = 1840, month = 1, day = 1)
    wide_max_date = datetime(year = 1880, month = 12, day = 31)
    date_filter = query.make_date_filter(wide_min_date, wide_max_date)
    wide_query = query.add_filter(filtered_query, date_filter)
    query_min_date, query_max_date = query.get_date_range(wide_query)
    assert query_min_date == min_date
    assert query_max_date == max_date
