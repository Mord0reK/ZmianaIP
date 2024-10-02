rem Wyświetlenie listy dostępnych interfejsów
netsh interface show interface

pause

set /p nazwa="Podaj nazwe interfejsu: "
set /p nowy_ip="Podaj nowy adres IP: "
set /p maska="Podaj maske podsieci: "
set /p brama="Podaj brame domyslna: "

rem Zmiana adresu IP
netsh interface ipv4 set address name=%nazwa% static %nowy_ip% %maska% %brama%  

rem Sprawdzenie nowej konfiguracji
netsh interface ipv4 show config name="%nazwa%"

pause

