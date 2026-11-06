import ipaddress
from concurrent.futures import ThreadPoolExecutor
from backend.services.ping_service import PingService

class NetworkScanner:
    @staticmethod
    def scan_subnet(cidr: str, max_threads: int = 15, max_hosts: int = 20):
        """
        Scans a subnet/CIDR range up to max_hosts and returns status of hosts.
        """
        try:
            network = ipaddress.ip_network(cidr, strict=False)
        except ValueError as e:
            return {"error": f"Invalid CIDR notation: {str(e)}", "hosts": []}

        # Scan a limited set of hosts for performance in web requests
        hosts_to_scan = [str(ip) for ip in list(network.hosts())[:max_hosts]]

        results = []
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            future_to_ip = {executor.submit(PingService.ping, ip, 1, 1.0): ip for ip in hosts_to_scan}
            for future in future_to_ip:
                res = future.result()
                results.append(res)

        online_count = sum(1 for r in results if r["status"] == "ONLINE")
        return {
            "subnet": cidr,
            "total_scanned": len(results),
            "online_hosts": online_count,
            "results": results
        }
