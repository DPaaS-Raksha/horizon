# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
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

from rakshaclient.v1 import client as rakshaclient

from django.conf import settings

from horizon import exceptions

from openstack_dashboard.api.base import url_for, APIDictWrapper


LOG = logging.getLogger(__name__)
FOLDER_DELIMITER = "/"


def backupjob_api(request):
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    raksha_url = ""
    try:
        raksha_url = url_for(request, 'backupjobs')
    except exceptions.ServiceCatalogException:
        LOG.debug('no backupjobs service configured.')
        return None

    LOG.debug('raksha connection created using token "%s" and url "%s"' %
              (request.user.token.id, raksha_url))
    c = rakshaclient.Client(request.user.username,
                             request.user.token.id,
                             project_id=request.user.tenant_id,
                             auth_url=raksha_url,
                             insecure=insecure,
                             http_log_debug=settings.DEBUG)
    c.client.auth_token = request.user.token.id
    c.client.management_url = raksha_url
    return c
                                         

def backupjob_get(request, backupjob_id):
    try:
        backupjobs = backupjob_api(request).backupjobs.get(backupjob_id)
        return backupjobs
    except :
        return None


def backupjob_list(request):
    backupjobs = backupjob_api(request).backupjobs.list()
    return backupjobs

def backupjob_create(request, context):
    backupjob = backupjob_api(request).backupjobs.create(context['instances'][0],
                                                         None, context['name'],
                                                         context['description'])
    return backupjob

def backupjob_execute(request, backupjob_id):
    return backupjob_api(request).backupjobs.execute(backupjob_id)

def backupjob_prepare(request, backupjob_id):
    return backupjob_api(request).backupjobs.prepare(backupjob_id)

def backupjob_delete(request, backupjob_id):
    backupjob_api(request).backupjobs.delete(backupjob_id)
    return True

def backupjobrun_get(request, backupjobrun_id):
    try:
        backupjobrun = backupjob_api(request).backupjobruns.get(backupjobrun_id)
        return backupjobrun
    except :
        return None

def backupjobrun_list(request, backupjob_id):
    backupjobruns = backupjob_api(request).backupjobruns.list(backupjob_id)
    return backupjobruns
                   
def backupjobrun_restore(request, backupjobrun_id):    
    backupjob_api(request).backupjobruns.restore(backupjobrun_id)
    return True
    
def backupjobrun_delete(request, backupjob_id, backupjobrun_id):
    backupjob_api(request).backupjobruns.delete(backupjobrun_id)
    return True


    

