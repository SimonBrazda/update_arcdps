$status = bw status
if ($status -like '*unauthenticated*') {
    Write-Output "Unauthenticated user. Plese log in."
    bw login simon.brazda@protonmail.com --raw | Out-Null
}
Write-Output "bw get password `"Guild Wars 2`" | clip"
bw get password "Guild Wars 2" | clip
Write-Output "Password copied to clipboard"
# bw logout
# Write-Output "User logedout"
Write-Output "Erasing cliboard in 15 seconds..."
Start-Sleep -s 15
if(Write-Output $null | clip) {
    Write-Output "Cliboard has been secessfully erased"
    Write-Output "Closing in 5 seconds"
    Exit
}
Write-Output "Could not erase contents of your clipboard. Please erase it manually by typing in `"Write-Output $null | clip`""

