from djangosaml2.backends import Saml2Backend
from django.contrib.auth.models import Group
from django.conf import settings

class CustomSaml2Backend(Saml2Backend):
    def get_or_create_user(self, *args, **kwargs):
        user, created = super().get_or_create_user(*args, **kwargs)
        user.saml = True
        user.save()

        saml_group = saml_user_group()
        if saml_group:
            user.groups.add(saml_group)

        return user, created

def saml_user_group():
    group_name = getattr(settings, 'SAML_GROUP_NAME', None)
    if group_name:
        group, _ = Group.objects.get_or_create(name=group_name)
        return group
