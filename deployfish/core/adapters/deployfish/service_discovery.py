from typing import Any

from ..abstract import Adapter


class ServiceDiscoveryServiceAdapter(Adapter):
    """
    .. code-block:: python

        {
            'namespace': 'local',
            'name': 'test',
            'dns_records': [
                {
                    'type': 'A',
                    'ttl': '60',
                }
            ],
        }
    """

    def convert(self) -> tuple[dict[str, Any], dict[str, Any]]:
        data = {}
        data["Name"] = self.data["name"]
        data["DnsConfig"] = {}
        data["DnsConfig"]["RoutingPolicy"] = "MULTIVALUE"
        data["DnsConfig"]["DnsRecords"] = []
        for record in self.data["dns_records"]:
            data["DnsConfig"]["DnsRecords"].append({
                "Type": record["type"],
                "TTL": record["ttl"]
            })
        kwargs = {}
        kwargs["namespace_name"] = self.data["namespace"]
        return data, kwargs
