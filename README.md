# Manuscrit

build18 2025 repo for Manuscrit. Created by Bryan Hong, Aaron Tang, Jonathan Waller, and Barbara Zhuo.

SITE IS LIVE ON https://manuscrit-gk3qwxg9u-aaronbiscottis-projects.vercel.app/

To clone:
git clone <URL>

To push:
git add -A
git commit -m "YOUR CHANGES"
git push

To pull:
git pull

TO CHECK PENDING G-CODE:
`curl https://manuscrit-production.up.railway.app/pending-gcode`

You'll get something like `{"files":["drawing_20250119_022451.nc","drawing_20250119_090554.nc"]}`

Use this in PowerShell to get the file from the Railway server and save it into client_backend\gcode locally:
`Invoke-WebRequest -Uri "https://manuscrit-production.up.railway.app/download-gcode/drawing_20250119_022451.nc" -OutFile "client_backend\gcode\drawing_20250119_022451.nc"`

Then run `python ".\Python Serial Code\serial_gcode_final.py" "client_backend\gcode\drawing_20250119_022451.nc"`

OR

Just run `python .\local_auto_exe.py`
