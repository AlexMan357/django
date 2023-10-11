from django.contrib.auth.models import User, Group, Permission
from django.core.management import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.get(pk=4)
        group, created = Group.objects.get_or_create(
            name="profile_manager",
        )

        permission_profile = Permission.objects.get(
            codename="view_profile",
        )

        permission_logentry = Permission.objects.get(
            codename="view_logentry",
        )

        # add permission to group
        group.permissions.add(permission_profile)

        # connect user to group
        user.groups.add(group)

        # link user with permission directly
        user.user_permissions.add(permission_logentry)

        group.save()
        user.save()
