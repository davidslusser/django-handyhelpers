"""Portable, timezone-aware counts over 24 hours, 52 ISO weeks, or 12 months."""

from datetime import timedelta
from datetime import timezone as datetime_timezone

from dateutil.relativedelta import relativedelta
from django.db.models import Count
from django.db.models.functions import TruncHour, TruncMonth, TruncWeek
from django.utils import timezone


def _counts(queryset, field_name, buckets, expression):
    newest = buckets[0]
    if expression is TruncHour:
        end = newest + timedelta(hours=1)
    elif expression is TruncWeek:
        end = newest + timedelta(weeks=1)
    else:
        end = newest + relativedelta(months=1)
    truncation = (
        expression(field_name, tzinfo=datetime_timezone.utc)
        if expression is TruncHour
        else expression(field_name)
    )
    rows = (
        queryset.filter(**{field_name + "__gte": buckets[-1], field_name + "__lt": end})
        .annotate(bucket=truncation)
        .order_by()
        .values("bucket")
        .annotate(count=Count("pk"))
    )
    # Full datetime buckets include ISO year/week, avoiding collisions across years.
    counts = {row["bucket"]: row["count"] for row in rows}
    return [counts.get(bucket, 0) for bucket in buckets]


def _now():
    now = timezone.now()
    return timezone.localtime(now) if timezone.is_aware(now) else now


def count_by_hour(queryset, field_name):
    now = _now()
    if timezone.is_aware(now):
        now = now.astimezone(datetime_timezone.utc)
    start = now.replace(minute=0, second=0, microsecond=0)
    return _counts(queryset, field_name, [start - timedelta(hours=i) for i in range(24)], TruncHour)


def count_by_week(queryset, field_name):
    now = _now()
    start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    return _counts(queryset, field_name, [start - timedelta(weeks=i) for i in range(52)], TruncWeek)


def count_by_month(queryset, field_name):
    start = _now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return _counts(
        queryset, field_name, [start - relativedelta(months=i) for i in range(12)], TruncMonth
    )
