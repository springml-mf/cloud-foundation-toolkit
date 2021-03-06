# Copyright 2019 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" This template creates an unmanaged instance group. """

def set_optional_property(receiver, source, property_name):
    """ If set, copies the given property value from one object to another. """

    if property_name in source:
        receiver[property_name] = source[property_name]


def generate_instance_url(project, zone, instance):
    """ Format the resource name as a resource URI. """

    is_self_link = '/' in instance or '.' in instance

    if is_self_link:
        instance_url = instance
    else:
        instance_url = 'projects/{}/zones/{}/instances/{}'
        instance_url = instance_url.format(project, zone, instance)

    return instance_url


def generate_config(context):
    """ Entry point for the deployment resources. """

    properties = context.properties
    name = properties.get('name', context.env['name'])
    project_id = properties.get('project', context.env['project'])
    zone = properties.get('zone')

    # Network formatting
    if 'network' in properties:
        network_name = properties.get('network')
        if not '/' in network_name:
            network_propertie = { 'network': 'global/networks/{}'.format(network_name) }
        else:
            network_propertie = { 'network': network_name }
    else:
        network_propertie = {}

    properties.update(network_propertie)

    # Create unmanaged instance group resource
    umig_properties = {
        'name': name,
        'project': project_id,
        'zone': zone
    }

    known_properties = [
        'description',
        'namedPorts',
        'region',
        'network',
    ]

    for prop in known_properties:
        set_optional_property(umig_properties, properties, prop)
        
    umig_resources = [
        {
            'name': name,
            'type': 'gcp-types/compute-v1:instanceGroups',
            'properties': umig_properties
        },
    ]

    # If instances are specified, add/remove them to/from the group.
    add_instances_resources = []
    remove_instances_resources = []
    instances = properties.get('instances', {
        'add': [],
        'delete': []
    })

    # Generate outputs
    umig_outputs = [
        {
            'name': 'selfLink',
            'value': '$(ref.{}.selfLink)'.format(name)
        },
        {
            'name': 'name',
            'value': '$(ref.{}.name)'.format(name)
        },
        {
            'name': 'zone',
            'value': '$(ref.{}.zone)'.format(name)
        }
    ]

    return {
        'resources': umig_resources + add_instances_resources + remove_instances_resources,
        'outputs': umig_outputs
    }
