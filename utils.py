import socket
import ipaddress
import csv
import re


HOSTNAME_PATTERN = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
    r"(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*$"
)

PORT_INFO = {
    20: ("FTP-DATA", "FTP file transfer data channel"),
    21: ("FTP", "File Transfer Protocol control channel"),
    22: ("SSH", "Secure Shell remote login"),
    23: ("Telnet", "Unencrypted remote terminal access"),
    25: ("SMTP", "Simple Mail Transfer Protocol"),
    37: ("Time", "Time protocol"),
    42: ("WINS", "Windows Internet Name Service"),
    43: ("WHOIS", "WHOIS directory service"),
    49: ("TACACS", "Terminal Access Controller Access-Control System"),
    53: ("DNS", "Domain Name System resolution"),
    67: ("DHCP", "Dynamic Host Configuration Protocol server"),
    68: ("DHCP", "Dynamic Host Configuration Protocol client"),
    69: ("TFTP", "Trivial File Transfer Protocol"),
    70: ("Gopher", "Gopher document retrieval protocol"),
    79: ("Finger", "User information lookup service"),
    80: ("HTTP", "Unencrypted web traffic"),
    88: ("Kerberos", "Network authentication protocol"),
    102: ("MS-EXCH", "Microsoft Exchange ISO transport"),
    110: ("POP3", "Post Office Protocol mail retrieval"),
    111: ("RPCbind", "Remote Procedure Call port mapper"),
    113: ("Ident", "Identification protocol"),
    119: ("NNTP", "Network News Transfer Protocol"),
    123: ("NTP", "Network Time Protocol"),
    135: ("MSRPC", "Microsoft RPC endpoint mapper"),
    137: ("NetBIOS-NS", "NetBIOS Name Service"),
    138: ("NetBIOS-DGM", "NetBIOS Datagram Service"),
    139: ("NetBIOS-SSN", "NetBIOS Session Service"),
    143: ("IMAP", "Internet Message Access Protocol"),
    161: ("SNMP", "Simple Network Management Protocol"),
    162: ("SNMP-Trap", "SNMP trap notifications"),
    177: ("XDMCP", "X Display Manager Control Protocol"),
    179: ("BGP", "Border Gateway Protocol routing"),
    194: ("IRC", "Internet Relay Chat"),
    201: ("AppleTalk", "AppleTalk routing maintenance"),
    264: ("BGMP", "Border Gateway Multicast Protocol"),
    318: ("PKIX-TIMESTAMP", "Time stamp protocol"),
    381: ("HP-OpenView", "HP OpenView data collection"),
    383: ("HP-OpenView", "HP OpenView alarm manager"),
    389: ("LDAP", "Lightweight Directory Access Protocol"),
    427: ("SLP", "Service Location Protocol"),
    443: ("HTTPS", "Secure web traffic"),
    444: ("SNPP", "Simple Network Paging Protocol"),
    445: ("SMB", "Microsoft Server Message Block file sharing"),
    464: ("Kerberos", "Kerberos password change"),
    465: ("SMTPS", "SMTP over implicit TLS"),
    500: ("ISAKMP", "Internet Security Association and Key Management"),
    512: ("Rexec", "Remote process execution"),
    513: ("Rlogin", "Remote login service"),
    514: ("Syslog", "System logging protocol"),
    515: ("LPD", "Line Printer Daemon"),
    520: ("RIP", "Routing Information Protocol"),
    521: ("RIPng", "RIP next generation for IPv6"),
    540: ("UUCP", "Unix-to-Unix Copy Protocol"),
    548: ("AFP", "Apple Filing Protocol"),
    554: ("RTSP", "Real Time Streaming Protocol"),
    563: ("NNTPS", "NNTP over TLS"),
    587: ("SMTP-Submission", "Mail submission over SMTP"),
    591: ("FileMaker", "FileMaker web sharing"),
    593: ("MSRPC-HTTP", "RPC over HTTP"),
    623: ("IPMI", "Intelligent Platform Management Interface"),
    631: ("IPP", "Internet Printing Protocol"),
    636: ("LDAPS", "LDAP over TLS"),
    639: ("MSDP", "Multicast Source Discovery Protocol"),
    646: ("LDP", "Label Distribution Protocol"),
    691: ("MS-Exchange", "Microsoft Exchange routing"),
    860: ("iSCSI", "Internet Small Computer Systems Interface"),
    873: ("Rsync", "Remote file synchronization"),
    902: ("VMware", "VMware server management"),
    989: ("FTPS-DATA", "FTP over implicit TLS data channel"),
    990: ("FTPS", "FTP over implicit TLS control channel"),
    993: ("IMAPS", "IMAP over TLS"),
    995: ("POP3S", "POP3 over TLS"),
    1025: ("NFS-or-IIS", "Windows RPC or IIS service"),
    1026: ("LSA-or-nterm", "Windows LSA or remote terminal"),
    1027: ("MSRPC", "Microsoft RPC dynamic port"),
    1028: ("MSRPC", "Microsoft RPC dynamic port"),
    1029: ("MSRPC", "Microsoft RPC dynamic port"),
    1080: ("SOCKS", "SOCKS proxy protocol"),
    1194: ("OpenVPN", "OpenVPN tunnel protocol"),
    1214: ("Kazaa", "Peer-to-peer file sharing"),
    1241: ("Nessus", "Nessus vulnerability scanner"),
    1311: ("Dell-OpenManage", "Dell server administration"),
    1337: ("WASTE", "Encrypted file sharing"),
    1433: ("MSSQL", "Microsoft SQL Server"),
    1434: ("MSSQL-Monitor", "Microsoft SQL Server monitor"),
    1512: ("WINS", "Windows Internet Name Service"),
    1521: ("Oracle-DB", "Oracle database listener"),
    1701: ("L2TP", "Layer 2 Tunneling Protocol"),
    1723: ("PPTP", "Point-to-Point Tunneling Protocol"),
    1755: ("MS-Streaming", "Microsoft media streaming"),
    1900: ("SSDP", "Simple Service Discovery Protocol"),
    2000: ("Cisco-SCCP", "Cisco Skinny Call Control Protocol"),
    2049: ("NFS", "Network File System"),
    2082: ("cPanel", "cPanel control panel"),
    2083: ("cPanel-SSL", "cPanel control panel over TLS"),
    2086: ("WHM", "Web Host Manager"),
    2087: ("WHM-SSL", "Web Host Manager over TLS"),
    2095: ("Webmail", "Webmail access"),
    2096: ("Webmail-SSL", "Webmail access over TLS"),
    2181: ("ZooKeeper", "Apache ZooKeeper coordination service"),
    2222: ("DirectAdmin", "DirectAdmin control panel or alt SSH"),
    2375: ("Docker", "Docker daemon API"),
    2376: ("Docker-TLS", "Docker daemon API over TLS"),
    2483: ("Oracle-DB", "Oracle database listener"),
    2484: ("Oracle-DB-SSL", "Oracle database listener over TLS"),
    3000: ("Dev-Server", "Common development web server"),
    3128: ("Squid-Proxy", "Squid caching proxy"),
    3260: ("iSCSI-Target", "iSCSI target service"),
    3268: ("LDAP-GC", "LDAP Global Catalog"),
    3269: ("LDAP-GC-SSL", "LDAP Global Catalog over TLS"),
    3306: ("MySQL", "MySQL database server"),
    3389: ("RDP", "Remote Desktop Protocol"),
    3690: ("SVN", "Subversion version control"),
    3724: ("WoW", "Battle.net game server"),
    4333: ("mSQL", "mSQL database service"),
    4444: ("Metasploit", "Common backdoor or Metasploit default"),
    4500: ("IPsec-NAT-T", "IPsec NAT traversal"),
    4664: ("Google-Desktop", "Google Desktop search service"),
    4848: ("GlassFish", "GlassFish application server admin"),
    5000: ("UPnP", "Universal Plug and Play or dev server"),
    5001: ("Synology", "Synology management or alt HTTP"),
    5060: ("SIP", "Session Initiation Protocol"),
    5061: ("SIP-TLS", "SIP over TLS"),
    5222: ("XMPP", "Extensible Messaging and Presence Protocol"),
    5353: ("mDNS", "Multicast DNS"),
    5432: ("PostgreSQL", "PostgreSQL database server"),
    5555: ("ADB", "Android Debug Bridge"),
    5601: ("Kibana", "Kibana data visualization dashboard"),
    5631: ("pcAnywhere", "Symantec pcAnywhere data"),
    5632: ("pcAnywhere", "Symantec pcAnywhere status"),
    5666: ("NRPE", "Nagios Remote Plugin Executor"),
    5672: ("AMQP", "Advanced Message Queuing Protocol"),
    5900: ("VNC", "Virtual Network Computing remote desktop"),
    5901: ("VNC-1", "VNC display 1"),
    5984: ("CouchDB", "Apache CouchDB database"),
    6000: ("X11", "X Window System display server"),
    6379: ("Redis", "Redis in-memory data store"),
    6443: ("Kubernetes-API", "Kubernetes API server"),
    6660: ("IRC", "Internet Relay Chat alt port"),
    6667: ("IRC", "Internet Relay Chat"),
    6881: ("BitTorrent", "BitTorrent peer traffic"),
    7000: ("Cassandra", "Apache Cassandra inter-node"),
    7001: ("WebLogic", "Oracle WebLogic server"),
    7077: ("Spark", "Apache Spark master"),
    7199: ("Cassandra-JMX", "Cassandra JMX monitoring"),
    7443: ("Alt-HTTPS", "Alternate secure web port"),
    7474: ("Neo4j", "Neo4j graph database HTTP"),
    8000: ("HTTP-Alt", "Alternate HTTP or dev server"),
    8008: ("HTTP-Alt", "Alternate HTTP port"),
    8020: ("Hadoop-NameNode", "Hadoop distributed file system"),
    8080: ("HTTP-Proxy", "Common HTTP proxy or alt web port"),
    8081: ("HTTP-Alt", "Alternate HTTP port"),
    8086: ("InfluxDB", "InfluxDB time series database"),
    8088: ("Hadoop-Yarn", "Hadoop YARN resource manager"),
    8161: ("ActiveMQ", "Apache ActiveMQ web console"),
    8200: ("Vault", "HashiCorp Vault API"),
    8222: ("VMware-Server", "VMware server management"),
    8443: ("HTTPS-Alt", "Alternate secure web port"),
    8500: ("Consul", "HashiCorp Consul service discovery"),
    8530: ("WSUS", "Windows Server Update Services"),
    8531: ("WSUS-SSL", "Windows Server Update Services over TLS"),
    8888: ("HTTP-Alt", "Alternate HTTP or Jupyter Notebook"),
    9000: ("PHP-FPM", "PHP FastCGI Process Manager or SonarQube"),
    9042: ("Cassandra-CQL", "Cassandra client protocol"),
    9092: ("Kafka", "Apache Kafka broker"),
    9100: ("JetDirect", "Network printer raw port"),
    9200: ("Elasticsearch", "Elasticsearch REST API"),
    9300: ("Elasticsearch-Cluster", "Elasticsearch inter-node communication"),
    9418: ("Git", "Git protocol daemon"),
    9999: ("Alt-Service", "Common alternate service port"),
    10000: ("Webmin", "Webmin system administration"),
    11211: ("Memcached", "Memcached in-memory cache"),
    15672: ("RabbitMQ", "RabbitMQ management console"),
    27017: ("MongoDB", "MongoDB database server"),
    27018: ("MongoDB-Shard", "MongoDB shard server"),
    28017: ("MongoDB-HTTP", "MongoDB HTTP status interface"),
    32400: ("Plex", "Plex media server"),
    49152: ("Windows-RPC", "Windows dynamic RPC range start"),
}

DEFAULT_SERVICE = "Unknown"
DEFAULT_DESCRIPTION = "No description available for this port"

COMMON_PORTS = sorted([
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
    993, 995, 1723, 3306, 3389, 5900, 8080,
])

TOP_100_PORTS = sorted(set(COMMON_PORTS + [
    7, 9, 13, 17, 19, 20, 26, 37, 49, 67, 68, 69, 70, 79, 81, 88, 100,
    106, 113, 119, 123, 137, 138, 158, 161, 179, 199, 254, 255, 264,
    280, 301, 306, 311, 340, 366, 389, 406, 407, 416, 417, 425, 427,
    444, 458, 464, 465, 481, 497, 500, 512, 513, 514, 515, 520, 521,
    540, 548, 554, 556, 563, 587, 593, 616, 617, 625, 631, 636, 646,
    648, 666, 667, 668, 683, 687, 691, 700, 705, 711, 714, 720, 722,
    726, 749, 765, 777, 783, 787, 800, 801, 808, 843, 873, 880, 888,
    898, 900, 901, 902, 903, 911, 912,
]))

TOP_1000_PORTS = list(range(1, 1001))


def get_port_list(mode, start=None, end=None):
    if mode == "Common Ports":
        return list(COMMON_PORTS)
    if mode == "Top 100":
        return list(TOP_100_PORTS)
    if mode == "Top 1000":
        return list(TOP_1000_PORTS)
    if mode == "Custom Range":
        return list(range(start, end + 1))
    return list(COMMON_PORTS)


def is_valid_ip(value):
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def is_valid_hostname(value):
    if not value or len(value) > 253:
        return False
    return bool(HOSTNAME_PATTERN.match(value))


def validate_target(target):
    target = target.strip()
    if not target:
        return False, "Target cannot be empty"
    if is_valid_ip(target) or is_valid_hostname(target):
        return True, ""
    return False, "Invalid IP address or hostname format"


def resolve_host(target):
    target = target.strip()
    if is_valid_ip(target):
        return target
    try:
        return socket.gethostbyname(target)
    except socket.gaierror:
        raise ValueError(f"Could not resolve hostname: {target}")


def validate_port_range(start_text, end_text):
    try:
        start = int(start_text)
        end = int(end_text)
    except (TypeError, ValueError):
        return False, "Port values must be numeric", None, None

    if start < 1 or start > 65535 or end < 1 or end > 65535:
        return False, "Ports must be between 1 and 65535", None, None

    if start > end:
        return False, "Start port must be less than or equal to end port", None, None

    return True, "", start, end


def get_service_info(port):
    if port in PORT_INFO:
        return PORT_INFO[port]

    try:
        service = socket.getservbyport(port, "tcp")
        return service.upper(), f"Registered service on port {port}"
    except OSError:
        return DEFAULT_SERVICE, DEFAULT_DESCRIPTION


def export_to_csv(filepath, results):
    open_results = [r for r in results if r.get("state") == "Open"]
    with open(filepath, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Port", "Protocol", "Service", "Status", "Description"])
        for row in open_results:
            writer.writerow([
                row.get("port", ""),
                row.get("protocol", "TCP"),
                row.get("service", ""),
                row.get("state", ""),
                row.get("description", ""),
            ])
    return len(open_results)
