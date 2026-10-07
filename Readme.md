# GitRank — Top GitHub Repositories Directory & Monetization Platform

GitRank is a high-performance, developer-focused leaderboard and search platform indexing the world's most influential and trending open-source GitHub repositories.

## 🚀 Key Features
- **Curated Multi-Category Ranking**: Repos categorized across AI/ML, Trending & Hot, Web Development, DevOps & Cloud, Cyber Security, Mobile, Systems, Databases, and Open Source Alternatives.
- **Fast Search & Multi-Filter**: Real-time keyword filtering, language selector, star threshold filter, and sorting by Stars, Velocity, Forks, or Name.
- **Direct Clickable GitHub Links**: Every repository card and row directly links to its official GitHub repository and live documentation/demo.
- **Built-in Monetization Architecture**:
  - Sponsored Repo Placements (Spotlight, Growth, and Partner tiers).
  - Weekly Developer Newsletter Signup with CSV subscriber export.
  - Developer Tool Affiliate slots & Cloud Perks.
  - Self-serve sponsor application modal.

## 🌐 Instant Free Hosting
You can deploy GitRank for free in under 2 minutes:
1. **GitHub Pages**:
   - Create a new repository on GitHub (e.g., `gitrank`).
   - Push `index.html`, `styles.css`, and `script.js`.
   - Go to **Settings > Pages > Branch: main / root > Save**.
   - Your site is immediately live at `https://<username>.github.io/<repo>/`.
2. **Vercel**:
   - Connect your GitHub repository to Vercel.
   - Click **Deploy**. Vercel provides instant global edge CDN and free custom domain SSL.
3. **Cloudflare Pages / Netlify**:
   - Import your Git repository and deploy static files with zero configuration.

## 🔄 Automated Daily Star Updates
Use the included `update_repos.py` script with a GitHub Actions cron workflow (`.github/workflows/update-stars.yml`) to refresh star counts, weekly velocity, and rankings automatically every night.
