import os
import re
import json

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save, post_delete
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy, ugettext as _

from guardian.shortcuts import assign_perm, get_perms_for_model

from taggit.managers import TaggableManager

from odk_logger.xform_instance_parser import XLSFormError
from stats.tasks import stat_log

from hashlib import md5


def upload_to(instance, filename):
    return os.path.join(
        instance.user.username,
        'xls',
        os.path.split(filename)[1])


class DuplicateUUIDError(Exception):
    pass


class XForm(models.Model):
    CLONED_SUFFIX = '_cloned'

    xls = models.FileField(upload_to=upload_to, null=True)
    json = models.TextField(default=u'')
    description = models.TextField(default=u'', null=True)
    xml = models.TextField()

    user = models.ForeignKey(User, related_name='xforms', null=True)
    shared = models.BooleanField(default=False)
    shared_data = models.BooleanField(default=False)
    form_active = models.BooleanField(default=True)
    is_crowd_form = models.BooleanField(default=False)
    allows_sms = models.BooleanField(default=False)
    encrypted = models.BooleanField(default=False)

    # the following fields are filled in automatically
    sms_id_string = models.SlugField(
        editable=False,
        verbose_name=ugettext_lazy("SMS ID"),
        default=''
    )
    id_string = models.SlugField(
        editable=False, verbose_name=ugettext_lazy("ID"), max_length=100
    )
    title = models.CharField(editable=False, max_length=64)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    last_submission_time = models.DateTimeField(blank=True, null=True)
    has_start_time = models.BooleanField(default=False)
    uuid = models.CharField(max_length=32, default=u'')

    uuid_regex = re.compile(r'(<instance>.*?id="[^"]+">)(.*</instance>)(.*)',
                            re.DOTALL)
    instance_id_regex = re.compile(r'<instance>.*?id="([^"]+)".*</instance>',
                                   re.DOTALL)
    uuid_node_location = 2
    uuid_bind_location = 4
    bamboo_dataset = models.CharField(max_length=60, default=u'')
    surveys_with_geopoints = models.BooleanField(default=False)
    num_of_submissions = models.IntegerField(default=-1)

    tags = TaggableManager()

    class Meta:
        app_label = 'odk_logger'
        unique_together = (("user", "id_string"), ("user", "sms_id_string"))
        verbose_name = ugettext_lazy("XForm")
        verbose_name_plural = ugettext_lazy("XForms")
        ordering = ("id_string",)
        permissions = (
            ("view_xform", _("Can view associated data")),
        )

    def file_name(self):
        return self.id_string + ".xml"

    def url(self):
        return reverse(
            "download_xform",
            kwargs={
                "username": self.user.username,
                "id_string": self.id_string
            }
        )

    def data_dictionary(self):
        from odk_viewer.models import DataDictionary
        return DataDictionary.objects.get(pk=self.pk)

    @property
    def has_surveys_with_geopoints(self):
        return self.surveys_with_geopoints

    def _set_id_string(self):
        matches = self.instance_id_regex.findall(self.xml)
        if len(matches) != 1:
            raise XLSFormError(_("There should be a single id string."))
        self.id_string = matches[0]

    def _set_title(self):
        text = re.sub(r"\s+", " ", self.xml)
        matches = re.findall(r"<h:title>([^<]+)</h:title>", text)
        if len(matches) > 1:
            raise XLSFormError(_("There should be a single title."), matches)
        self.title = self.id_string if not matches else matches[0]

    def _set_encrypted_field(self):
        if self.json and self.json != '':
            json_dict = json.loads(self.json)
            if 'submission_url' in json_dict and 'public_key' in json_dict:
                self.encrypted = True
            else:
                self.encrypted = False

    # That looks intersting.
    def update(self, *args, **kwargs):
        super(XForm, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        old_id_string = self.id_string
        if not old_id_string:
            self._set_id_string()
        self._set_encrypted_field()
        # check if we have an existing id_string,
        # if so, the one must match but only if xform is NOT new
        if self.pk and old_id_string and old_id_string != self.id_string:
            raise XLSFormError(
                _(u"Your updated form's id_string '%(new_id)s' must match "
                  "the existing forms' id_string '%(old_id)s'." %
                  {'new_id': self.id_string, 'old_id': old_id_string}))
        if getattr(settings, 'STRICT', True) and \
                not re.search(r"^[\w-]+$", self.id_string):
            raise XLSFormError(_(u'In strict mode, the XForm ID must be a '
                               'valid slug and contain no spaces.'))
        if not self.sms_id_string:
            try:
                # try to guess the form's wanted sms_id_string
                # from it's json rep (from XLSForm)
                # otherwise, use id_string to ensure uniqueness
                self.sms_id_string = json.loads(self.json).get('sms_keyword',
                                                               self.id_string)
            except:
                self.sms_id_string = self.id_string
        original_pk = self.pk
        super(XForm, self).save(*args, **kwargs)
        if self.pk != original_pk:
            self._set_title()
            print "Setting perms for ", self.pk
            for perm in get_perms_for_model(XForm):
                assign_perm(perm.codename, self.user, self)


    def __unicode__(self):
        return getattr(self, "id_string", "")

    def submission_count(self):
        if self.num_of_submissions == -1:
            count = self.surveys.filter(is_deleted=False).count()
            self.num_of_submissions = count
            self.save()
        return self.num_of_submissions
    submission_count.short_description = ugettext_lazy("Submission Count")

    def geocoded_submission_count(self):
        from odk_viewer.models import ParsedInstance
        return ParsedInstance.objects.filter(
            instance__in=self.surveys.filter(is_deleted=False),
            lat__isnull=False).count()
    geocoded_submission_count.short_description = \
        ugettext_lazy("Geocoded Submission Count")

    def time_of_last_submission(self):
        if self.last_submission_time is None and self.num_of_submissions > 0:
            try:
                last_submission = self.surveys.\
                    filter(is_deleted=False).latest("date_created")
            except ObjectDoesNotExist:
                pass
            else:
                self.last_submission_time = last_submission.date_created
                self.save()
        return self.last_submission_time

    def time_of_last_submission_update(self):
        try:
            # we also consider deleted surveys in this case
            return self.surveys.latest("date_modified").date_modified
        except ObjectDoesNotExist:
            pass

    @property
    def hash(self):
        return u'%s' % md5(self.xml.encode('utf8')).hexdigest()

    @property
    def can_be_replaced(self):
        if hasattr(self.submission_count, '__call__'):
            num_submissions = self.submission_count()
        else:
            num_submissions = self.submission_count
        return num_submissions == 0

    @classmethod
    def public_forms(cls):
        return cls.objects.filter(shared=True)


def stats_forms_created(sender, instance, created, **kwargs):
    print "created ", instance, created
    if created:
        stat_log.delay('formhub-forms-created', 1)

post_save.connect(stats_forms_created, sender=XForm)

def update_profile_num_submissions(sender, instance, **kwargs):
    profile_qs = User.profile.get_query_set()
    try:
        profile = profile_qs.select_for_update()\
            .get(pk=instance.user.profile.pk)
    except ObjectDoesNotExist:
        pass
    else:
        profile.num_of_submissions -= instance.num_of_submissions
        if profile.num_of_submissions < 0:
            profile.num_of_submissions = 0
        profile.save()

post_delete.connect(update_profile_num_submissions, sender=XForm,
                    dispatch_uid='update_profile_num_submissions')
