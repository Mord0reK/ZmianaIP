@echo off

net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Ten skrypt musi byc uruchomiony jako administrator.
    pause
    exit /b
)

rem Wyświetlenie szczegółów konfiguracji wszystkich interfejsów
netsh interface ipv4 show config

pause

set /p nazwa="Podaj nazwe interfejsu: "
set /p tryb="Czy chcesz ustawic statyczny adres IP (s) czy przywrocic ustawienia DHCP (d)? [s/d]: "

if /i "%tryb%"=="s" (
    :input_loop
    set /p nowy_ip="Podaj nowy adres IP: "
    set /p maska="Podaj maske podsieci: "
    set /p brama="Podaj brame domyslna: "

    rem Sprawdzenie, czy adres IP i brama domyslna sa rozne
    if "%nowy_ip%"=="%brama%" (
        echo Adres IP i brama domyslna nie moga byc takie same.
        goto input_loop
    )

    rem Zmiana adresu IP na statyczny
    netsh interface ipv4 set address name=%nazwa% static %nowy_ip% %maska% %brama%  
) else if /i "%tryb%"=="d" (
    rem Przywrócenie ustawień DHCP
    netsh interface ipv4 set address name=%nazwa% source=dhcp
    netsh interface ipv4 set dns name=%nazwa% source=dhcp
) else (
    echo Nieprawidlowy wybor.
    exit /b
)

rem Sprawdzenie nowej konfiguracji
netsh interface ipv4 show config name=%nazwa%

pause