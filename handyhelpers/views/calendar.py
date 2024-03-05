import calendar
from datetime import date
import re

from django.shortcuts import render
from django.views.generic import View



class CalendarView(View):
    """ View to render a monthly calendar and optionally display events.

    class parameters:
        template_name           - template used when rendering partial; defaults to: handyhelpers/partials/calendar.htm
        event_model             - django model representing events
        event_model_date_field  - date or datetime field containing event date
        event_detail_url        - url to use to get event details and display in a modal
        use_htmx                - boolean representing option to use htmx in in today/next month/previous month links 
    
    Usage Example:
        class MyEventCalendarView(CalendarView):
            event_model = Event
            event_model_date_field = "date"
            event_detail_url = "myapp_:get_event_details"   
    """
    title = "Calendar"
    event_model = None
    event_model_date_field = None
    event_detail_url = None
    template_name = "handyhelpers/partials/calendar.htm"
    use_htmx = True

    def get_next(self, this_year:int, this_month:int) -> tuple:
        """get the year and month of the next month

        Args:
            this_year (int): year of the currently rendered calendar
            this_month (int): month of the currently rendered calendar

        Returns:
            tuple: tuple of integers containing year and month of the next calendar month
        """
        if this_month == 12:
            return (this_year + 1), 1
        return this_year, this_month + 1

    def get_previous(self, this_year:int, this_month:int) -> tuple:
        """get the year and month of the previous month

        Args:
            this_year (int): year of the currently rendered calendar
            this_month (int): month of the currently rendered calendar

        Returns:
            tuple: tuple of integers containing year and month of the next calendar month
        """
        if this_month == 1:
            return this_year - 1, 12
        return this_year, this_month - 1

    def get(self, request, *args, **kwargs):
        mo = re.search(r"^(/[^/]+/)", request.path)
        if mo:
            calendar_url_root = mo.groups()[0]
        
        today = date.today()
        year = kwargs.get("year", today.year)
        month = kwargs.get("month", today.month)
        if year == 0:
            year = today.year
        if month == 0:
            month = today.month
        next_year, next_month = self.get_next(year, month)
        prev_year, prev_month = self.get_previous(year, month)

        today_url = f"{calendar_url_root}{today.year}/{today.month}"
        prev_month_url = f"{calendar_url_root}{prev_year}/{prev_month}"
        next_month_url = f"{calendar_url_root}{next_year}/{next_month}"
        
        cal_data = calendar.monthcalendar(year, month)

        queryset = None
        if self.event_model:
            queryset = self.event_model.objects.filter(
                **{f"{self.event_model_date_field}__year": year,
                   f"{self.event_model_date_field}__month": month,
                   }
                )

        context = {
            "cal_data": cal_data,
            "title": self.title,
            "year": year,
            "month": month,
            "month_name": calendar.month_name[month],
            "today": today,
            "event_list": queryset,
            "use_htmx": self.use_htmx,
            "event_detail_url": self.event_detail_url,
            "today_url": today_url,
            "prev_month_url": prev_month_url,
            "next_month_url": next_month_url,
        }
        return render(request, self.template_name, context)
