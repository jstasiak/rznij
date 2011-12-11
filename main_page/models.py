# -*- coding: utf-8 -*-
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.db import models

class Shortcut(models.Model):
    shortcut = models.TextField(unique = True, db_index = True, blank = True)
    url = models.TextField(db_index = True, validators = [URLValidator])
    created_at = models.DateTimeField(auto_now_add = True, db_index = True)
    use_count = models.IntegerField(default = 0, db_index = True)

    def bump_use_count(self):
        self.use_count += 1
        self.save()

    @classmethod
    def normalize_shortcut(class_object, shortcut):
        return re.sub(r'[\s/?&%]]', '-', shortcut)

    def clean(self):
        self.shortcut = Shortcut.normalize_shortcut(self.shortcut)

        if not self.shortcut:
            while not self.shortcut or not Shortcut.is_available(self.shortcut):
                self.shortcut = User.objects.make_random_password()

    @classmethod
    def is_available(class_object, shortcut):
        shortcut = class_object.normalize_shortcut(shortcut)
        return len(class_object.objects.filter(shortcut = shortcut)) == 0



