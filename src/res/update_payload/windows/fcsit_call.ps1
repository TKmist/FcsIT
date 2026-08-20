# Copyright (C) 2026 TKmist (https://github.com/TKmist)
#
# This file is part of the FcsIT repository.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.
<# Send one FcsIT TCP/JSON command from a Windows command line. #>

param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Command,

    [Parameter(Position = 1)]
    [string]$Arguments = '{}'
)

$ErrorActionPreference = 'Stop'
$ServerHost = if ($env:FCSIT_TCP_HOST) { $env:FCSIT_TCP_HOST } else { '127.0.0.1' }
$ServerPort = if ($env:FCSIT_TCP_PORT) { [int]$env:FCSIT_TCP_PORT } else { 8765 }

try {
    $ParsedArguments = $Arguments | ConvertFrom-Json
} catch {
    Write-Error 'Arguments must be a valid JSON object.'
    exit 2
}

if ($null -eq $ParsedArguments -or
    $ParsedArguments -is [System.Array] -or
    $ParsedArguments -is [string] -or
    $ParsedArguments -is [ValueType]) {
    Write-Error 'Arguments must be a valid JSON object.'
    exit 2
}

$Request = [ordered]@{
    protocol = 'fcsit-tcp-json'
    version = '1.0'
    id = 'cli-' + [Guid]::NewGuid().ToString('N')
    command = $Command
    arguments = $ParsedArguments
}
if ($env:FCSIT_TCP_TOKEN) {
    $Request['token'] = $env:FCSIT_TCP_TOKEN
}

$Client = $null
$Writer = $null
$Reader = $null
try {
    $Client = [System.Net.Sockets.TcpClient]::new()
    $Client.Connect($ServerHost, $ServerPort)
    $Stream = $Client.GetStream()
    $Encoding = [System.Text.UTF8Encoding]::new($false)
    $Writer = [System.IO.StreamWriter]::new($Stream, $Encoding, 4096, $true)
    $Reader = [System.IO.StreamReader]::new($Stream, $Encoding, $false, 4096, $true)
    $Writer.WriteLine(($Request | ConvertTo-Json -Compress -Depth 20))
    $Writer.Flush()
    $Response = $Reader.ReadLine()
    if ($null -eq $Response) {
        throw 'FcsIT closed the connection without a response.'
    }
    $Response | ConvertFrom-Json | ConvertTo-Json -Depth 20
} catch {
    Write-Error "FcsIT TCP request failed: $($_.Exception.Message)"
    exit 1
} finally {
    if ($null -ne $Reader) { $Reader.Dispose() }
    if ($null -ne $Writer) { $Writer.Dispose() }
    if ($null -ne $Client) { $Client.Dispose() }
}
