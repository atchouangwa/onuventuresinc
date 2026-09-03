# Onu Ventures — website

Static marketing site for Onu Ventures, Inc., implemented from the Claude Design
canvas `Onu Ventures Home.dc.html`.

## What's here

```
index.html            Home page
assets/css/site.css   Styles (design tokens + components)
assets/js/site.js     Header scroll state, mobile menu, stat counters, contact form
assets/               Logos
web/                  Project renderings
api/contact.js        Serverless contact-form handler (Resend)
```

The site is plain HTML/CSS/JS with no build step — deploy the repository root as-is.

## Pages

Only the **home page** is implemented in this change. The header, mobile menu and
footer already link to `about.html`, `approach.html`, `portfolio.html` and
`news.html`; those pages come from the remaining canvases in the same design
project and are not built yet.

## Renderings

`web/` holds the full set of project renderings supplied for the site, in WebP.
The home page uses four of them; the rest are here for the remaining pages:

| File | Subject |
| --- | --- |
| `hero.webp` | Townhome + retail development, aerial (home hero) |
| `townhomes-retail-aerial.webp` | Same development, closer aerial |
| `trailblazer.webp` | Trailblazer Village courtyard at dusk |
| `miss-eddies-interior.webp` | Miss Eddie's Market & Café, interior |
| `miss-eddies-exterior.webp` | Miss Eddie's Market & Café, exterior aerial |
| `adaline-street.webp` | The Adaline, street level |
| `adaline-aerial.webp` | The Adaline, aerial |
| `colonial-5300.webp` | 5300 Colonial townhomes |
| `edison-arts-exterior.webp` | Edison Cultural Arts Center, entrance |
| `edison-arts-lobby.webp` | Edison Cultural Arts Center, lobby bar |
| `edison-arts-lounge.webp` | Edison Cultural Arts Center, lounge |
| `new-life-farms.webp` | New Life Farms, farmhouse and vineyard |
| `single-family-aerial.webp` | Single-family subdivision, aerial |
| `lakeside-homes.webp` | Lakeside homes and trail |
| `townhome-courtyard.webp` | Townhome courtyard |
| `townhomes-lane-aerial.webp` | Townhome lane, aerial |
| `brick-townhomes.webp` | Brick townhomes, corner |

Subjects are described from the renderings themselves; confirm the project
attribution before using a file on a page that names the project.

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
