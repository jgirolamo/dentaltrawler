# Installing Homebrew

Homebrew requires administrator privileges and user interaction, so it needs to be installed manually in your terminal.

## Installation Steps

1. **Open your terminal** (Terminal.app or iTerm2)

2. **Run the Homebrew installation command:**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

3. **Follow the prompts:**
   - You'll be asked for your password (for sudo access)
   - The installation will take a few minutes
   - You may see instructions to add Homebrew to your PATH

4. **After installation, add Homebrew to your PATH** (if prompted):
   ```bash
   echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
   eval "$(/opt/homebrew/bin/brew shellenv)"
   ```

5. **Verify installation:**
   ```bash
   brew --version
   ```

## After Installing Homebrew

Once Homebrew is installed, you can install Node.js:

```bash
brew install node
```

Then verify Node.js is installed:
```bash
node --version
npm --version
```

## Then Test the App Locally

After Node.js is installed, you can test the app:

```bash
cd /Users/g/Projects/dentaltrawler/dentaltrawler
npm install
npm run dev
```

The app will be available at `http://localhost:5173`

