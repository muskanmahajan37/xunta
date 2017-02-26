from __future__ import unicode_literals

from functools import reduce
from operator import ior

from future.builtins import int
from uuslug import uuslug

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible

from mezzanine.accounts import get_profile_model
from mezzanine.core.models import Displayable, Ownable
from mezzanine.core.request import current_request
from mezzanine.generic.models import Rating, Keyword, AssignedKeyword
from mezzanine.generic.fields import RatingField, CommentsField
from mezzanine.utils.importing import import_dotted_path
from django.utils.translation import ugettext_lazy as _

USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class Link(Displayable, Ownable):
    class Meta:
        verbose_name = _('推荐')
        verbose_name_plural = _('推荐')

    link = models.URLField(null=True,
        blank=(not getattr(settings, "LINK_REQUIRED", False)))
    rating = RatingField()
    comments = CommentsField()

    def get_absolute_url(self):
        return reverse("link_detail", kwargs={"slug": self.slug})

    @property
    def domain(self):
        return urlparse(self.url).netloc

    @property
    def url(self):
        if self.link:
            return self.link
        return current_request().build_absolute_uri(self.get_absolute_url())

    def save(self, *args, **kwargs):
        self.slug = uuslug(self.title, instance=self)
        keywords = []
        if not self.keywords_string and getattr(settings, "AUTO_TAG", False):
            func_name = getattr(settings, "AUTO_TAG_FUNCTION",
                                "drum.links.utils.auto_tag")
            keywords = import_dotted_path(func_name)(self)
        super(Link, self).save(*args, **kwargs)
        if keywords:
            lookup = reduce(ior, [Q(title__iexact=k) for k in keywords])
            for keyword in Keyword.objects.filter(lookup):
                self.keywords.add(AssignedKeyword(keyword=keyword), bulk=False)

@python_2_unicode_compatible
class Profile(models.Model):
    YEAR_IN_SCHOOL_CHOICES = (
        ('1', '白羊座'),
        ('2', '金牛座'),
        ('3', '双子座'),
        ('4', '巨蟹座'),
        ('5', '狮子座'),
        ('6', '处女座'),
        ('7', '天秤座'),
        ('8', '天蝎座'),
        ('9', '射手座'),
        ('10', '摩羯座'),
        ('11', '双鱼座'),
        ('12', '双鱼座'),
    )

    user = models.OneToOneField(USER_MODEL)
    address = models.CharField(blank=True, max_length=20, verbose_name=_('地址'))
    birthday = models.DateTimeField(_("生日"), help_text=_(""), blank=True, null=True, db_index=True)
    interest = models.CharField(blank=True,  max_length=20, verbose_name=_('爱好'))
    weight = models.IntegerField(default=150, blank=True, verbose_name=_('体重'))
    height = models.IntegerField(default=150, blank=True, verbose_name=_('身高'))
    constellate = models.CharField(blank=True, max_length=10, choices=YEAR_IN_SCHOOL_CHOICES, verbose_name=_('星座'))
    job = models.CharField(blank=True, max_length=10, verbose_name=_('职业'))
    movie_type = models.CharField(blank=True, max_length=10, verbose_name=_('电影类型'))
    sport_type = models.CharField(blank=True, max_length=10, verbose_name=_('运动爱好'))
    book_type = models.CharField(blank=True, max_length=10, verbose_name=_('书籍类型'))
    karma = models.IntegerField(default=0, editable=False)
    bio = models.TextField(blank=True, verbose_name=_('简介'))

    def __str__(self):
        return "%s (%s)" % (self.user, self.karma)


@receiver(post_save, sender=Rating)
@receiver(pre_delete, sender=Rating)
def karma(sender, **kwargs):
    """
    Each time a rating is saved, check its value and modify the
    profile karma for the related object's user accordingly.
    Since ratings are either +1/-1, if a rating is being edited,
    we can assume that the existing rating is in the other direction,
    so we multiply the karma modifier by 2. We also run this when
    a rating is deleted (undone), in which case we just negate the
    rating value from the karma.
    """
    rating = kwargs["instance"]
    value = int(rating.value)
    if "created" not in kwargs:
        value *= -1 #  Rating deleted
    elif not kwargs["created"]:
        value *= 2 #  Rating changed
    content_object = rating.content_object
    if rating.user != content_object.user:
        queryset = get_profile_model().objects.filter(user=content_object.user)
        queryset.update(karma=models.F("karma") + value)
