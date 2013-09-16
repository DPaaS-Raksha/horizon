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

from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tables

from openstack_dashboard import api
from openstack_dashboard.api import raksha

LOG = logging.getLogger(__name__)

class RestoreBackupJobRun(tables.BatchAction):
    name = "restore"
    verbose_name = _("Restore BackupJobRun")
    action_present = _("Restore")
    action_past = _("Scheduled restore of")
    classes = ("btn-simple", "btn-restore")
    data_type_singular = _("BackupJobRun")
    data_type_plural = _("BackupJobRuns")

      
    def action(self, request, obj_id):
        try:
            raksha.backupjobrun_restore(request, obj_id)
        except:
            msg = _('Failed to restore backupjobrun %s') % obj_id
            LOG.info(msg)
            redirect = reverse('horizon:project:backupjobruns:detail',
                               args=[obj_id])
            exceptions.handle(request, msg, redirect=redirect)

class DeleteBackupJobRun(tables.DeleteAction):
    data_type_singular = _("BackupJobRun")
    data_type_plural = _("BackupJobRuns")

    def delete(self, request, obj_id):
        try:
            raksha.backupjobrun_delete(request, obj_id)
        except:
            msg = _('Failed to delete backupjobrun %s') % obj_id
            LOG.info(msg)
            redirect = reverse('horizon:project:backupjobruns:detail',
                               args=[obj_id])
            exceptions.handle(request, msg, redirect=redirect)

class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, backupjobrun_id):
        backupjob = raksha.backupjobrun_get(request, backupjobrun_id)
        return backupjob


class BackupJobRunsTable(tables.DataTable):
    name = tables.Column("name", verbose_name=_("ID"),
                         link='horizon:project:backupjobruns:detail')
    failure_url = reverse_lazy('horizon:project:backupjobs:index')

    class Meta:
        name = "backupjobruns"
        verbose_name = _("BackupJobRuns")
        row_class = UpdateRow
        table_actions = (DeleteBackupJobRun,)
        row_actions = (RestoreBackupJobRun,)
