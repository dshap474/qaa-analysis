# Git Push
git add . ; git commit -m "Your commit message" ; git push origin main

# Git Force Pull
git reset --hard origin/main ; git pull origin main

# Repomix
npx repomix C:\Users\dansh\Documents\Investing\seven7s\s7-core\src

# Generate Tree File Full -- Windows
tree /f /a > .repomix/tree.txt

# Generate Tree File Full -- Mac
tree -afi > .repomix/tree.txt

# rsync (MSYS2 UCRT64)
1) Transfer s7-db from Desktop to EC2

2) Transfer from EC2 to Local

# Service Files
sudo nano /etc/systemd/system/s7-frontend.service

# Dev Deploy Test
ssh seven7s -L 3000:localhost:3000 -L 8000:localhost:8000
http://localhost:3000/