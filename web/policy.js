// policy.js — run after policy.html is injected into #tab-content
// It expects elements with ids: changesContainer, addRow, resetAll, runReform, status, result

(function(){
  // small helpers
  function el(id){ return document.getElementById(id); }
  const changesContainer = el('changesContainer');
  const statusEl = el('status');
  const resultEl = el('result');

  if (!changesContainer) {
    console.warn('policy.js: changesContainer not found - aborting');
    return;
  }

  let optionsData = {};

  async function loadOptions() {
    try {
      const resp = await fetch('/policy_options');
      const data = await resp.json();
      if (!resp.ok || data.status !== 'ok') {
        console.error('policy_options fetch error', data);
        showError('Failed to load policy options from server. See console for details.');
        return [];
      }
      optionsData = data.options || {};
      return Object.keys(optionsData).sort();
    } catch (err) {
      console.error('policy_options error', err);
      showError('Failed to contact server for policy options.');
      return [];
    }
  }

  function showError(msg) {
    resultEl.innerHTML = `<div style="color:crimson"><strong>Error:</strong> ${msg}</div>`;
  }

  function makeParamSelect() {
    const sel = document.createElement('select');
    sel.name = 'param';
    sel.style.width = '300px';
    const emptyOpt = document.createElement('option');
    emptyOpt.value = '';
    emptyOpt.textContent = '-- select parameter --';
    sel.appendChild(emptyOpt);
    Object.keys(optionsData).sort().forEach(k => {
      const opt = document.createElement('option');
      opt.value = k;
      opt.textContent = k;
      sel.appendChild(opt);
    });
    return sel;
  }

  function makeRow(id) {
    const row = document.createElement('div');
    row.className = 'row';
    row.dataset.id = id;

    const paramSelect = makeParamSelect();

    const pairs = document.createElement('div');
    pairs.className = 'pairs';

    function makePair(index){
      const span = document.createElement('span');
      span.className = 'pair';
      const y = document.createElement('input'); y.type='text'; y.name='year' + index; y.placeholder='Year (e.g. 2022)';
      const v = document.createElement('input'); v.type='text'; v.name='value' + index; v.placeholder='Value (e.g. 0.18)';
      span.appendChild(y); span.appendChild(v);
      return span;
    }

    pairs.appendChild(makePair(0));

    const addPairBtn = document.createElement('button'); addPairBtn.type='button'; addPairBtn.textContent = '+';
    const removeRowBtn = document.createElement('button'); removeRowBtn.type='button'; removeRowBtn.textContent = '-';
    const resetRowBtn = document.createElement('button'); resetRowBtn.type='button'; resetRowBtn.textContent = 'Reset';

    addPairBtn.title = 'Add year/value pair';
    removeRowBtn.title = 'Delete this change line';
    resetRowBtn.title = 'Reset this line';

    addPairBtn.addEventListener('click', () => {
      const idx = pairs.querySelectorAll('.pair').length;
      pairs.appendChild(makePair(idx));
    });

    removeRowBtn.addEventListener('click', () => {
      row.remove();
    });

    resetRowBtn.addEventListener('click', () => {
      paramSelect.value = '';
      pairs.innerHTML = '';
      pairs.appendChild(makePair(0));
    });

    paramSelect.addEventListener('change', () => {
      const chosen = paramSelect.value;
      const firstPair = pairs.querySelector('.pair');
      if (!firstPair) return;
      const yearInput = firstPair.querySelector('input[name^="year"]');
      const valueInput = firstPair.querySelector('input[name^="value"]');
      if (!chosen || !optionsData[chosen]) {
        if (yearInput) yearInput.value = '';
        if (valueInput) valueInput.value = '';
        return;
      }
      const meta = optionsData[chosen];
      if (meta.row_label && meta.row_label.length > 0) yearInput.value = String(meta.row_label[0]); else yearInput.value = '';
      if (meta.value !== undefined && meta.value !== null) {
        if (Array.isArray(meta.value)) {
          if (meta.value.length > 0 && Array.isArray(meta.value[0])) valueInput.value = JSON.stringify(meta.value[0]);
          else if (meta.value.length > 0) valueInput.value = String(meta.value[0]);
          else valueInput.value = '';
        } else valueInput.value = String(meta.value);
      } else valueInput.value = '';
    });

    row.appendChild(paramSelect);
    row.appendChild(pairs);
    row.appendChild(addPairBtn);
    row.appendChild(removeRowBtn);
    row.appendChild(resetRowBtn);
    return row;
  }

  // initialize UI (async)
  (async function init(){
    await loadOptions();
    changesContainer.appendChild(makeRow(0));

    const addBtn = el('addRow');
    const resetBtn = el('resetAll');
    const runBtn = el('runReform');

    if (addBtn) addBtn.addEventListener('click', ()=>{
      const id = changesContainer.querySelectorAll('.row').length;
      changesContainer.appendChild(makeRow(id));
    });

    if (resetBtn) resetBtn.addEventListener('click', ()=>{
      changesContainer.innerHTML = '';
      changesContainer.appendChild(makeRow(0));
      resultEl.innerHTML = '';
      if (statusEl) statusEl.textContent = '';
    });

    if (runBtn) runBtn.addEventListener('click', async ()=>{
      if (statusEl) statusEl.textContent = 'Running...';
      resultEl.innerHTML = '';
      const rows = Array.from(changesContainer.querySelectorAll('.row'));
      const changes = [];
      for (const r of rows) {
        const sel = r.querySelector('select[name=param]');
        const param = sel ? sel.value : '';
        if (!param) continue;
        const pairEls = Array.from(r.querySelectorAll('.pair'));
        const years = [], values = [];
        for (const p of pairEls) {
          const y = p.querySelector('input[name^="year"]').value.trim();
          const v = p.querySelector('input[name^="value"]').value.trim();
          if (y === '' || v === '') continue;
          years.push(y);
          values.push(v);
        }
        if (years.length > 0) changes.push({param: param, years: years, values: values});
      }

      if (changes.length === 0) {
        alert('Please add at least one parameter change with year and value.');
        if (statusEl) statusEl.textContent = '';
        return;
      }

      try {
        const resp = await fetch('/run_reform', {
          method: 'POST', headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({changes})
        });
        const data = await resp.json();
        if (!resp.ok || data.status !== 'ok') {
          if (statusEl) statusEl.textContent = 'Error';
          resultEl.innerHTML = `<pre class="trace">${JSON.stringify(data, null, 2)}</pre>`;
          return;
        }
        if (statusEl) statusEl.textContent = 'Completed';
        const rowsOut = data.rows || [];
        let html = '<h3>pit_revenue_projection.csv</h3>';
        html += `<p><a class="link" href="/download/pit_revenue_projection.csv" target="_blank">Download CSV</a></p>`;
        if (rowsOut.length > 0) {
          const cols = Object.keys(rowsOut[0]);
          html += '<table><thead><tr>' + cols.map(c => `<th>${c}</th>`).join('') + '</tr></thead><tbody>';
          for (const row of rowsOut) {
            html += '<tr>' + cols.map(c => `<td>${row[c] ?? ''}</td>`).join('') + '</tr>';
          }
          html += '</tbody></table>';
        } else {
          html += '<div>No rows returned.</div>';
        }
        resultEl.innerHTML = html;
      } catch (err) {
        console.error('run_reform error', err);
        if (statusEl) statusEl.textContent = 'Request failed';
        resultEl.innerHTML = `<pre class="trace">${err.toString()}</pre>`;
      }
    });
  })();

})(); // end policy.js


