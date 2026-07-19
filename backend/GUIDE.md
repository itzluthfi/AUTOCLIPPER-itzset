# 📖 YT-Short-Clipper User Guide

Complete guide for using YT-Short-Clipper for beginners.

---

## 📑 Table of Contents

- [1. Download & Installation](#1-download--installation)
  - [1.1 Download from GitHub](#11-download-from-github)
  - [1.2 Extract and Run](#12-extract-and-run)
- [2. Setup Library (yt-dlp, FFmpeg & Deno)](#2-setup-library-yt-dlp-ffmpeg--deno)
- [3. Setup YouTube Cookies](#3-setup-youtube-cookies)
  - [3.1 Install Browser Extension](#31-install-browser-extension)
  - [3.2 Export Cookies](#32-export-cookies)
  - [3.3 Upload Cookies to App](#33-upload-cookies-to-app)
- [4. Create API Key on YT Clip AI (Recommended)](#4-create-api-key-on-yt-clip-ai-recommended)
  - [4.1 Login with Google](#41-login-with-google)
  - [4.2 Top Up Balance](#42-top-up-balance)
  - [4.3 Create API Key](#43-create-api-key)
- [5. AI API Configuration](#5-ai-api-configuration)
  - [5.1 Open AI API Settings](#51-open-ai-api-settings)
  - [5.2 Select AI Module](#52-select-ai-module)
  - [5.3 Select AI Provider](#53-select-ai-provider)
  - [5.4 Enter API Key & Load Models](#54-enter-api-key--load-models)
  - [5.5 Validate & Save](#55-validate--save)
- [6. Start Using the App](#6-start-using-the-app)

---

## 1. Download & Installation

### 1.1 Download from GitHub

1. Go to the YT-Short-Clipper GitHub page
2. Click **"Releases"** in the right sidebar

   ![GitHub Releases](assets/docs/01.github-releases.png)

3. On the Releases page, find the `.exe` file and click to download

   ![Download EXE](assets/docs/02.exe-link-download.png)

### 1.2 Run the Application

1. After download completes, double-click the `.exe` file to run the application
2. If Windows Defender warning appears, click **"More info"** → **"Run anyway"**

---

## 2. Setup Library (yt-dlp, FFmpeg & Deno)

The app requires additional libraries for downloading and processing videos.

1. When first opening the app, click the **"Library"** button in the top right corner

   ![Library Button](assets/docs/03.library-button.png)

2. Click the **"Download"** button to download the required libraries

   ![Download Library](assets/docs/04.download-library.png)

3. Wait for the download process to complete

   ![Download Process](assets/docs/05.download-process.png)

4. Once finished, the status will change to ✅ **Installed**
5. **Restart the app** after all libraries are installed

---

## 3. Setup YouTube Cookies

Cookies are required so the app can access YouTube videos on your behalf.

### 3.1 Install Browser Extension

1. Open Chrome/Edge browser
2. Install the **"Get cookies.txt LOCALLY"** extension:
   - [Download for Chrome/Edge](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)

### 3.2 Export Cookies

1. Go to [youtube.com](https://youtube.com) and **make sure you're logged in**
2. Click the extension icon in the browser toolbar

   ![Get Cookies Locally](assets/docs/06.get-cookies-locally.png)

3. Click **"Export"** to save the cookies

   ![Export Text](assets/docs/07.export-text.png)

4. Save the file as `cookies.txt`

### 3.3 Upload Cookies to App

1. On the app's main page, click the **"Upload Cookies"** button

   ![Upload Cookies](assets/docs/08.upload-cookies.png)

2. Select the `cookies.txt` file you exported
3. The cookies status will change to ✅ **Valid**

> **⚠️ Important:** 
> - YouTube cookies typically expire within 1-2 weeks
> - If you see authentication errors, re-export cookies from your browser
> - Never share your cookies.txt file with anyone

---

## 4. Create API Key on YT Clip AI (Recommended)

**YT Clip AI** is the recommended AI provider because it's more affordable and optimized for this app.

### 4.1 Login with Google

1. Go to [https://ai.ytclip.org](https://ai.ytclip.org)
2. Click **"Login with Google"** and select your Google account

   ![YT Clip AI Login](assets/docs/15.ytclip-ai-login-google.png)

### 4.2 Top Up Balance

1. After login, click the **"Top Up"** button to add balance

   ![Top Up Balance](assets/docs/16.ytclip-ai-topup-balance.png)

2. Enter the top up amount (in USD), you'll see the conversion to IDR

   ![Input Top Up Amount](assets/docs/17.ytclip-ai-input-topup-amount-and-calculation-to-idr.png)

3. Pay using **QRIS**

   ![Pay with QRIS](assets/docs/18.ytclip-ai-pay-qris.png)

4. After payment is successful, your USD balance will be added in realtime

### 4.3 Create API Key

1. After balance is added, click the **"Create Key"** button

   ![Create Key Button](assets/docs/19.ytclip-ai-create-key.png)

2. Enter a name for your API Key, then click **"Create"**

   ![Create API Key Modal](assets/docs/20.ytclip-ai-create-api-key-modal.png)

3. **Copy the Secret Key** that appears and save it somewhere safe

   ![Copy Secret Key](assets/docs/21.ytclip-ai-copy-secret-key.png)

> **⚠️ Important:** The Secret Key is only shown once! Make sure to copy it before closing the dialog.

After getting your API Key, continue to [AI API Configuration](#5-ai-api-configuration) to enter the key into the app.

---

## 5. AI API Configuration

The app requires an API Key to access AI services (GPT, Whisper, TTS).

### 5.1 Open AI API Settings

1. Click the **Settings** button (⚙️) in the top right corner
2. Select **"AI API Settings"**

   ![AI API Settings](assets/docs/09.ai-api-settings.png)

### 5.2 Select AI Module

The app has several AI modules that can be configured separately:

   ![AI Setting Modules](assets/docs/10.ai-setting-modules.png)

- **Highlight Finder** - Finds interesting moments from videos
- **Caption Maker** - Creates captions/subtitles
- **Hook Maker** - Creates hook text for intros
- **Title Generator** - Generates SEO titles & descriptions

### 5.3 Select AI Provider

1. Click the **"AI Provider"** dropdown
2. Select the provider you have an API key for:
   - **YT CLIP AI** - [https://ai.ytclip.org](https://ai.ytclip.org)
   - **OpenAI** - [https://platform.openai.com](https://platform.openai.com)
   - **Custom** - Use other providers

   ![AI Provider Selector](assets/docs/11.ai-provider-selector.png)

3. The URL will auto-fill based on the selected provider

### 5.4 Enter API Key & Load Models

1. Paste your **API Key** in the provided field
2. Click the **"Load Models"** button to fetch the model list

   ![Load Model Button](assets/docs/12.load-model-button.png)

3. Select the model you want to use from the dropdown

   ![Select Models](assets/docs/13.select-models.png)

### 5.5 Validate & Save

1. Click the **"Validate"** button to ensure the configuration is correct
2. If valid, click **"Save"** to save the settings

   ![Validate Configuration and Save](assets/docs/14.validate-configuration-and-save.png)

> **💡 Tip:** Repeat steps 5.2 - 5.5 for each AI module you want to configure.

---

## 6. Start Using the App

After all setup is complete, you can start using the app:

1. **Paste the YouTube URL** you want to process
2. **Set the number of clips** you want
3. **Click "Start Processing"** and wait for results

The resulting clips will be saved in the `output/` folder inside the app folder.

---

## ❓ Need Help?

- 🔑 [Get AI API Key here](https://ai.ytclip.org)
- 💬 Join [Discord Community](https://s.id/ytsdiscord) for Q&A, bug reports, and discussions with other users
