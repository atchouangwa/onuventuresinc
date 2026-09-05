# Marin Home Properties — website

Static marketing site for Marin Home Properties (Susan Coleman, Coldwell Banker
Realty), implemented from the `Marin Home Properties.dc.html` canvas in the
Claude Design project.

It is self-contained: deploy this directory as a site root, or serve it from a
sub-path — every link is relative.

```
index.html             Home
recently-sold.html     Recently Sold
assets/css/site.css    Styles (design tokens + components)
assets/js/site.js      Mobile nav, FAQ accordion, interest chips, contact form
assets/img/            Illustrations (see below) + favicon
tools/                 The illustration generator (not part of the build)
```

Plain HTML/CSS/JS, no build step.

## Pages

The canvas is a single-page app with two routes (`home` and `sold`); the two are
split into real pages here so each has its own URL, title and description. The
header, mobile panel and footer are duplicated across both — keep them in sync.

| File | Canvas route | Sections |
| --- | --- | --- |
| `index.html` | `isHome` | Hero, market intro, About, the three-step process, twelve communities, market intelligence + community snapshot, selected sales, testimonials, FAQ, contact |
| `recently-sold.html` | `isSold` | Hero, three featured sales, the full-record embed slot, closing call to action |

Interactive behaviour ported from the canvas lives in `assets/js/site.js`. With
JavaScript off the desktop navigation, every FAQ answer and the form itself all
remain in the document; only the mobile panel is unreachable.

## Images

Every image slot in the canvas is a photography brief, not a photograph, and no
photography was supplied with the project. So that nothing renders as an empty
swatch, `assets/img/` ships flat SVG illustrations drawn in the canvas palette
by `tools/make-illustrations.py`:

| File | Stands in for |
| --- | --- |
| `hero-marin.svg` | Home hero — elevated Marin viewpoint, Bay, golden hour |
| `hero-recently-sold.svg` | Recently Sold hero — residential exterior at dusk |
| `interior-bay-view.svg` | Living room, wall of glass, Bay and the SF skyline |
| `susan-coleman.svg` | **Susan's portrait.** A monogram card, deliberately not a likeness |
| `community-*.svg` (12) | One per community card |
| `sale-01…06.svg` | Sold-property photographs |

To swap in real photography, drop the file in `assets/img/` and repoint the one
`<img>` that uses it (update its `alt` at the same time). Aspect ratios the
layout expects: hero 16:10 or wider, portrait 4:5, community 4:3, sale 16:10
(the home page crops the same file to 5:4).

Rerun the generator with `python3 tools/make-illustrations.py` — it rewrites
`assets/img/` and nothing else depends on it.

## Before launch

- [ ] **Portrait.** Replace `assets/img/susan-coleman.svg` with the supplied
      photograph.
- [ ] **Sales.** `index.html` (Selected Sales) and `recently-sold.html`
      (Featured Sales) carry structure only — address, price, beds/baths, days
      on market and the short story are all marked *to be added*. Fill them
      from the MLS record. The site should not go live with these placeholders.
- [ ] **MLS / IDX.** Replace the `.embed-slot` block in `recently-sold.html`
      with the approved provider snippet and restyle it to the ivory palette
      and the Cormorant / Jost type.
- [ ] **Testimonials.** The home page renders the Jotform website widget
      (`JFWebsiteWidget-01a0723b835070008e40dd8bcdd53d0976e3`) in place of the
      former three review cards. It loads a third-party script at runtime, so
      it is inert when the page is opened over `file://` and shows nothing.
      Verify it on a served page, and manage the testimonial content in Jotform.
- [ ] **Market figures.** The four metrics and the eight snapshot rows are the
      canvas's Q1–Q2 2026 numbers, kept together in one block in `index.html`.
      Verify against BAREIS before publication and refresh each quarter.
- [ ] **Contact form.** `assets/js/site.js` acknowledges the enquiry in the page
      and transmits nothing, as the canvas specifies. To deliver it, POST the
      `FormData` to a serverless handler (the sibling Onu Ventures site has a
      Resend-based `api/contact.js` worth copying) and reveal the confirmation
      only once it resolves. Then drop the "not yet wired" note under the
      submit button.
- [ ] **Domain-dependent metadata.** Both pages need `<link rel="canonical">`,
      `og:url` and a 1200×630 `og:image` once the domain is known.
- [ ] **Licence number.** The footer says *CalRE license number pending
      confirmation* — replace with the real number.
