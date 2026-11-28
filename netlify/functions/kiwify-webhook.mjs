// Recebe os avisos da Kiwify (compra aprovada, reembolso, chargeback)
// e mantém a lista de alunos que podem emitir certificado.
import { store, somaStats, chaveAluno, chaveCpf, cursoDoProduto, assinaturaKiwifyOk, json } from "../lib/cert-lib.mjs";

export default async (req) => {
  if (req.method !== "POST") return json({ ok: false }, 405);
  const raw = await req.text();
  const url = new URL(req.url);
  if (!assinaturaKiwifyOk(raw, url.searchParams.get("signature"))) return json({ ok: false, erro: "assinatura" }, 401);

  let d;
  try { d = JSON.parse(raw); } catch { return json({ ok: false }, 400); }
  const cli = d.Customer || d.customer || {};
  const prod = d.Product || d.product || {};
  const email = cli.email, cpf = cli.CPF || cli.cpf || cli.document;
  const curso = cursoDoProduto(prod.product_name || prod.name, prod.product_id || prod.id);
  if (!email || !cpf || !curso) return json({ ok: true, ignorado: true });

  const s = store();
  const chave = `alunos/${chaveAluno(email, cpf)}/${curso.id}`;
  const status = String(d.order_status || d.webhook_event_type || "").toLowerCase();
  const estorno = /refund|reembols|chargeback|chargedback/.test(status);

  if (estorno) {
    await s.setJSON(chave, { situacao: "estornado", pedido: d.order_id, em: new Date().toISOString() });
    // cancela certificado já emitido para este aluno/curso
    const idx = await s.get(`emitidos/${chaveCpf(cpf)}/${curso.id}`, { type: "json" });
    if (idx && idx.numero) {
      const c = await s.get(`cert/${idx.numero}`, { type: "json" });
      if (c) { c.situacao = "cancelado"; await s.setJSON(`cert/${idx.numero}`, c); }
    }
    return json({ ok: true, cancelado: true });
  }
  if (/paid|approved|aprovad/.test(status)) {
    const antes = await s.get(chave, { type: "json" });
    if (!antes) await somaStats(curso.id, "alunos");
    await s.setJSON(chave, { situacao: "ativo", pedido: d.order_id, nome: cli.full_name || "", em: new Date().toISOString() });
    return json({ ok: true, registrado: true });
  }
  return json({ ok: true, ignorado: true });
};

export const config = { path: "/api/kiwify" };
