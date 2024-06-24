@echo off

set orig_cwd=%cd%
set script_path=%~dp0

cd /d %script_path%..\
set SDK_BASE=%cd%
set SDK_BASE=%SDK_BASE:\=/%

cd /d ..\
set WORKSPACE=%cd%
set WORKSPACE=%WORKSPACE:\=/%

cd /d %orig_cwd%
