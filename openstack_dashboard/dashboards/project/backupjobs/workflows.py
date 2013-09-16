# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 NEC Corporation
# Copyright (c) 2013 TrilioData, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import logging
import netaddr

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon import workflows
from horizon.utils import fields

from openstack_dashboard import api
from openstack_dashboard.api import raksha
from openstack_dashboard.api import nova
from openstack_dashboard.usage import quotas

LOG = logging.getLogger(__name__)


class SelectProjectUserAction(workflows.Action):
    project_id = forms.ChoiceField(label=_("Project"))
    user_id = forms.ChoiceField(label=_("User"))

    def __init__(self, request, *args, **kwargs):
        super(SelectProjectUserAction, self).__init__(request, *args, **kwargs)
        # Set our project choices
        projects = [(tenant.id, tenant.name)
                    for tenant in request.user.authorized_tenants]
        self.fields['project_id'].choices = projects

        # Set our user options
        users = [(request.user.id, request.user.username)]
        self.fields['user_id'].choices = users

    class Meta:
        name = _("Project & User")
        # Unusable permission so this is always hidden. However, we
        # keep this step in the workflow for validation/verification purposes.
        permissions = ("!",)


class SelectProjectUser(workflows.Step):
    action_class = SelectProjectUserAction
    contributes = ("project_id", "user_id")

class SetBackupJobDetailsAction(workflows.Action):
    name = forms.CharField(max_length=80, label=_("Backup Job Name"))
    description = forms.CharField(max_length=1024, label=_("Backup Job Description"))

    class Meta:
        name = _("Details")
        help_text_template = ("project/backupjobs/"
                              "_backupjob_details_help.html")
    def clean(self):
        cleaned_data = super(SetBackupJobDetailsAction, self).clean()

        # Validate our instance source.
        name = cleaned_data['name']
        # There should always be at least one image_id choice, telling the user
        # that there are "No Images Available" so we check for 2 here...
        if name == None or name == '':
            raise forms.ValidationError(_("There is no name for backup job"))
        if not cleaned_data['name']:
            raise forms.ValidationError(_("Please enter name of the backup job"))

        return cleaned_data


class SetBackupJobDetails(workflows.Step):
    action_class = SetBackupJobDetailsAction
    contributes = ("name", "description")

"""
    def contribute(self, data, context):
        context = super(SetBackupJobDetails, self).contribute(data, context)

        # Translate form input to context for name values.
        if 'name' in data:
            context['name'] = data.get(data['name'], None)

        if 'description' in data:
            context['description'] = data.get(data['description'], None)

        return context
"""

class SetInstancesAction(workflows.Action):
    instances = forms.MultipleChoiceField(label=_("Instances"),
                                        required=True,
                                        widget=forms.CheckboxSelectMultiple(),
                                        error_messages={
                                            'required': _(
                                                "At least one instance must"
                                                " be specified.")},
                                        help_text=_("Create backup job with"
                                                    "these instances"))

    class Meta:
        name = _("Instances")
        permissions = ('openstack.services.compute',)
        help_text = _("Select instances for your backup job.")

    def populate_instances_choices(self, request, context):
        try:
            tenant_id = self.request.user.tenant_id
            instances = api.nova.server_list(request)
            instance_list = [(instance.id, instance.name) for instance in instances]
        except:
            instance_list = []
            exceptions.handle(request,
                              _('Unable to retrieve instances.'))
        return instance_list

class SetInstances(workflows.Step):
    action_class = SetInstancesAction
    template_name = "project/backupjobs/_update_instances.html"
    contributes = ("instances",)

    def contribute(self, data, context):
        if data:
            instances = self.workflow.request.POST.getlist("instances")
            if instances:
                context['instances'] = instances
        return context

class SetBackupIntervalAction(workflows.Action):
    interval = forms.CharField(widget=forms.Textarea,
                                           label=_("Backup Interval"),
                                           required=False,
                                           help_text=_("A backup iternval"
                                                       "specifies how frequently"
                                                       "the resources should be"
                                                       "backed up"))

    class Meta:
        name = _("Backup Interval")
        help_text_template = ("project/backupjobs/"
                              "_create_interval_help.html")


class SetBackupInterval(workflows.Step):
    action_class = SetBackupIntervalAction
    contributes = ("interval",)


class CreateBackupJob(workflows.Workflow):
    slug = "create_backupjob"
    name = _("Create Backup Job")
    finalize_button_name = _("Create")
    success_message = _('Create a backup job named "%(name)s".')
    failure_message = _('Unable to create backup job named "%(name)s".')
    default_steps = (SelectProjectUser,
                     SetBackupJobDetails,
                     SetInstances,
                     SetBackupInterval)


    def get_success_url(self):
        return reverse("horizon:project:backupjobs:index")

    def get_failure_url(self):
        return reverse("horizon:project:backupjobs:index")

    def format_status_message(self, message):
        name = self.context.get('name', '')
        return message % {"name": name}

    def handle(self, request, data):
        try:
            raksha.backupjob_create(request, context = self.context)
            return True
        except:
            exceptions.handle(request)
            return False
