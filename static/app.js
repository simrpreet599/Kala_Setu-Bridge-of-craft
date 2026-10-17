(() => {
  const $ = id => document.getElementById(id), t0 = Date.now();
  const S = {enh: null, fields: {}, listing: {}, price: null};
  const show = n => { [1,2,3,4].forEach(i => $('s'+i).classList.toggle('hide', i !== n));
    [...$('steps').children].forEach((el, i) => el.classList.toggle('on', i < n)); window.scrollTo(0, 0); };
  const post = async (url, body, isForm) => {
    const r = await fetch(url, {method: 'POST', headers: isForm ? {} : {'Content-Type': 'application/json'}, body: isForm ? body : JSON.stringify(body)});
    const j = await r.json(); if (!r.ok) throw new Error(j.error || 'Something went wrong'); return j; };
  const busy = (b, on) => { b.disabled = on; };

  // 1 photo
  $('photo').onchange = e => { const f = e.target.files[0]; if (f) { $('imgBefore').src = URL.createObjectURL(f); } };
  $('btnEnh').onclick = async e => {
    const f = $('photo').files[0]; if (!f) return alert('Please choose a photo first.');
    const fd = new FormData(); fd.append('photo', f); fd.append('bg', $('bg').value); busy(e.target, true); e.target.textContent = 'Working…';
    try { const j = await post('/api/enhance', fd, true); S.enh = j; $('imgAfter').src = j.enhanced_url; $('enhOut').classList.remove('hide');
      $('enhWarn').innerHTML = j.warnings.map(w => `<div class="warnbox">⚠ ${w}</div>`).join('');
      $('enhMetrics').textContent = `Brightness ${j.before.brightness} → ${j.after.brightness} · background ${j.background_removed ? 'removed' : 'kept'}`;
      $('to2').disabled = false;
    } catch (err) { alert(err.message); }
    busy(e.target, false); e.target.textContent = '✨ Improve photo'; };
  $('to2').onclick = () => show(2); $('skip1').onclick = () => show(2);

  // 2 speech + catalog
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition; let rec = null;
  $('mic').onclick = () => {
    if (!SR) { $('micMsg').textContent = 'Voice input not supported in this browser. Please type, or use Chrome.'; return; }
    if (rec) { rec.stop(); return; }
    rec = new SR(); rec.lang = $('lang').value; rec.interimResults = true; rec.continuous = true; const base = $('speech').value;
    rec.onresult = ev => { let s = ''; for (const r of ev.results) s += r[0].transcript; $('speech').value = (base + ' ' + s).trim(); };
    rec.onend = () => { rec = null; $('mic').classList.remove('rec'); $('micMsg').textContent = 'Tap to speak again'; };
    rec.onerror = ev => { $('micMsg').textContent = 'Voice error: ' + ev.error + '. You can type instead.'; };
    rec.start(); $('mic').classList.add('rec'); $('micMsg').textContent = 'Listening… tap to stop'; };
  const FK = ['item', 'material', 'color', 'technique', 'dimensions'];
  const fill = d => { S.fields = d.fields; S.listing = d.listing;
    FK.forEach(k => $('f_' + k).value = d.fields[k] || ''); $('t_en').value = d.listing.title_en; $('t_hi').value = d.listing.title_hi;
    $('d_en').value = d.listing.desc_en; $('d_hi').value = d.listing.desc_hi;
    $('missing').innerHTML = d.listing.missing.map(m => `<div class="warnbox">❓ ${m}</div>`).join('');
    if (d.fields.material_cost) $('p_mat').value = d.fields.material_cost; if (d.fields.labour_hours) $('p_hrs').value = d.fields.labour_hours;
    if (d.fields.asking_price) S.asking = d.fields.asking_price;
    $('hrsNote').textContent = d.fields.hours_from_days_assumption ? 'Hours were estimated from days at 6 working hours/day. Please correct if needed.' : '';
    $('catOut').classList.remove('hide'); };
  $('btnCat').onclick = async e => {
    if (!$('speech').value.trim()) return alert('Please speak or type a few details.'); busy(e.target, true);
    try { fill(await post('/api/catalog', {text: $('speech').value, story: $('story').value})); } catch (err) { alert(err.message); } busy(e.target, false); };
  $('btnRegen').onclick = async () => { const fields = {}; FK.forEach(k => fields[k] = $('f_' + k).value);
    try { const d = await post('/api/catalog', {fields, story: $('story').value});
      S.fields = {...S.fields, ...fields}; $('t_en').value = d.listing.title_en; $('t_hi').value = d.listing.title_hi; $('d_en').value = d.listing.desc_en; $('d_hi').value = d.listing.desc_hi;
      $('missing').innerHTML = d.listing.missing.map(m => `<div class="warnbox">❓ ${m}</div>`).join(''); } catch (err) { alert(err.message); } };
  $('to3').onclick = () => { FK.forEach(k => S.fields[k] = $('f_' + k).value || null); show(3); };

  // 3 price
  const inr = n => '₹' + Number(n).toLocaleString('en-IN');
  $('btnPrice').onclick = async e => { busy(e.target, true);
    try { const cat = S.fields.category;
      const j = await post('/api/price', {item: S.fields.item, category: cat, material_cost: $('p_mat').value, labour_hours: $('p_hrs').value, labour_rate: $('p_rate').value, margin_pct: $('p_margin').value});
      S.price = j; $('pLabel').textContent = j.label; $('pFloor').textContent = inr(j.cost_floor); $('pRange').textContent = `${inr(j.retail.low)} – ${inr(j.retail.high)} (suggested ${inr(j.retail.suggested)})`;
      $('pWhole').textContent = inr(j.wholesale_suggested); $('pConf').textContent = 'Confidence: ' + j.confidence;
      $('pNotes').innerHTML = j.notes.map(n => `<div class="warnbox">${n}</div>`).join('');
      $('p_final').value = S.asking || j.retail.suggested; $('priceOut').classList.remove('hide');
    } catch (err) { alert(err.message); } busy(e.target, false); };
  $('to4').onclick = () => { if (!$('p_final').value) return alert('Please enter your selling price.');
    if (S.price && Number($('p_final').value) < S.price.cost_floor && !confirm('Your price (' + inr($('p_final').value) + ') is below your cost floor (' + inr(S.price.cost_floor) + '). Continue anyway?')) return;
    $('summary').innerHTML = `<div class="grid g2"><div>${S.enh ? `<img class="thumb" src="${S.enh.enhanced_url}">` : ''}</div><div><h3>${$('t_en').value}</h3><p>${$('t_hi').value}</p><div class="stat">${inr($('p_final').value)}</div></div></div>`; show(4); };

  // 4 publish
  $('btnPub').onclick = async e => { busy(e.target, true);
    try { const f = S.fields; const j = await post('/api/products', {title_en: $('t_en').value, title_hi: $('t_hi').value, desc_en: $('d_en').value, desc_hi: $('d_hi').value,
        item: f.item, category: f.category || null, material: f.material, color: f.color, technique: f.technique, dimensions: f.dimensions,
        original_image: S.enh && S.enh.original, enhanced_image: S.enh && S.enh.enhanced, metrics: S.enh ? {before: S.enh.before, after: S.enh.after} : {},
        price: {set: Number($('p_final').value), low: S.price && S.price.retail.low, high: S.price && S.price.retail.high, label: S.price && S.price.label, confidence: S.price && S.price.confidence},
        session_seconds: Math.round((Date.now() - t0) / 1000)});
      location.href = j.url; } catch (err) { $('pubMsg').textContent = err.message; busy(e.target, false); } };
})();
