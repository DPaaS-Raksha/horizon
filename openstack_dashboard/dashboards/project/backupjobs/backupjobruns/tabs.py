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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs

from openstack_dashboard import api
from openstack_dashboard.api import raksha

LOG = logging.getLogger(__name__)


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = "project/backupjobs/backupjobruns/_detail_overview.html"

    def get_context_data(self, request):
        backupjobrun_id = self.tab_group.kwargs['backupjobrun_id']
        try:
            backupjobrun = raksha.backupjobrun_get(self.request, backupjobrun_id)
        except:
            redirect = reverse('horizon:project:backupjobs:index')
            msg = _('Unable to retrieve backupjobrun details.')
            exceptions.handle(request, msg, redirect=redirect)
        return {'backupjobrun': backupjobrun}


class BackupJobRunDetailTabs(tabs.TabGroup):
    slug = "backupjobrun_details"
    tabs = (OverviewTab,)
