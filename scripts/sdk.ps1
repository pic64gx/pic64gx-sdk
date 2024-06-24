$_SDK_BASE=Split-Path -Path $PSScriptRoot -Parent
$env:SDK_BASE=$_SDK_BASE.replace("\", "/")
$_WORKSPACE=Split-Path -Path $_SDK_BASE -Parent
$env:WORKSPACE=$_WORKSPACE.replace("\", "/")
