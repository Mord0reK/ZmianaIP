import psutil
import subprocess
import platform


def get_network_interfaces():
    interfaces = psutil.net_if_addrs()
    for iface_name, iface_addresses in interfaces.items():
        print(f"\nInterfejs: {iface_name}")
        for addr in iface_addresses:
            print(f"  Typ: {addr.family}, Adres: {addr.address}, Maska: {addr.netmask}")


def set_network_configuration(interface, ip, mask, gateway, dns):
    # Zmiana adresu IP i maski
    if platform.system() == "Windows":
        subprocess.run(["netsh", "interface", "ip", "set", "address", f"name={interface}", "static", ip, mask, gateway])
        subprocess.run(["netsh", "interface", "ip", "set", "dns", f"name={interface}", "static", dns])
    elif platform.system() == "Linux":
        subprocess.run(["ip", "addr", "add", f"{ip}/{mask}", "dev", interface])
        subprocess.run(["ip", "route", "add", gateway, "dev", interface])
        subprocess.run(["echo", dns, ">>", "/etc/resolv.conf"])
    else:
        print("Nie obsługiwany system operacyjny.")


def main():
    get_network_interfaces()

    interface = input("Podaj nazwę interfejsu do zmiany: ")
    ip = input("Podaj nowy adres IP: ")
    mask = input("Podaj nową maskę: ")
    gateway = input("Podaj nową bramę: ")
    dns = input("Podaj adres nowego serwera DNS: ")

    set_network_configuration(interface, ip, mask, gateway, dns)
    print("Konfiguracja sieci została zaktualizowana.")


if __name__ == "__main__":
    main()
