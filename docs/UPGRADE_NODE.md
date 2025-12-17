# Node.js Upgrade Required

## Issue
Vite requires Node.js version **20.19+** or **22.12+**, but you have **Node.js 18.19.1**.

## Solution: Install Node.js 20 using nvm

### Step 1: Install nvm (if not already installed)
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
```

### Step 2: Reload your shell
```bash
source ~/.bashrc
# Or close and reopen your terminal
```

### Step 3: Install Node.js 20
```bash
nvm install 20
nvm use 20
```

### Step 4: Verify
```bash
node --version  # Should show v20.x.x
npm --version
```

### Step 5: Run the dev server
```bash
cd /home/g/Projects/dentaltrawler/dentaltrawler
npm run dev
```

## Make Node 20 Default (Optional)
```bash
nvm alias default 20
```

This ensures Node 20 is used in new terminal sessions.

## Alternative: Use System Package Manager
If you prefer not to use nvm:
```bash
# For Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## After Upgrade
Once Node.js 20 is installed, the dev server should start successfully at:
**http://localhost:5173**

