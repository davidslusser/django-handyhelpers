"""Render verified, pinned CDN assets; never fetch anything at render time."""

import json
from functools import lru_cache
from importlib.resources import files

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


@lru_cache(maxsize=1)
def asset_manifest():
    return json.loads(files("handyhelpers").joinpath("assets.json").read_text())


@register.simple_tag
def cdn_asset(name):
    asset = asset_manifest()[name]
    if asset["kind"] == "css" and name not in {"table_css", "bootstrap_icons"}:
        return format_html(
            '<link rel="stylesheet" href="{}" integrity="{}" crossorigin="anonymous">',
            asset["url"],
            asset["integrity"],
        )
    if name in {"jquery", "bootstrap_js", "htmx"}:
        return format_html(
            '<script src="{}" integrity="{}" crossorigin="anonymous"></script>',
            asset["url"],
            asset["integrity"],
        )
    # Optional libraries are loaded once even when components arrive via HTMX.
    spec = json.dumps({"name": name, **asset}).replace("<", "\\u003c")
    javascript = """(() => {
        const asset = SPEC;
        const pending = window.handyhelpersAssets ||= {};
        if (pending[asset.name]) return;
        const dependency = asset.name === 'table_locale' ? pending.table_js :
            asset.name === 'table_js' && !window.jQuery ? new Promise(resolve =>
                document.addEventListener('DOMContentLoaded', resolve, {once: true})) : null;
        pending[asset.name] = Promise.resolve(dependency).then(() => new Promise((resolve, reject) => {
            const script = document.createElement(asset.kind === 'css' ? 'link' : 'script');
            if (asset.kind === 'css') { script.rel = 'stylesheet'; script.href = asset.url; }
            else script.src = asset.url;
            script.integrity = asset.integrity;
            script.crossOrigin = 'anonymous'; script.dataset.hhAsset = asset.name;
            script.onload = resolve; script.onerror = () => reject(new Error('Failed to load '+asset.name));
            document.head.appendChild(script);
        }));
        pending[asset.name].then(() => window.initializeHandyhelpers?.(document));
    })();""".replace("SPEC", spec)
    return format_html("<script>{}</script>", mark_safe(javascript))
