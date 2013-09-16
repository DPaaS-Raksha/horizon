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

"""
Views for managing Raksha BackupJobs.
"""
import logging

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tables
from horizon import workflows

from openstack_dashboard import api
from openstack_dashboard.api import raksha
from .tables import BackupJobsTable
from .backupjobruns.tables import BackupJobRunsTable
from .workflows import CreateBackupJob


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = BackupJobsTable
    template_name = 'project/backupjobs/index.html'

    def get_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            #backupjobs = raksha.backupjob_list_for_tenant(self.request,
            #                                               tenant_id)
            backupjobs = raksha.backupjob_list(self.request)
        except:
            backupjobs = []
            msg = _('BackupJob list can not be retrieved.')
            exceptions.handle(self.request, msg)

        return backupjobs

class CreateView(workflows.WorkflowView):
    workflow_class = CreateBackupJob
    template_name = 'project/backupjobs/create.html'

    def get_initial(self):
        pass


class DetailView(tables.DataTableView):
    table_class = BackupJobRunsTable
    template_name = 'project/backupjobs/detail.html'
    failure_url = reverse_lazy('horizon:project:backupjobs:index')

    def get_data(self):
        try:
            backupjob = self._get_data()
            backupjobruns = raksha.backupjobrun_list(self.request,
                                              backupjob_id=backupjob.id)
        except:
            backupjobruns = []
            msg = _('BackupJobRuns list can not be retrieved.')
            exceptions.handle(self.request, msg)
        return backupjobruns
        
    def _get_data(self):
        if not hasattr(self, "_backupjob"):
            try:
                backupjob_id = self.kwargs['backupjob_id']
                backupjob = raksha.backupjob_get(self.request, backupjob_id)
            except:
                msg = _('Unable to retrieve details for backupjob "%s".') \
                      % (backupjob_id)
                exceptions.handle(self.request, msg, redirect=self.failure_url)
            self._backupjob = backupjob
        return self._backupjob

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["backupjob"] = self._get_data()
        return context
