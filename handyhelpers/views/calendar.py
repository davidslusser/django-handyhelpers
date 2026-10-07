"""Monthly calendars using the configured event field and reversible URLs."""

import calendar
from datetime import datetime

from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.views import View

from handyhelpers.mixins.view_mixins import HtmxViewMixin


class CalendarView(View):
    title = "Calendar"
    event_model = event_model_date_field = event_detail_url = None
    template_name = "handyhelpers/partials/calendar.htm"
    use_htmx = True
    calendar_url_name = None

    def get_next(self, year, month):
        return (year + 1, 1) if month == 12 else (year, month + 1)

    def get_previous(self, year, month):
        return (year - 1, 12) if month == 1 else (year, month - 1)

    def calendar_url(self, year, month):
        match = self.request.resolver_match
        name = self.calendar_url_name or (match.view_name if match else None)
        kwargs = {**(match.kwargs if match else {}), "year": year, "month": month}
        if name:
            try:
                return reverse(name, kwargs=kwargs)
            except NoReverseMatch:
                pass
        from handyhelpers.utils import update_query

        return update_query(self.request.path, {"year": year, "month": month})

    def get(self, request, *args, **kwargs):
        today = timezone.localdate() if timezone.is_aware(timezone.now()) else timezone.now().date()
        try:
            year = int(kwargs.get("year", request.GET.get("year", today.year))) or today.year
            month = int(kwargs.get("month", request.GET.get("month", today.month))) or today.month
            if year < 1 or year > 9998 or month < 1 or month > 12:
                raise ValueError
        except (TypeError, ValueError):
            return HttpResponseBadRequest("Invalid calendar date")
        events = []
        if self.event_model:
            for obj in self.event_model._default_manager.filter(
                **{
                    self.event_model_date_field + "__year": year,
                    self.event_model_date_field + "__month": month,
                }
            ):
                date = getattr(obj, self.event_model_date_field)
                if isinstance(date, datetime) and timezone.is_aware(date):
                    date = timezone.localtime(date)
                events.append(
                    {
                        "object": obj,
                        "day": date.day,
                        "month": date.month,
                        "year": date.year,
                        "pk": obj.pk,
                    }
                )
        context = dict(
            title=self.title,
            year=year,
            month=month,
            month_name=calendar.month_name[month],
            today=today,
            cal_data=calendar.monthcalendar(year, month),
            event_list=events,
            use_htmx=self.use_htmx,
            event_detail_url=self.event_detail_url,
            today_url=self.calendar_url(today.year, today.month),
            prev_month_url=self.calendar_url(*self.get_previous(year, month)),
            next_month_url=self.calendar_url(*self.get_next(year, month)),
        )
        return render(request, self.template_name, context)


class HtmxCalendarView(HtmxViewMixin, CalendarView):
    htmx_template_name = None

    def get(self, request, *args, **kwargs):
        if self.is_htmx() and self.htmx_template_name:
            self.template_name = self.htmx_template_name
        return super().get(request, *args, **kwargs)
