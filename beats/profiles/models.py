from django.utils.translation import gettext_lazy as _
from beats.core.models import AbstractBaseModel, models


def upload_to_avatar(instance, filename):
    return f'profiles/avatars/{instance.user.pk}/{filename}'


class Profile(AbstractBaseModel):
    
    user = models.OneToOneField('auth.User', verbose_name=_('user'), on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(verbose_name=_('bio'), blank=True)
    avatar = models.ImageField(verbose_name=_('avatar'), upload_to=upload_to_avatar, blank=True, null=True)

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    def __str__(self):
        return f'{self.user.username}'