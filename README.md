# Onu Ventures — website

Static marketing site for Onu Ventures, Inc., implemented from the Claude Design
canvases in a Claude Design project.

## What's here

```
*.html                The five pages
assets/css/site.css   Styles (design tokens + components)
assets/js/site.js     Header scroll state, mobile menu, stat counters,
                      contact form, project-overview modal
assets/               Logos
web/                  Project renderings + responsive derivatives
api/contact.js        Serverless contact-form handler (Resend)
vercel.json           Cache headers for static assets
package.json          Declares ESM so api/contact.js runs as a module
```

The site is plain HTML/CSS/JS with no build step — deploy the repository root as-is.

## Pages

| File | Page |
| --- | --- |
| `index.html` | Home — hero, stats, capabilities, featured projects, press, investors, contact |
| `about.html` | About — story, stats, leadership, values |
| `approach.html` | Our Approach — data-driven thesis, capabilities, 7-step lifecycle, impact |
| `portfolio.html` | Portfolio — all nine projects, project-overview modals, The Adaline in focus |
| `news.html` | News — press coverage |

All five come from the canvases in the same Claude Design project. The contact
form lives on the home page; interior pages link to `index.html#contact`.

## Renderings

`web/` holds the renderings supplied for the site, in WebP, each with 640px and
1280px derivatives served through `srcset`. Every file below is used on at least
one page except the four marked *spare*, which are alternate views kept for
future use.

| File | Subject | Used on |
| --- | --- | --- |
| `hero.webp` | Trailblazer Village aerial | Home hero, About hero |
| `adaline-featured.webp` | The Adaline, street level | Portfolio hero, cards, bands |
| `trailblazer.webp` | Trailblazer Village courtyard at dusk | Approach hero, cards |
| `miss-eddies.webp` | Miss Eddie's Market & Café, interior | Cards, News band |
| `nosta.webp` | NOSTA House, lobby bar | Portfolio |
| `new-life-farms.webp` | New Life Farms, farmhouse and vineyard | Approach, Portfolio |
| `sunny-meadow.webp` | Sunny Meadow, aerial | Approach, Portfolio |
| `concord.webp` | Concord townhomes, Beaumont | Portfolio |
| `colonial.webp` | 5300 Colonial townhomes | Portfolio |
| `whitney-oak.webp` | Whitney Oak townhomes | Portfolio |
| `townhomes-retail-aerial.webp` | Trailblazer Village, closer aerial | Home |
| `portrait.jpg` | Mikial Onu | About |
| `adaline-aerial.webp` | The Adaline, aerial | *spare* |
| `miss-eddies-exterior.webp` | Miss Eddie's, exterior and BKYD | *spare* |
| `nosta-lounge.webp` | NOSTA House, lounge | *spare* |
| `edison-arts.webp` | Edison Cultural Arts Center | *spare* |
| `lakeside-homes.webp` | Lakeside homes and trail | *spare* |
| `townhome-courtyard.webp` | Townhome courtyard | *spare* |

Each rendering was matched to its project by comparing against the design
project's own image for that slot, not by guessing from the filename.

## Contact form

The form on the home page POSTs JSON to `/api/contact`, which relays it to the
team through [Resend](https://resend.com).

1. Deploy `api/contact.js` as a serverless function (on Vercel it works at this
   path as-is).
2. Set `RESEND_API_KEY` in the hosting dashboard. Do **not** commit the key —
   `.env.example` lists the variable with an empty value.
3. Verify the sending domain `onuventuresinc.com` in Resend (SPF + DKIM) so mail
   from `updates@onuventuresinc.com` is accepted. Delivery fails until it is.

Mail goes to info@, kvillanueva@ and mo@onuventuresinc.com, with the sender set
as Reply-To. The handler validates name, email, company, inquiry type and message
server-side, and caps the message at 5,000 characters.

> The Resend key referenced by the original design project was shared in chat and
> should be treated as compromised: rotate it in the Resend dashboard and store
> the new key only as a hosting environment variable.

## Newsletter

Signup is hosted externally by Constant Contact and linked from the newsletter
band. No API key needed.

## Deploying

The site is static with one serverless function, so it deploys as-is from the
repository root — no build step, no framework preset.

**Vercel (recommended):** import the repository at
[vercel.com/new](https://vercel.com/new). Leave the framework preset as *Other*,
build command empty, and output directory as the repository root. Then add
`RESEND_API_KEY` under Settings → Environment Variables and redeploy. Every push
to the default branch deploys automatically after that.

**From a terminal:**

```sh
npm i -g vercel
vercel login
vercel --prod
```

`package.json` sets `"type": "module"` so `api/contact.js` is loaded as ES module
rather than CommonJS; without it the function fails at import.
