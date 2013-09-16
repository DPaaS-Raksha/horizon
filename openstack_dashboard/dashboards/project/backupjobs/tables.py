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

from django import template
from django.core.urlresolvers import reverse
from django.template import defaultfilters as filters
from django.utils.translation import ugettext_lazy as _
from django.utils import http

from horizon import exceptions
from horizon import tables

from openstack_dashboard import api
from openstack_dashboard.api import raksha

LOG = logging.getLogger(__name__)

class PrepareBackupJob(tables.BatchAction):
    name = "prepare"
    verbose_name = _("Prepare Backupjob")
    action_present = _("Prepare")
    action_past = _("Scheduled preparation of")
    classes = ("btn-simple", "btn-prepare")
    data_type_singular = _("BackupJob")
    data_type_plural = _("BackupJobs")
  
        
    def action(self, request, obj_id):
        try:
            backupjob_id = obj_id
            raksha.backupjob_prepare(request, backupjob_id)
            LOG.debug('Prepared backupjob %s successfully' % backupjob_id)
        except:
            msg = _('Failed to prepare backupjob %s') % backupjob_id
            LOG.info(msg)
            redirect = reverse("horizon:project:backupjobs:index")
            exceptions.handle(request, msg, redirect=redirect)
            
            
class ExecuteBackupJob(tables.BatchAction):
    name = "execute"
    verbose_name = _("Execute Backupjob")
    action_present = _("Execute")
    action_past = _("Scheduled execution of")
    classes = ("btn-simple", "btn-execute")
    data_type_singular = _("BackupJob")
    data_type_plural = _("BackupJobs")
        
    def action(self, request, obj_id):
        try:
            backupjob_id = obj_id
            raksha.backupjob_execute(request, backupjob_id)
            LOG.debug('Executed backupjob %s successfully' % backupjob_id)
        except:
            msg = _('Failed to execute backupjob %s') % backupjob_id
            LOG.info(msg)
            redirect = reverse("horizon:project:backupjobs:index")
            exceptions.handle(request, msg, redirect=redirect)            
            
class DeleteBackupJob(tables.DeleteAction):
    data_type_singular = _("BackupJob")
    data_type_plural = _("BackupJobs")

    def delete(self, request, backupjob_id):
        try:
            # Retrieve existing backupjobruns belonging to the backupjob.
            backupjobruns = raksha.backupjobrun_list(request, backupjob_id=backupjob_id)
            LOG.debug('BackupJob %s has backupjobruns: %s' %
                      (backupjob_id, [s.id for s in backupjobruns]))
            for s in backupjobruns:
                raksha.backupjobrun_delete(request, s.id)
                LOG.debug('Deleted backupjobrun %s' % s.id)

            raksha.backupjob_delete(request, backupjob_id)
            LOG.debug('Deleted backupjob %s successfully' % backupjob_id)
        except:
            msg = _('Failed to delete backupjob %s') % backupjob_id
            LOG.info(msg)
            redirect = reverse("horizon:project:backupjobs:index")
            exceptions.handle(request, msg, redirect=redirect)
            
class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, backupjob_id):
        backupjob = raksha.backupjob_get(request, backupjob_id)
        return backupjob

class CreateBackupJob(tables.LinkAction):
    name = "create"
    verbose_name = _("Create BackupJob")
    url = "horizon:project:backupjobs:create"
    classes = ("ajax-modal", "btn-create")

class BackupJobsTable(tables.DataTable):
    name = tables.Column( "name",
                        verbose_name=_("Name"),
                        link="horizon:project:backupjobs:detail")
      
    class Meta:
        name = "backupjobs"
        verbose_name = _("Backup Jobs")
        row_class = UpdateRow
        table_actions = (CreateBackupJob, DeleteBackupJob)
        row_actions = (PrepareBackupJob, ExecuteBackupJob, DeleteBackupJob,)
