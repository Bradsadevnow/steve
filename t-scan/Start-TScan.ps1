param([string]$LMStudioUrl='http://192.168.1.128:1234',[string]$Model='google/gemma-4-e4b')
$ErrorActionPreference='Stop'
$taskRoot=$PSScriptRoot
$taskPython=Join-Path $taskRoot '.venv/Scripts/python.exe'
if(-not(Test-Path -LiteralPath $taskPython)){throw 'Missing environment. See LIVE_VIEWER.md.'}
$taskArgs=@((Join-Path $taskRoot 'live/bridge.py'),'--lm-url',$LMStudioUrl,'--model',$Model)
& $taskPython @taskArgs
