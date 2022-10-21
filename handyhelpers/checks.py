from django.core.checks import Warning, register


@register()
def user_tags_depreciated(app_configs, **kwargs):
    errors = list()
    # errors.append(
    #     Warning(
    #         "The 'user_tags' template tags in django-handyhelpers has moved to 'handyhelper_tags'. Starting in "
    #         "version 0.2 'user_tags' will be unavailable to templates.",
    #         hint='change {% load user_tags %} to {% load handyhelper_tags %} in applicable templates.',
    #         id='user_tags',
    #         obj='django-handyhelpers',
    #     )
    # )
    return errors
