"""Build plain chart configurations suitable for Django's json_script filter."""

from urllib.parse import quote

from django import template

from handyhelpers.utils import update_query
from handyhelpers.views.report import get_colors

register = template.Library()


@register.simple_tag
def chart_config(chart, chart_type="bar"):
    if "data" in chart and isinstance(chart["data"], dict):
        return chart
    labels = chart.get("label_list", [])
    colors = chart.get("color_list") or get_colors(len(labels))
    links = {item["case"]: item["link"] for item in chart.get("list_view_link_list", [])}
    base_url = chart.get("list_view", "/")
    urls = [
        update_query(
            links.get(label, base_url + quote(str(label), safe="")),
            {"page_description": str(label)},
        )
        for label in labels
    ]
    return {
        "type": chart.get("type", chart_type),
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "label": chart.get("title", "Item count"),
                    "data": chart.get("value_list", chart.get("data_list", [])),
                    "backgroundColor": colors,
                    "urls": urls,
                }
            ],
        },
        "options": {
            "responsive": True,
            "plugins": {
                "legend": {"display": bool(chart.get("legend", False))},
                "title": {"display": bool(chart.get("title")), "text": chart.get("title", "")},
            },
        },
    }
