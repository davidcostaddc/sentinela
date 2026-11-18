const tabs = document.querySelectorAll('.tab');
const input = document.getElementById('contentInput');
const label = document.getElementById('fieldLabel');
const helper = document.getElementById('helperText');
const counter = document.getElementById('counter');
const form = document.getElementById('analysisForm');
const button = document.getElementById('analyzeButton');
let mode = 'link';

tabs.forEach(tab => tab.addEventListener('click', () => {
  mode = tab.dataset.mode;
  tabs.forEach(item => item.classList.toggle('active', item === tab));
  if (mode === 'link') {
    label.textContent = 'COLE O LINK QUE DESEJA ANALISAR';
    input.placeholder = 'https://exemplo.com/pagina';
    input.maxLength = 2048;
    helper.textContent = 'A análise examina o endereço como texto. O link não será aberto.';
  } else {
    label.textContent = 'COLE O CONTEÚDO DO E-MAIL OU MENSAGEM';
    input.placeholder = 'Cole aqui o texto da mensagem suspeita...';
    input.maxLength = 20000;
    helper.textContent = 'Remova informações pessoais antes de enviar o texto para análise.';
  }
  input.value = '';
  counter.textContent = `0 / ${input.maxLength.toLocaleString('pt-BR')}`;
  document.getElementById('result').classList.add('hidden');
}));

input.addEventListener('input', () => {
  counter.textContent = `${input.value.length.toLocaleString('pt-BR')} / ${input.maxLength.toLocaleString('pt-BR')}`;
});

form.addEventListener('submit', async event => {
  event.preventDefault();
  const content = input.value.trim();
  if (!content) return;
  button.disabled = true;
  button.innerHTML = '<span>◌</span> Analisando...';
  try {
    const endpoint = mode === 'link' ? '/api/analyze/url' : '/api/analyze/email';
    const payload = mode === 'link' ? {url: content} : {content};
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Não foi possível realizar a análise.');
    renderResult(data);
  } catch (error) {
    showError(error.message);
  } finally {
    button.disabled = false;
    button.innerHTML = '<span>⌕</span> Analisar agora <b>→</b>';
  }
});

function renderResult(data) {
  const result = document.getElementById('result');
  const score = data.risk_score;
  const color = score >= 70 ? 'var(--red)' : score >= 35 ? 'var(--yellow)' : 'var(--green)';
  document.getElementById('scoreValue').textContent = score;
  document.getElementById('scoreRing').style.background = `conic-gradient(${color} ${score * 3.6}deg, #24364c 0deg)`;
  document.getElementById('riskLevel').textContent = data.risk_level;
  document.getElementById('riskSummary').textContent = data.indicators.length
    ? `Foram identificados ${data.indicators.length} indicador(es) que merecem atenção.`
    : 'Nenhum dos indicadores configurados foi encontrado. Isso não comprova que o conteúdo seja seguro.';
  const badge = document.getElementById('riskBadge');
  badge.textContent = data.risk_level.toUpperCase();
  badge.style.color = color;
  badge.style.border = `1px solid ${color}`;
  document.getElementById('findingCount').textContent = `${data.indicators.length} indicador(es)`;
  const list = document.getElementById('indicators');
  list.replaceChildren();
  if (!data.indicators.length) {
    const empty = document.createElement('div');
    empty.className = 'empty';
    empty.textContent = 'Nenhum indicador configurado foi identificado nesta análise.';
    list.appendChild(empty);
  } else {
    data.indicators.forEach(item => {
      const card = document.createElement('article');
      card.className = 'indicator';
      const top = document.createElement('div');
      top.className = 'indicator-top';
      const name = document.createElement('span');
      name.textContent = item.name;
      const severity = document.createElement('span');
      severity.className = `severity ${item.severity}`;
      severity.textContent = item.severity;
      const desc = document.createElement('p');
      desc.textContent = item.description;
      top.append(name, severity);
      card.append(top, desc);
      list.appendChild(card);
    });
  }
  document.getElementById('recommendationText').textContent = data.recommendation;
  document.getElementById('disclaimerText').textContent = data.disclaimer;
  result.classList.remove('hidden');
  result.scrollIntoView({behavior: 'smooth', block: 'start'});
}

function showError(message) {
  const result = document.getElementById('result');
  result.classList.remove('hidden');
  document.getElementById('riskBadge').textContent = 'ERRO NA ANÁLISE';
  document.getElementById('riskLevel').textContent = 'Não foi possível analisar';
  document.getElementById('riskSummary').textContent = message;
  document.getElementById('scoreValue').textContent = '—';
  document.getElementById('indicators').replaceChildren();
  document.getElementById('recommendationText').textContent = 'Confira o conteúdo informado e tente novamente.';
  document.getElementById('disclaimerText').textContent = '';
  result.scrollIntoView({behavior: 'smooth', block: 'start'});
}
