@echo off

set /p nazwa="Podaj nazwe interfejsu: "
set /p nowy_ip="Podaj nowy adres IP: "
set /p maska="Podaj maske podsieci: "
set /p brama="Podaj brame domyslna: "

rem Zmiana adresu IP
netsh interface ipv4 set address name=%nazwa% static %nowy_ip% %maska% %brama%  

rem Sprawdzenie nowej konfiguracji
netsh interface ip show config name="%interface_name%"

pause