@echo off
echo Initializing Git repository...
git init
git config user.name "DoganAI"
git config user.email "doganai@example.com"

echo Adding files to Git...
git add .

echo Creating initial commit...
git commit -m "Initial commit: Set up FastAPI project structure with authentication"

echo Adding remote repository...
git remote add origin https://github.com/Dohanhub/DoganAI-Compliance-Kit.git

echo Pushing to remote repository...
git branch -M main
git push -u origin main

echo Done!
