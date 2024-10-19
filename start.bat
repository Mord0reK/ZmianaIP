@echo off

pip install ifaddr
pip install psutil

cls

python %~dp0\zmianaip.py

pause