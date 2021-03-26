from .abstract import Manager, Model


# ----------------------------------------
# Managers
# ----------------------------------------


class ServiceDiscoveryNamespaceManager(Manager):

    service = 'servicediscovery'

    def get(self, pk, **kwargs):
        if pk.startsith('ns-'):
            # this is a namespace['Id']
            try:
                response = self.client.get_namespace(Id=pk)
            except self.client.NamespaceNotFound:
                raise ServiceDiscoveryNamespace.DoesNotExist(
                    'No Service Discovery namespace with id="{}" exists in AWS.'.format(pk)
                )
            return ServiceDiscoveryNamespace(response['Namespace'])
        else:
            # Assume this is a namespace['Name']
            namespaces = self.list(private_only=True)
            for namespace in namespaces:
                if namespace.name == pk:
                    return namespace
            raise ServiceDiscoveryNamespace.DoesNotExist(
                'No Service Discovery namespace with name="{}" exists in AWS.'.format(pk)
            )

    def list(self, private_only=False):
        kwargs = {}
        if private_only:
            kwargs['Filters'] = [{'Name': 'TYPE', 'Values': ['DNS_PRIVATE'], 'Condition': 'EQ'}]
        paginator = self.client.paginate('list_namespaces')
        response_iterator = paginator.paginate(**kwargs)
        namespaces = []
        for response in response_iterator:
            namespaces.extend(response['Namespaces'])
        return [ServiceDiscoveryNamespace(d) for d in namespaces]

    def save(self, obj):
        raise ServiceDiscoveryNamespace.ReadOnly('deployfish cannot modify Service Discovery namespaces')

    def delete(self, obj):
        raise ServiceDiscoveryNamespace.ReadOnly('deployfish cannot modify Service Discovery namespaces')


class ServiceDiscoveryServiceManager(Manager):

    service = 'servicediscovery'

    def _get_with_id(self, pk):
        """
        `pk` is a service['Id']: "srv-{hexstring}"
        """
        try:
            response = self.client.get_service(Id=pk)
        except self.client.ServiceNotFound:
            raise ServiceDiscoveryService.DoesNotExist(
                'No Service Discovery service with id="{}" exists in AWS.'.format(pk)
            )
        return ServiceDiscoveryNamespace(response['Namespace'])

    def _get_with_namespace_and_service_name(self, pk):
        """
        pk looks like '{namespace_pk}:{service_name}'
        """
        # this is a namespace_pk:service_name
        namespace_pk, service_name = pk.split(':')
        namespace = ServiceDiscoveryNamespace.objects.get(namespace_pk)
        services = self.list(namespace=namespace)
        for service in services:
            if service.name == service_name:
                return service
        raise ServiceDiscoveryService.DoesNotExist(
            'No Service Discovery service with name="{}" exists in namespace "{}" in AWS.'.format(pk, namespace_pk)
        )

    def _get_with_bare_service_name(self, pk):
        """
        `pk` is just a bare service name.
        """
        # this is just a bare service name
        services = self.list()
        found = []
        for service in services:
            if service.name == pk:
                found.append(service)
        if len(found) == 0:
            raise ServiceDiscoveryService.DoesNotExist(
                'No Service Discovery service with name="{}" exists in AWS.'.format(pk)
            )
        elif len(found) > 1:
            raise ServiceDiscoveryService.MultipleObjectsReturned(
                'More than one Service Discovery service with name="{}" exists in AWS.'.format(pk)
            )
        else:
            # We have to do this because the NamespaceId is not included in the services returned by
            # self.client.list_services, but is included in self.client.get_service
            return self.get(found[0].pk)

    def get(self, pk, **kwargs):
        """
        `pk` is one of::

            * a service id, which starts with "srv-"
            * a string like '{namespace_pk}:{service_name}'
            * a string like '{service_name}'
        """
        if pk.startsith('srv-'):
            return self._get_with_id(pk)
        elif ':' in pk:
            return self._get_with_namespace_and_service_name(pk)
        else:
            return self._get_with_bare_service_name(pk)

    def list(self, namespace=None):
        kwargs = {}
        if namespace:
            if not isinstance(namespace, ServiceDiscoveryNamespace):
                namespace = ServiceDiscoveryNamespace.objects.get(namespace)
            kwargs['Filters'] = [{'Name': 'NAMESPACE_ID', 'Values': [namespace.pk], 'Condition': 'EQ'}]
        paginator = self.client.paginate('list_services')
        response_iterator = paginator.paginate(**kwargs)
        services = []
        for response in response_iterator:
            services.extend(response['Services'])
        services = [ServiceDiscoveryService(d) for d in services]
        if namespace:
            for service in services:
                service.data['NamespaceId'] = namespace.pk
        return services

    def save(self, obj):
        try:
            response = self.client.create_service(**obj.render_for_create())
        except self.client.exceptions.NamespaceNotFound:
            raise ServiceDiscoveryService.NamespaceNotFound(
                'No Service Discovery namespace with name="{}" exists in AWS'.format(obj.namespace.name)
            )
        return response['Services'][0]['Arn']

    def delete(self, obj):
        try:
            self.client.delete_service(obj.pk)
        except self.client.exceptions.ServiceNotFound:
            raise ServiceDiscoveryService.DoesNotExist(
                'No Service Discovery service with id="{}" exists in AWS.'.format(obj.pk)
            )
        except self.client.exceptions.ResourceInUse:
            raise ServiceDiscoveryService.OperationalError(
                'Service Discovery service with id="{}" cannot be deleted because it is in use.'.format(obj.pk)
            )


# ----------------------------------------
# Models
# ----------------------------------------

class ServiceDiscoveryNamespace(Model):

    objects = ServiceDiscoveryNamespaceManager()

    @property
    def pk(self):
        return self.data['Id']

    @property
    def name(self):
        return self.data['Name']

    @property
    def arn(self):
        return self.data['Arn']

    def render_for_diff(self):
        data = self.render()
        del data['CreateDate']
        del data['CreateRequestorId']
        return data


class ServiceDiscoveryService(Model):

    objects = ServiceDiscoveryServiceManager()

    def __init__(self, data, **kwargs):
        self.namespace_name = kwargs.pop('namespace_name')
        super(ServiceDiscoveryService, self).__init__(self, **kwargs)

    @property
    def pk(self):
        if self.data.get('Id', None):
            return self.data['Id']
        elif self.data.get('NamespaceId', None):
            return "{}:{}".format(self.data['NamespaceId'], self.name)
        elif self.namespace_name:
            return "{}:{}".format(self.namespace_name, self.name)
        else:
            return self.name

    @property
    def name(self):
        return self.data['Name']

    @property
    def arn(self):
        return self.data['Arn']

    @property
    def namespace(self):
        if 'NamespaceId' in self.data:
            pk = self.data['NamespaceId']
        elif self.namespace_name:
            pk = self.namespace_name
        else:
            self.cache['namespace'] = None
            return None
        try:
            return self.get_cached('namespace', ServiceDiscoveryNamespace.objects.get, [pk])
        except ServiceDiscoveryNamespace.DoesNotExist:
            self.cache['namespace'] = None
            return None

    def render_for_diff(self):
        data = self.render()
        del data['Id']
        del data['Arn']
        del data['CreateDate']
        del data['CreateRequestorId']
        return data

    def render_for_create(self):
        return self.render_for_diff()

    def save(self):
        if not self.namespace:
            raise self.ImproperlyConfigured(
                'Service Discovery service "{}" has no namespace assigned'.format(self.name)
            )
        self.data['NamespaceId'] = self.namespace.pk
        self.data['DnsConfig']['NamespaceId'] = self.namespace.pk
        super(ServiceDiscoveryService, self).save()
