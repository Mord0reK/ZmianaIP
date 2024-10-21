import ifaddr
import os
import psutil
import subprocess


def list_interfaces():
    adapters = ifaddr.get_adapters()
    gateways = psutil.net_if_stats()

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
        print(f"  Brama: {gateway_ip}")

        interface_list.append(adapter.nice_name)

    return interface_list


def convert_cidr_to_netmask(cidr):
    mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
    return f"{(mask >> 24) & 0xff}.{(mask >> 16) & 0xff}.{(mask >> 8) & 0xff}.{mask & 0xff}"


def get_gateway_for_interface(interface_name):
    # Wykonaj polecenie ipconfig /all i przetwórz wynik
    result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True, encoding='utf-8', errors='ignore')
    output = result.stdout

    found_interface = False
    default_gateway = None

    for line in output.splitlines():
        # Sprawdź, czy wiersz zawiera nazwę interfejsu
        if interface_name in line:
            found_interface = True
        # Gdy znajdziemy interfejs, szukamy "Default Gateway"
        elif found_interface and "Default Gateway" in line:
            parts = line.split(":")
            if len(parts) > 1 and parts[1].strip():
                default_gateway = parts[1].strip()  # Pobierz adres bramy
                break
        # Jeśli znajdziemy inny interfejs, przestajemy szukać
        elif found_interface and line == "":
            found_interface = False

    # Sprawdź, czy brama została znaleziona
    if default_gateway:
        return default_gateway
    else:
        return "Brak bramy domyślnej"


def map_interface_to_standard_name(interface):
    if "Ethernet" in interface or "Realtek" in interface or ("Intel" in interface and "Ethernet" in interface) or "LAN" in interface:
        return "Ethernet"
    elif "MHz" in interface or ("Intel" in interface and "Wi-Fi" in interface):
        return "Wi-Fi"
    else:
        return "Ethernet0"


def change_interface_params(interface, ip, netmask, gateway, dns=None):
    standardized_interface = map_interface_to_standard_name(interface)

    if ip:  # If the user provided a new IP
        command = f'netsh interface ip set address name="{standardized_interface}" static {ip} {netmask} {gateway}'
        print(f"Wykonywanie komendy: {command}")
        result = os.system(command)

        if result == 0:
            print(f"Poprawnie zaaktualizowano interfejs '{standardized_interface}' z Adresem IP {ip}, Maską {netmask}, oraz Bramą {gateway}.")
        else:
            print(f"Nie udało się zmienić parametrów interfejsu '{standardized_interface}'. Sprawdź parametry i spróbuj ponownie.")

        if dns:
            dns_command = f'netsh interface ip set dns name="{standardized_interface}" static {dns}'
            print(f"Wykonywanie komendy DNS: {dns_command}")
            dns_result = os.system(dns_command)

            if dns_result == 0:
                print(f"Poprawnie zaaktualizowano DNS dla interfejsu '{standardized_interface}' na {dns}.")
            else:
                print(f"Nie udało się zmienić serwera DNS dla interfejsu '{standardized_interface}'. Sprawdź parametr DNS i spróbuj ponownie.")
    else:  # If no IP was provided, switch to DHCP
        print(f"Ustawianie interfejsu '{standardized_interface}' na DHCP.")
        dhcp_command = f'netsh interface ip set address name="{standardized_interface}" source=dhcp'
        result = os.system(dhcp_command)

        if result == 0:
            print(f"Interfejs '{standardized_interface}' został ustawiony na pobieranie adresu IP z DHCP.")
        else:
            print(f"Nie udało się ustawić interfejsu '{standardized_interface}' na DHCP. Sprawdź parametry i spróbuj ponownie.")

        if dns:
            dns_command = f'netsh interface ip set dns name="{standardized_interface}" source=dhcp'
            print(f"Wykonywanie komendy DNS: {dns_command}")
            dns_result = os.system(dns_command)

            if dns_result == 0:
                print(f"Poprawnie zaaktualizowano DNS dla interfejsu '{standardized_interface}' na DHCP.")
            else:
                print(f"Nie udało się zmienić serwera DNS dla interfejsu '{standardized_interface}'. Sprawdź parametr DNS i spróbuj ponownie.")


def release_and_renew_ip():
    # Ustaw wszystkie interfejsy na DHCP
    interface_list = list_interfaces()  # Zaktualizuj dane interfejsów
    for interface in interface_list:
        dhcp(interface)  # Ustaw każdy interfejs na DHCP

    print("Wykonywanie komendy: ipconfig /release")
    os.system('ipconfig /release')
    print("Wykonywanie komendy: ipconfig /renew")
    os.system('ipconfig /renew')



def display_arp_table():
    print("Wykonywanie komendy: arp -a")
    os.system('arp -a')
    os.system('pause')

def dhcp(interface):
    standardized_interface = map_interface_to_standard_name(interface)
    dhcp_command = f'netsh interface ip set address name="{standardized_interface}" source=dhcp'
    result = os.system(dhcp_command)

    if result == 0:
        print(f"Interfejs '{standardized_interface}' został ustawiony na pobieranie adresu IP z DHCP.")
    elif result == "DHCP is already enabled on this interface.".upper():
        print(f"Interfejs '{standardized_interface}' jest już skonfigurowany na DHCP.")
    else:
        print(f"Nie udało się ustawić interfejsu '{standardized_interface}' na DHCP. Sprawdź parametry i spróbuj ponownie.")

    dns_command = f'netsh interface ip set dns name="{standardized_interface}" source=dhcp'
    print(f"Wykonywanie komendy DNS: {dns_command}")
    dns_result = os.system(dns_command)

    if dns_result == 0:
        print(f"Poprawnie zaaktualizowano DNS dla interfejsu '{standardized_interface}' na DHCP.")
    else:
        print(f"Nie udało się zmienić serwera DNS dla interfejsu '{standardized_interface}'. Sprawdź parametr DNS i spróbuj ponownie.")

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
    clear_console()  # Opcjonalnie, czyść konsolę na początku
    try:
        while True:
            clear_console()  # Czyści konsolę przed wyświetleniem menu
            interface_list = list_interfaces()  # Zaktualizuj dane interfejsów

            if not interface_list:
                print("Nie znaleziono żadnych interfejsów.")
                exit(1)

            # Menu dla użytkownika
            print("\nWybierz opcje:")
            print("1) Zmiana parametrów kart sieciowych")
            print("2) Wyświetlanie parametrów kart sieciowych")
            print("3) Ipconfig /release & /renew")
            print("4) arp -a")
            print("5) Koniec")
            action_choice = input("Opcja: ").strip()

            if action_choice == '1':
                # Input and validation for changing interface parameters
                try:
                    interface_idx = int(input("Wprowadź numer interfejsu, który chcesz zmienić: ")) - 1
                    if interface_idx < 0 or interface_idx >= len(interface_list):
                        raise IndexError("Wybrano niepoprawny interfejs.")
                except ValueError as e:
                    print(f"Błąd: {e}. Wprowadź prawidłowy numer interfejsu (liczba).")
                    continue

                interface = interface_list[interface_idx]
                ip = input("Wprowadź nowe IP (zostaw puste, aby ustawić DHCP): ").strip()
                if not ip:
                    dhcp(interface)
                    continue  # Zmień 'break' na 'continue' tutaj, aby wrócić do menu
                netmask = input("Wprowadź nową Maskę Podsieci: ").strip()
                gateway = input("Wprowadź nową Bramę: ").strip()
                dns = input("Wprowadź nowy DNS (Zostaw puste, jeżeli nie zmieniasz): ").strip()

                # Apply the changes
                change_interface_params(interface, ip if ip else None, netmask, gateway, dns if dns else None)

            elif action_choice == '2':
                # Display interface parameters
                list_interfaces()

            elif action_choice == '3':
                # Execute the release and renew commands
                release_and_renew_ip()

            elif action_choice == '4':
                # Display ARP table
                display_arp_table()

            elif action_choice == '5':
                print("Jurecki Babka.")
                break

            else:
                print("Niepoprawny wybór. Proszę wprowadzić numer opcji od 1 do 5.")

    except KeyboardInterrupt:
        print("\nOperacja anulowana przez użytkownika.")
    except IndexError as e:
        print(f"Błąd: {e}. Nieprawidłowy wybór interfejsu. Spróbuj ponownie.")
    except ValueError as e:
        print(f"Błąd: {e}. Wprowadź poprawne wartości.")

