// Emissão (POST /api/certificado) e consulta (GET /api/certificado?n=...&c=...)
import {
  store, somaStats, chaveAluno, chaveCpf, cpfValido, cpfMascara, cursoCfg, notaMinima, prefixo, codigoNovo, json, normEmail,
} from "../lib/cert-lib.mjs";

const publico = (c) => ({
  numero: c.numero, codigo: c.codigo, nome: c.nome, cpf: c.cpf, curso: c.curso, carga: c.carga,
  data: c.data, ementa: c.ementa, conteudo: c.conteudo, situacao: c.situacao,
});

export default async (req) => {
  const s = store();
  const url = new URL(req.url);

  if (req.method === "GET" && url.searchParams.get("stats")) {
    const st = (await s.get("stats", { type: "json" })) || { total: 0, cursos: {} };
    return json({ ok: true, total: st.total || 0, cursos: st.cursos || {} });
  }
  if (req.method === "GET") {
    const n = String(url.searchParams.get("n") || "").trim().toUpperCase();
    const c = String(url.searchParams.get("c") || "").trim().toUpperCase();
    if (!n || !c) return json({ ok: false }, 400);
    const cert = await s.get(`cert/${n}`, { type: "json" });
    if (!cert || cert.codigo !== c) return json({ ok: false }, 404);
    return json({ ok: true, certificado: publico(cert) });
  }

  if (req.method !== "POST") return json({ ok: false }, 405);
  let b;
  try { b = await req.json(); } catch { return json({ ok: false, erro: "Dados inválidos." }, 400); }

  const email = normEmail(b.email), cpf = String(b.cpf || ""), nome = String(b.nome || "").trim().replace(/\s+/g, " ");
  const curso = cursoCfg(b.curso);
  if (!curso || !curso.ativo) return json({ ok: false, erro: "Este curso ainda não emite certificado." }, 400);
  if (!/^\S+@\S+\.\S+$/.test(email)) return json({ ok: false, erro: "Confira o e-mail." }, 400);
  if (!cpfValido(cpf)) return json({ ok: false, erro: "Confira o CPF." }, 400);
  if (nome.split(" ").length < 2 || nome.length > 90) return json({ ok: false, erro: "Escreva o nome completo." }, 400);

  // compra confirmada pela Kiwify, com o mesmo e-mail e CPF
  const aluno = await s.get(`alunos/${chaveAluno(email, cpf)}/${curso.id}`, { type: "json" });
  if (!aluno) return json({ ok: false, erro: "Não encontramos uma compra deste curso com este e-mail e CPF. Use os mesmos dados da compra na Kiwify." }, 403);
  if (aluno.situacao !== "ativo") return json({ ok: false, erro: "Esta compra foi estornada e não dá direito a certificado." }, 403);

  // já emitido: devolve o mesmo certificado
  const idxKey = `emitidos/${chaveCpf(cpf)}/${curso.id}`;
  const idx = await s.get(idxKey, { type: "json" });
  if (idx && idx.numero) {
    const c = await s.get(`cert/${idx.numero}`, { type: "json" });
    if (c) return json({ ok: true, jaEmitido: true, certificado: publico(c) });
  }

  // avaliação final
  const resp = Array.isArray(b.respostas) ? b.respostas : [];
  const acertos = curso.perguntas.reduce((t, q, i) => t + (Number(resp[i]) === q.resposta ? 1 : 0), 0);
  if (acertos < notaMinima())
    return json({ ok: false, reprovado: true, acertos, total: curso.perguntas.length,
      erro: `Você acertou ${acertos} de ${curso.perguntas.length}. São necessários ${notaMinima()} acertos. Revise o conteúdo e tente de novo.` }, 200);

  // número de registro em sequência
  const ano = new Date().getFullYear();
  let seq = 0;
  for (let t = 0; t < 5; t++) {
    const cont = await s.getWithMetadata("contador", { type: "json" });
    const atual = (cont && cont.data && cont.data.n) || 0;
    const r = await s.setJSON("contador", { n: atual + 1 }, cont ? { onlyIfMatch: cont.etag } : { onlyIfNew: true });
    if (r && r.modified !== false) { seq = atual + 1; break; }
  }
  if (!seq) return json({ ok: false, erro: "Tente de novo em alguns segundos." }, 503);

  const numero = `${prefixo()}-${ano}-${String(seq).padStart(4, "0")}`;
  const hoje = new Date(Date.now() - 3 * 3600e3).toISOString().slice(0, 10);
  const cert = {
    numero, codigo: codigoNovo(), nome, cpf: cpfMascara(cpf), curso: curso.titulo, curso_id: curso.id,
    carga: curso.carga, data: hoje, ementa: curso.ementa, conteudo: curso.conteudo,
    situacao: "valido", acertos, emitido_em: new Date().toISOString(),
  };
  await s.setJSON(`cert/${numero}`, cert);
  await s.setJSON(idxKey, { numero });
  await somaStats(curso.id, "emitidos");
  return json({ ok: true, certificado: publico(cert) });
};

export const config = { path: "/api/certificado" };
