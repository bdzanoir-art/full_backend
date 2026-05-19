@echo off
echo Starting React Frontend Server...
cd /d D:\projects\Full_project
set NODE_OPTIONS=--max-old-space-size=8192
npm run dev -- --force
