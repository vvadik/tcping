import struct
from tabulate import tabulate


IP_HEADERS = ['Ver', 'Head Len', 'Service fields', 'Total length',
              'ID', 'Flags', 'TTL', 'Proto', 'Checksum', 'Source ip',
              'Destination ip']
TCP_HEADERS = ['Src port', 'Dst port', 'SEQ', 'ACK', 'Flags', 'Window',
               'Checksum', 'Urgent']
ICMP_HEADERS = ['Type', 'Code', 'Checksum']


def sniff(*packages):
    for pack in packages:
        if pack is None:
            continue
        network_layout, transport_layout = _parse(pack)
        _print(pack, network_layout, transport_layout)


def _print(pack, network_layout, transport_layout):
    if network_layout:
        print(tabulate([IP_HEADERS, network_layout], tablefmt='pretty'))
        if network_layout[7] == 6:
            print(tabulate([TCP_HEADERS, transport_layout],
                           tablefmt='pretty'))
        else:
            print(tabulate([ICMP_HEADERS, transport_layout],
                           tablefmt='pretty'))
    else:
        print(tabulate([TCP_HEADERS, transport_layout], tablefmt='pretty'))

    for i in range(0, len(pack), 16):
        print(tabulate([[f'{pack[i:i + 16]} {pack[i:i + 16].hex()}']],
                       tablefmt='orgtbl'))


def _parse(pack):
    network_layout = ''
    if len(pack) < 30:
        transport_layout = _parse_tcp(pack)
    else:
        network_layout = _parse_ip(pack)
        if network_layout[7] == 6:
            transport_layout = _parse_tcp(pack[20:40])
        else:
            transport_layout = _parse_icmp(pack[20:24])
    return network_layout, transport_layout


def _parse_ip(pack):
    result = []
    values = struct.unpack('!BBHHHBBH', pack[:12])
    data = _get_version(values[0])
    result.extend(data)  # Version, header length
    result.extend(values[1:])
    result.append(_get_ip(pack, 12, 16))  # Source IP
    result.append(_get_ip(pack, 16, 20))  # Dest Ip
    return result


def _parse_tcp(pack):
    values = struct.unpack('!HHIIHHHH', pack[:20])
    result = list(values)
    result[4] = bin(result[4])
    return result


def _parse_icmp(pack):
    return struct.unpack('!BBH', pack)


def _get_version(value):
    bin_value = bin(value)
    version = int(bin_value[2:-4], 2)
    length = int(bin_value[:-4], 2) * 5
    return (version, length)


def _get_ip(pack, start, end):
    return '.'.join([str(x) for x in struct.unpack('!BBBB', pack[start:end])])
