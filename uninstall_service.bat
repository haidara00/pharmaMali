@echo off
echo Uninstalling PharmaGestion Service...
nssm stop PharmaGestion
nssm remove PharmaGestion confirm
echo ✅ PharmaGestion service removed!
pause