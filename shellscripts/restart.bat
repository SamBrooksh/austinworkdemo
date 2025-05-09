@echo off
IF EXIST "demo.db" (
    del "demo.db"
    echo Delete database
)

call shellscripts\buildtable.bat

call python3 ./base.py