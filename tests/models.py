from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class Article(models.Model):
    author = models.ForeignKey('auth.User', null=True, blank=True)
    title = models.CharField(max_length=30)
    body = models.TextField()
    slug = models.SlugField(blank=True)


class CanonicalArticle(models.Model):
    author = models.ForeignKey('auth.User', null=True, blank=True)
    title = models.CharField(max_length=30)
    body = models.TextField()
    slug = models.SlugField(blank=True)

    def get_canonical_slug(self):
        if self.author:
            return "{0.author.username}-{0.slug}".format(self)
        return "unauthored-{0.slug}".format(self)


class CustomUser(AbstractBaseUser):
    contact = models.EmailField(max_length=255, unique=True)

    USERNAME_FIELD = 'contact'

    def get_short_name(self):
        return self.contact

    def get_full_name(self):
        return self.get_short_name()

    def __unicode__(self):
        return self.contact
