// Monta o certificado (frente e verso) a partir dos dados do registro.
window.CR = (() => {
  const M = ['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro'];
  const x = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const dt = (s) => { const [a, m, d] = String(s || '').split('-'); return a ? `${+d} de ${M[+m - 1]} de ${a}` : ''; };
  const qr = (t) => { try { const q = qrcode(0, 'M'); q.addData(t); q.make(); return q.createSvgTag({ cellSize: 4, margin: 0 }); } catch (e) { return ''; } };
  function render(d, el) {
    const url = location.origin + '/certificado?n=' + encodeURIComponent(d.numero) + '&c=' + d.codigo;
    const cpf = d.cpf ? `, CPF ${x(d.cpf)},` : '';
    el.innerHTML = `<div class="cv-actions"><button class="btn gold" type="button" onclick="print()">Baixar em PDF / imprimir</button></div>
<div class="cert-sheet cert-front"><img class="cf-wm" src="/marca-wn-200.png" alt=""><div class="cf-in"><img class="cf-logo" src="/marca-wn-200.png" alt="">
<div class="cf-br">WALKER CONSULTORIA EDUCACIONAL</div><h2>Certificado de conclusão</h2><p class="cf-sub">Certificamos que</p>
<div class="cf-nm">${x(d.nome)}</div><p class="cf-tx">${cpf ? cpf.slice(2, -1) + ', ' : ''}concluiu, com aproveitamento, o curso livre de atualização profissional</p>
<div class="cf-curso">${x(d.curso)}</div><p class="cf-tx">promovido pela Walker Consultoria Educacional sob a coordenação do Prof. Walker Nascimento, com carga horária total de <b>${x(d.carga)} horas</b>, concluído em ${dt(d.data)}.</p>
<div class="cf-ft"><div class="cf-sig"><img src="/assinatura.png" alt="Assinatura">Prof. Walker Nascimento<span>Walker Consultoria Educacional</span></div>
<div class="cf-reg">Registro nº <b>${x(d.numero)}</b><br>Curso livre de atualização profissional</div></div></div></div>
<div class="cert-sheet cert-back"><div class="cb-in"><h3>Ementa</h3>${d.ementa ? `<p class="cb-em">${x(d.ementa)}</p>` : ''}
<h4>Conteúdo programático</h4>${d.conteudo && d.conteudo.length ? '<ol>' + d.conteudo.map((t) => '<li>' + x(t) + '</li>').join('') + '</ol>' : '<p>Conforme o programa do curso.</p>'}
<div class="cb-grid"><div><span>Participante</span><b>${x(d.nome)}</b></div><div><span>CPF</span><b>${x(d.cpf || '—')}</b></div><div><span>Carga horária</span><b>${x(d.carga)} horas</b></div><div><span>Conclusão</span><b>${dt(d.data)}</b></div></div>
<div class="cb-ver"><div class="cb-qr">${qr(url)}</div><div><span>Registro nº</span><b class="cb-num">${x(d.numero)}</b><span>Código de verificação</span><b class="cb-num">${x(d.codigo)}</b>
<p>Confira a autenticidade em <b>walkerconsultoria.com.br/certificado</b> ou pelo QR code.</p></div></div>
<p class="cb-leg">Curso livre amparado pela Lei nº 9.394/1996 e pelo Decreto nº 5.154/2004. Por ser de livre oferta, não exige credenciamento no MEC. Destina-se ao aperfeiçoamento profissional e não confere grau acadêmico ou técnico.</p></div></div>`;
  }
  return { x, dt, render };
})();
