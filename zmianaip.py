import ifaddr
import os
import psutil


def list_interfaces():
    adapters = ifaddr.get_adapters()
    gateways = psutil.net_if_stats()

    # Get default gateways from psutil
    default_gateways = psutil.net_if_addrs()

    interface_list = []
    interface_count = 0  # To ensure continuous numbering

    print("Dostępne interfejsy sieciowe:")
    for adapter in adapters:
        # Filter out loopback, VMware, VirtualBox, and other irrelevant adapters
        if "Loopback" in adapter.nice_name or "VMware" in adapter.nice_name or "Bluetooth" in adapter.nice_name or "VirtualBox" in adapter.nice_name or "Microsoft" in adapter.nice_name:
            continue

        # Increment the interface counter only for meaningful interfaces
        interface_count += 1
        print(f"{interface_count}. {adapter.nice_name}")

        # Display IP address and netmask
        for ip in adapter.ips:
            if isinstance(ip.ip, tuple):  # Skip IPv6
                continue
            netmask = convert_cidr_to_netmask(ip.network_prefix)
            print(f"  Adres IP: {ip.ip}")
            print(f"  Maska Podsieci: {netmask}")
            if adapter.nice_name in gateways and gateways[adapter.nice_name].isup:
                print(f"  Status: UP")

        # Display gateway for the interface if available
        gateway_ip = get_gateway_for_interface(adapter.nice_name)
        if gateway_ip:
            print(f"  Gateway: {gateway_ip}")

        interface_list.append(adapter.nice_name)

    return interface_list


def convert_cidr_to_netmask(cidr):
    mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
    return f"{(mask >> 24) & 0xff}.{(mask >> 16) & 0xff}.{(mask >> 8) & 0xff}.{mask & 0xff}"


def get_gateway_for_interface(interface_name):
    # Get gateway using ipconfig /all and extract "Default Gateway"
    output = os.popen('ipconfig /all').read()
    found_interface = False
    default_gateway = None

    for line in output.splitlines():
        if interface_name in line:
            found_interface = True
        elif found_interface and "Default Gateway" in line:
            parts = line.split(":")
            if len(parts) > 1 and parts[1].strip():
                default_gateway = parts[1].strip()
                break
    return default_gateway


def map_interface_to_standard_name(interface):
    if "Ethernet" in interface or "Realtek" in interface or ("Intel" in interface and "Ethernet" in interface) or "LAN" in interface:
        return "Ethernet"
    elif "MHz" in interface or ("Intel" in interface and "Wi-Fi" in interface):
        return "Wi-Fi"
    else:
        return "Ethernet0"


def change_interface_params(interface, ip, netmask, gateway, dns=None):
    # Map interface name to standardized name like "Ethernet" or "Wi-Fi"
    standardized_interface = map_interface_to_standard_name(interface)

    # Run the netsh command to set the static IP
    command = f'netsh interface ip set address name="{standardized_interface}" static {ip} {netmask} {gateway}'
    print(f"Wykonywanie komendy: {command}")
    result = os.system(command)

    # Check if the command was successful
    if result == 0:
        print(f"Poprawnie zaaktualizowano interfejs '{standardized_interface}' z Adresem IP {ip}, Maską {netmask}, oraz Bramą {gateway}.")
    else:
        print(f"Nie udało się zmienić parametrów interfejsu '{standardized_interface}'. Sprawdź parametry i spróbuj ponownie.")

    # Set DNS if provided
    if dns:
        dns_command = f'netsh interface ip set dns name="{standardized_interface}" static {dns}'
        print(f"Wykonywanie komendy DNS: {dns_command}")
        dns_result = os.system(dns_command)

        if dns_result == 0:
            print(f"Poprawnie zaaktualizowano DNS dla interfejsu '{standardized_interface}' na {dns}.")
        else:
            print(f"Nie udało się zmienić serwera DNS dla interfejsu '{standardized_interface}'. Sprawdź parametr DNS i spróbuj ponownie.")


if __name__ == "__main__":
    try:
        interface_list = list_interfaces()

        if not interface_list:
            print("Nie znaleziono zadnych interfejsów.")
            exit(1)

        # Input and validation
        interface_idx = int(input("Wprowadź numer interfejsu, który chcesz zmienić: ")) - 1
        if interface_idx < 0 or interface_idx >= len(interface_list):
            raise IndexError("Wybrano niepoprawny interfejs.")
        elif interface_idx == -1:
            print("Zakończono program.")
            exit(0)

        interface = interface_list[interface_idx]
        ip = input("Wprowadź nowy adres IP: ")
        netmask = input("Wprowadź nową Maskę Podsieci: ")
        gateway = input("Wprowadź nowy adres bramy: ")
        dns = input("Wprowadź nowy adres serwera DNS (Zostaw puste, jezeli nie zmieniasz): ")

        # Apply the changes
        change_interface_params(interface, ip, netmask, gateway, dns if dns else None)

    except KeyboardInterrupt:
        print("\nOperacja anulowana przez uzytkownika.")
    except (IndexError, ValueError):
        print("\nInvalid input. Please enter a valid number or parameter.")
