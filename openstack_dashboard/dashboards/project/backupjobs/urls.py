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

from django.conf.urls.defaults import patterns, url, include

from .views import IndexView, CreateView, DetailView
from .backupjobruns import urls as backupjobrun_urls

BACKUPJOBS = r'^(?P<backupjob_id>[^/]+)/%s$'

urlpatterns = patterns('openstack_dashboard.dashboards.project.backupjobs.views',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^create$', CreateView.as_view(), name='create'),
    #url(BACKUPJOBS % 'detail', DetailView.as_view(), name='detail'),
    url(r'^(?P<backupjob_id>[^/]+)/$',DetailView.as_view(), name='detail'),    
    url(r'^backupjobruns/', include(backupjobrun_urls, namespace='backupjobruns'))
)

