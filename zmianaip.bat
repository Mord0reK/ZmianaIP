@echo off
setlocal enabledelayedexpansion

:show_interfaces
echo Listing all network interfaces...
echo ---------------------------------
ipconfig | findstr /R /C:"Adapter" /C:"IPv4" /C:"Subnet" /C:"Default Gateway"
echo.

:choose_option
echo ---------------------------------
echo Do you want to change the IP configuration?
echo 1. Set Static IP
echo 2. Set DHCP
echo 3. Exit
set /p option=Choose an option (1-3):

if "%option%"=="1" goto static_ip
if "%option%"=="2" goto dhcp
if "%option%"=="3" goto end
echo Invalid option. Please try again.
goto choose_option

:static_ip
set /p interface=Enter the interface name:
set /p ipaddr=Enter the new static IP address:
set /p mask=Enter the subnet mask:
set /p gateway=Enter the gateway:
echo Setting Static IP...
netsh interface ipv4 set address name="%interface%" static %ipaddr% %mask% %gateway%
echo IP configuration has been updated.
goto end

:dhcp
set /p interface=Enter the interface name:
echo Switching to DHCP...
netsh interface ipv4 set address name="%interface%" source=dhcp
echo IP configuration has been updated to DHCP.
goto end

:end
echo Exiting program...
exit /b
