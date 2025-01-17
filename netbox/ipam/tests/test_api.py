import json

from django.urls import reverse
from django.conf import settings
from netaddr import IPNetwork
from rest_framework import status

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from ipam.choices import *
from ipam.models import Aggregate, IPAddress, Prefix, RIR, Role, RouteTarget, Service, VLAN, VLANGroup, VRF
from utilities.testing import APITestCase, APIViewTestCases, disable_warnings


class AppTest(APITestCase):

    def test_root(self):

        url = reverse('ipam-api:api-root')
        response = self.client.get('{}?format=api'.format(url), **self.header)

        self.assertEqual(response.status_code, 200)


class VRFTest(APIViewTestCases.APIViewTestCase):
    model = VRF
    brief_fields = ['display_name', 'id', 'name', 'prefix_count', 'rd', 'url']
    create_data = [
        {
            'name': 'VRF 4',
            'rd': '65000:4',
        },
        {
            'name': 'VRF 5',
            'rd': '65000:5',
        },
        {
            'name': 'VRF 6',
            'rd': '65000:6',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        vrfs = (
            VRF(name='VRF 1', rd='65000:1'),
            VRF(name='VRF 2', rd='65000:2'),
            VRF(name='VRF 3'),  # No RD
        )
        VRF.objects.bulk_create(vrfs)


class RouteTargetTest(APIViewTestCases.APIViewTestCase):
    model = RouteTarget
    brief_fields = ['id', 'name', 'url']
    create_data = [
        {
            'name': '65000:1004',
        },
        {
            'name': '65000:1005',
        },
        {
            'name': '65000:1006',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        route_targets = (
            RouteTarget(name='65000:1001'),
            RouteTarget(name='65000:1002'),
            RouteTarget(name='65000:1003'),
        )
        RouteTarget.objects.bulk_create(route_targets)


class RIRTest(APIViewTestCases.APIViewTestCase):
    model = RIR
    brief_fields = ['aggregate_count', 'id', 'name', 'slug', 'url']
    create_data = [
        {
            'name': 'RIR 4',
            'slug': 'rir-4',
        },
        {
            'name': 'RIR 5',
            'slug': 'rir-5',
        },
        {
            'name': 'RIR 6',
            'slug': 'rir-6',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        rirs = (
            RIR(name='RIR 1', slug='rir-1'),
            RIR(name='RIR 2', slug='rir-2'),
            RIR(name='RIR 3', slug='rir-3'),
        )
        RIR.objects.bulk_create(rirs)


class AggregateTest(APIViewTestCases.APIViewTestCase):
    model = Aggregate
    brief_fields = ['family', 'id', 'prefix', 'url']
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        rirs = (
            RIR(name='RIR 1', slug='rir-1'),
            RIR(name='RIR 2', slug='rir-2'),
        )
        RIR.objects.bulk_create(rirs)

        aggregates = (
            Aggregate(prefix=IPNetwork('10.0.0.0/8'), rir=rirs[0]),
            Aggregate(prefix=IPNetwork('172.16.0.0/12'), rir=rirs[0]),
            Aggregate(prefix=IPNetwork('192.168.0.0/16'), rir=rirs[0]),
        )
        Aggregate.objects.bulk_create(aggregates)

        cls.create_data = [
            {
                'prefix': '100.0.0.0/8',
                'rir': rirs[1].pk,
            },
            {
                'prefix': '101.0.0.0/8',
                'rir': rirs[1].pk,
            },
            {
                'prefix': '102.0.0.0/8',
                'rir': rirs[1].pk,
            },
        ]


class RoleTest(APIViewTestCases.APIViewTestCase):
    model = Role
    brief_fields = ['id', 'name', 'prefix_count', 'slug', 'url', 'vlan_count']
    create_data = [
        {
            'name': 'Role 4',
            'slug': 'role-4',
        },
        {
            'name': 'Role 5',
            'slug': 'role-5',
        },
        {
            'name': 'Role 6',
            'slug': 'role-6',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        roles = (
            Role(name='Role 1', slug='role-1'),
            Role(name='Role 2', slug='role-2'),
            Role(name='Role 3', slug='role-3'),
        )
        Role.objects.bulk_create(roles)


class PrefixTest(APIViewTestCases.APIViewTestCase):
    model = Prefix
    brief_fields = ['family', 'id', 'prefix', 'url']
    create_data = [
        {
            'prefix': '192.168.4.0/24',
        },
        {
            'prefix': '192.168.5.0/24',
        },
        {
            'prefix': '192.168.6.0/24',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        prefixes = (
            Prefix(prefix=IPNetwork('192.168.1.0/24')),
            Prefix(prefix=IPNetwork('192.168.2.0/24')),
            Prefix(prefix=IPNetwork('192.168.3.0/24')),
        )
        Prefix.objects.bulk_create(prefixes)

    def test_list_available_prefixes(self):
        """
        Test retrieval of all available prefixes within a parent prefix.
        """
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/24'))
        Prefix.objects.create(prefix=IPNetwork('192.0.2.64/26'))
        Prefix.objects.create(prefix=IPNetwork('192.0.2.192/27'))
        url = reverse('ipam-api:prefix-available-prefixes', kwargs={'pk': prefix.pk})
        self.add_permissions('ipam.view_prefix')

        # Retrieve all available IPs
        response = self.client.get(url, **self.header)
        available_prefixes = ['192.0.2.0/26', '192.0.2.128/26', '192.0.2.224/27']
        for i, p in enumerate(response.data):
            self.assertEqual(p['prefix'], available_prefixes[i])

    def test_create_single_available_prefix(self):
        """
        Test retrieval of the first available prefix within a parent prefix.
        """
        vrf = VRF.objects.create(name='Test VRF 1', rd='1234')
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/28'), vrf=vrf, is_pool=True)
        url = reverse('ipam-api:prefix-available-prefixes', kwargs={'pk': prefix.pk})
        self.add_permissions('ipam.add_prefix')

        # Create four available prefixes with individual requests
        prefixes_to_be_created = [
            '192.0.2.0/30',
            '192.0.2.4/30',
            '192.0.2.8/30',
            '192.0.2.12/30',
        ]
        for i in range(4):
            data = {
                'prefix_length': 30,
                'description': 'Test Prefix {}'.format(i + 1)
            }
            response = self.client.post(url, data, format='json', **self.header)
            self.assertHttpStatus(response, status.HTTP_201_CREATED)
            self.assertEqual(response.data['prefix'], prefixes_to_be_created[i])
            self.assertEqual(response.data['vrf']['id'], vrf.pk)
            self.assertEqual(response.data['description'], data['description'])

        # Try to create one more prefix
        response = self.client.post(url, {'prefix_length': 30}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertIn('detail', response.data)

        # Try to create invalid prefix type
        response = self.client.post(url, {'prefix_length': '30'}, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('prefix_length', response.data[0])

    def test_create_multiple_available_prefixes(self):
        """
        Test the creation of available prefixes within a parent prefix.
        """
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/28'), is_pool=True)
        url = reverse('ipam-api:prefix-available-prefixes', kwargs={'pk': prefix.pk})
        self.add_permissions('ipam.view_prefix', 'ipam.add_prefix')

        # Try to create five /30s (only four are available)
        data = [
            {'prefix_length': 30, 'description': 'Test Prefix 1'},
            {'prefix_length': 30, 'description': 'Test Prefix 2'},
            {'prefix_length': 30, 'description': 'Test Prefix 3'},
            {'prefix_length': 30, 'description': 'Test Prefix 4'},
            {'prefix_length': 30, 'description': 'Test Prefix 5'},
        ]
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertIn('detail', response.data)

        # Verify that no prefixes were created (the entire /28 is still available)
        response = self.client.get(url, **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['prefix'], '192.0.2.0/28')

        # Create four /30s in a single request
        response = self.client.post(url, data[:4], format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 4)

    def test_list_available_ips(self):
        """
        Test retrieval of all available IP addresses within a parent prefix.
        """
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/29'), is_pool=True)
        url = reverse('ipam-api:prefix-available-ips', kwargs={'pk': prefix.pk})
        self.add_permissions('ipam.view_prefix', 'ipam.view_ipaddress')

        # Retrieve all available IPs
        response = self.client.get(url, **self.header)
        self.assertEqual(len(response.data), 8)  # 8 because prefix.is_pool = True

        # Change the prefix to not be a pool and try again
        prefix.is_pool = False
        prefix.save()
        response = self.client.get(url, **self.header)
        self.assertEqual(len(response.data), 6)  # 8 - 2 because prefix.is_pool = False

    def test_create_single_available_ip(self):
        """
        Test retrieval of the first available IP address within a parent prefix.
        """
        vrf = VRF.objects.create(name='Test VRF 1', rd='1234')
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/30'), vrf=vrf, is_pool=True)
        url = reverse('ipam-api:prefix-available-ips', kwargs={'pk': prefix.pk})
        self.add_permissions('ipam.view_prefix', 'ipam.add_ipaddress')

        # Create all four available IPs with individual requests
        for i in range(1, 5):
            data = {
                'description': 'Test IP {}'.format(i)
            }
            response = self.client.post(url, data, format='json', **self.header)
            self.assertHttpStatus(response, status.HTTP_201_CREATED)
            self.assertEqual(response.data['vrf']['id'], vrf.pk)
            self.assertEqual(response.data['description'], data['description'])

        # Try to create one more IP
        response = self.client.post(url, {}, **self.header)
        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertIn('detail', response.data)

    def test_create_multiple_available_ips(self):
        """
        Test the creation of available IP addresses within a parent prefix.
        """
        prefix = Prefix.objects.create(prefix=IPNetwork('192.0.2.0/29'), is_pool=True)
        url = reverse('ipam-api:prefix-available-ips', kwargs={'pk': prefix.pk})
        self.add_permissions('ipam.view_prefix', 'ipam.add_ipaddress')

        # Try to create nine IPs (only eight are available)
        data = [{'description': f'Test IP {i}'} for i in range(1, 10)]  # 9 IPs
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertIn('detail', response.data)

        # Create all eight available IPs in a single request
        data = [{'description': 'Test IP {}'.format(i)} for i in range(1, 9)]  # 8 IPs
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 8)

    def test_reserve_too_much_available_ips(self):
        """
        Test that reserving too many available IPs per request is forbidden
        """
        prefix = Prefix.objects.create(prefix=IPNetwork('10.0.0.0/16'), is_pool=True)
        url = reverse('ipam-api:prefix-available-ips', kwargs={'pk': prefix.pk})
        self.add_permissions('ipam.view_prefix', 'ipam.add_ipaddress')

        data = [{'description': f'Test IP {i}'} for i in range(0, settings.IPAM_MAX_RESERVABLE_IPS + 1)]
        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('requested_ips', response.data)


class IPAddressTest(APIViewTestCases.APIViewTestCase):
    model = IPAddress
    brief_fields = ['address', 'family', 'id', 'url']
    create_data = [
        {
            'address': '192.168.0.4/24',
        },
        {
            'address': '192.168.0.5/24',
        },
        {
            'address': '192.168.0.6/24',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        ip_addresses = (
            IPAddress(address=IPNetwork('192.168.0.1/24')),
            IPAddress(address=IPNetwork('192.168.0.2/24')),
            IPAddress(address=IPNetwork('192.168.0.3/24')),
        )
        IPAddress.objects.bulk_create(ip_addresses)


class VLANGroupTest(APIViewTestCases.APIViewTestCase):
    model = VLANGroup
    brief_fields = ['id', 'name', 'slug', 'url', 'vlan_count']
    create_data = [
        {
            'name': 'VLAN Group 4',
            'slug': 'vlan-group-4',
        },
        {
            'name': 'VLAN Group 5',
            'slug': 'vlan-group-5',
        },
        {
            'name': 'VLAN Group 6',
            'slug': 'vlan-group-6',
        },
    ]
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        vlan_groups = (
            VLANGroup(name='VLAN Group 1', slug='vlan-group-1'),
            VLANGroup(name='VLAN Group 2', slug='vlan-group-2'),
            VLANGroup(name='VLAN Group 3', slug='vlan-group-3'),
        )
        VLANGroup.objects.bulk_create(vlan_groups)


class VLANTest(APIViewTestCases.APIViewTestCase):
    model = VLAN
    brief_fields = ['display_name', 'id', 'name', 'url', 'vid']
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):

        vlan_groups = (
            VLANGroup(name='VLAN Group 1', slug='vlan-group-1'),
            VLANGroup(name='VLAN Group 2', slug='vlan-group-2'),
        )
        VLANGroup.objects.bulk_create(vlan_groups)

        vlans = (
            VLAN(name='VLAN 1', vid=1, group=vlan_groups[0]),
            VLAN(name='VLAN 2', vid=2, group=vlan_groups[0]),
            VLAN(name='VLAN 3', vid=3, group=vlan_groups[0]),
        )
        VLAN.objects.bulk_create(vlans)

        cls.create_data = [
            {
                'vid': 4,
                'name': 'VLAN 4',
                'group': vlan_groups[1].pk,
            },
            {
                'vid': 5,
                'name': 'VLAN 5',
                'group': vlan_groups[1].pk,
            },
            {
                'vid': 6,
                'name': 'VLAN 6',
                'group': vlan_groups[1].pk,
            },
        ]

    def test_delete_vlan_with_prefix(self):
        """
        Attempt and fail to delete a VLAN with a Prefix assigned to it.
        """
        vlan = VLAN.objects.first()
        Prefix.objects.create(prefix=IPNetwork('192.0.2.0/24'), vlan=vlan)

        self.add_permissions('ipam.delete_vlan')
        url = reverse('ipam-api:vlan-detail', kwargs={'pk': vlan.pk})
        with disable_warnings('django.request'):
            response = self.client.delete(url, **self.header)

        self.assertHttpStatus(response, status.HTTP_409_CONFLICT)

        content = json.loads(response.content.decode('utf-8'))
        self.assertIn('detail', content)
        self.assertTrue(content['detail'].startswith('Unable to delete object.'))


class ServiceTest(APIViewTestCases.APIViewTestCase):
    model = Service
    brief_fields = ['id', 'name', 'ports', 'protocol', 'url']
    bulk_update_data = {
        'description': 'New description',
    }

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name='Site 1', slug='site-1')
        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model='Device Type 1')
        devicerole = DeviceRole.objects.create(name='Device Role 1', slug='device-role-1')

        devices = (
            Device(name='Device 1', site=site, device_type=devicetype, device_role=devicerole),
            Device(name='Device 2', site=site, device_type=devicetype, device_role=devicerole),
        )
        Device.objects.bulk_create(devices)

        services = (
            Service(device=devices[0], name='Service 1', protocol=ServiceProtocolChoices.PROTOCOL_TCP, ports=[1]),
            Service(device=devices[0], name='Service 2', protocol=ServiceProtocolChoices.PROTOCOL_TCP, ports=[2]),
            Service(device=devices[0], name='Service 3', protocol=ServiceProtocolChoices.PROTOCOL_TCP, ports=[3]),
        )
        Service.objects.bulk_create(services)

        cls.create_data = [
            {
                'device': devices[1].pk,
                'name': 'Service 4',
                'protocol': ServiceProtocolChoices.PROTOCOL_TCP,
                'ports': [4],
            },
            {
                'device': devices[1].pk,
                'name': 'Service 5',
                'protocol': ServiceProtocolChoices.PROTOCOL_TCP,
                'ports': [5],
            },
            {
                'device': devices[1].pk,
                'name': 'Service 6',
                'protocol': ServiceProtocolChoices.PROTOCOL_TCP,
                'ports': [6],
            },
        ]
