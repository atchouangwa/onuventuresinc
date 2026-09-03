// POST /api/contact — sends the website contact form to the Onu Ventures team via Resend.
// Works as-is on Vercel (api/contact.js). Requires env var RESEND_API_KEY.
// Netlify/Cloudflare: same body, adapt the handler signature.

const TO = ['info@onuventuresinc.com', 'kvillanueva@onuventuresinc.com', 'mo@onuventuresinc.com'];
const FROM = 'Onu Ventures Website <updates@onuventuresinc.com>';

const esc = (v) => String(v ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { name = '', email = '', company = '', inquiryType = '', message = '' } =
    typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});

  if (!name.trim() || !company.trim() || !inquiryType.trim() || !message.trim() || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    return res.status(400).json({ error: 'All fields are required, including a valid email address.' });
  }
  if (message.length > 5000) return res.status(400).json({ error: 'Message too long.' });

  const rows = [
    ['Name', name],
    ['Email', email],
    ['Company', company],
    ['Inquiry type', inquiryType]
  ];

  const html = `<div style="font-family:Helvetica,Arial,sans-serif;font-size:15px;color:#231f20">
  <h2 style="font-weight:400;border-bottom:2px solid #c3b04a;padding-bottom:8px">New website inquiry</h2>
  <table cellpadding="0" cellspacing="0" style="margin:0 0 20px">
    ${rows.map(([k, v]) => `<tr><td style="padding:4px 16px 4px 0;color:#6b6663">${esc(k)}</td><td style="padding:4px 0"><strong>${esc(v)}</strong></td></tr>`).join('')}
  </table>
  <p style="margin:0 0 6px;color:#6b6663">Message</p>
  <p style="margin:0;white-space:pre-wrap;line-height:1.6">${esc(message)}</p>
</div>`;

  const text = rows.map(([k, v]) => `${k}: ${v}`).join('\n') + `\n\nMessage:\n${message}`;

  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${process.env.RESEND_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        from: FROM,
        to: TO,
        reply_to: email,
        subject: `Website inquiry — ${name}${inquiryType ? ' · ' + inquiryType : ''}`,
        html,
        text
      })
    });
    if (!r.ok) {
      const detail = await r.text();
      console.error('Resend error', r.status, detail);
      return res.status(502).json({ error: 'Email delivery failed' });
    }
    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Unexpected error' });
  }
}
