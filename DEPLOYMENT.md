# Deployment Guide

This guide explains how to deploy the Maps Lead Scraper to a cloud platform.

## Option 1: Render (Recommended for Free Tier)
Render offers a free tier for web services and makes it easy to deploy Dockerized apps.

1.  **Push to GitHub**:
    - Initialize a git repo: `git init`
    - Add files: `git add .`
    - Commit: `git commit -m "Initial commit"`
    - Push to a new GitHub repository.

2.  **Create New Web Service on Render**:
    - Go to [dashboard.render.com](https://dashboard.render.com/).
    - Click **New +** -> **Web Service**.
    - Connect your GitHub repository.

3.  **Configure**:
    - **Name**: `maps-scraper` (or similar)
    - **Runtime**: `Docker`
    - **Region**: Choose one close to you.
    - **Instance Type**: Free (or Starter for better performance).

4.  **Environment Variables**:
    - Add the following variable:
        - `HEADLESS`: `true`
        - `PYTHONUNBUFFERED`: `1`

5.  **Deploy**:
    - Click **Create Web Service**.
    - Render will build the Docker image (this may take a few minutes as it installs Chrome).

## Option 2: Railway
Railway is another excellent option with a slightly different pricing model (trial credits).

1.  **Install Railway CLI** (optional) or use the dashboard.
2.  **Deploy from GitHub**:
    - Go to [railway.app](https://railway.app/).
    - Click **New Project** -> **Deploy from GitHub repo**.
    - Select your repository.
3.  **Variables**:
    - Go to the **Variables** tab.
    - Add `HEADLESS=true`.
4.  **Domain**:
    - Railway automatically generates a domain for you.

## Notes
- **Performance**: Scraping uses a lot of RAM. The free tiers might be slow or crash if you try to scrape too many leads at once. Keep `MAX_LEADS` low (e.g., 10-20) on free tiers.
- **Storage**: The generated CSV files are stored in the container's ephemeral file system. They will disappear if the app restarts. For persistent storage, you would need to integrate S3 or a database.
- **Blocking**: As mentioned in the app design, scraping is a blocking operation. The request might timeout on some platforms (Render has a 100s timeout on free tier) if the scrape takes too long.
