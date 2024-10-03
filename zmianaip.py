import psutil
import subprocess

def list_interfaces():
    interfaces = psutil.net_if_addrs()
    for interface, addrs in interfaces.items():
        print(f"Interface: {interface}")
        for addr in addrs:
            print(f"  Address: {addr.address}")
            print(f"  Netmask: {addr.netmask}")
            print(f"  Broadcast: {addr.broadcast}")
        print()

def change_ip(interface, new_ip, netmask):
    try:
        subprocess.run(["netsh", "interface", "ip", "set", "address", interface, "static", new_ip, netmask], check=True)
        print(f"IP address of {interface} changed to {new_ip} with netmask {netmask}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to change IP address: {e}")

if __name__ == "__main__":
    print("Available network interfaces and their default information:")
    list_interfaces()

    interface = input("Enter the interface you want to change the IP for: ")
    new_ip = input("Enter the new IP address: ")
    netmask = input("Enter the netmask: ")

    change_ip(interface, new_ip, netmask)