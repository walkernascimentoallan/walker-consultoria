import { getStore } from "@netlify/blobs";
import { createHash, createHmac, randomBytes, timingSafeEqual } from "node:crypto";
import CFG from "../../content/certificacao.json" with { type: "json" };
import CURSOS from "../../content/cursos.json" with { type: "json" };

export const store = () => getStore({ name: "certificados", consistency: "strong" });
const SALT = () => process.env.CERT_SALT || "wce-walkerconsultoria.com.br";

export const soDigitos = (s) => String(s || "").replace(/\D/g, "");
export const normEmail = (s) => String(s || "").trim().toLowerCase();

export function cpfValido(c) {
  c = soDigitos(c);
  if (c.length !== 11 || /^(\d)\1{10}$/.test(c)) return false;
  const dv = (n) => {
    let s = 0;
    for (let i = 0; i < n; i++) s += +c[i] * (n + 1 - i);
    const r = (s * 10) % 11;
    return r === 10 ? 0 : r;
  };
  return dv(9) === +c[9] && dv(10) === +c[10];
}

export const cpfMascara = (c) => {
  c = soDigitos(c);
  return c.length === 11 ? `***.${c.slice(3, 6)}.${c.slice(6, 9)}-**` : "";
};

export const chaveAluno = (email, cpf) =>
  createHash("sha256").update(`${normEmail(email)}|${soDigitos(cpf)}|${SALT()}`).digest("hex");

export const chaveCpf = (cpf) =>
  createHash("sha256").update(`${soDigitos(cpf)}|${SALT()}`).digest("hex");

export function cursoCfg(id) {
  const c = (CFG.cursos || []).find((x) => x.id === id);
  if (!c) return null;
  const pag = (CURSOS.cursos || []).find(
    (x) => (x.titulo || "").trim().toLowerCase() === (c.titulo || "").trim().toLowerCase()
  ) || {};
  return {
    ...c,
    carga: Math.max(CFG.carga_minima || 16, +c.carga_horaria || 16),
    ementa: pag.texto || "",
    conteudo: (pag.topicos || []).map((t) => t.texto).filter(Boolean),
  };
}

export function cursoDoProduto(nomeProduto, idProduto) {
  const n = String(nomeProduto || "").toLowerCase();
  return (CFG.cursos || []).find(
    (c) =>
      (c.kiwify_id && String(c.kiwify_id) === String(idProduto)) ||
      (c.kiwify_produto && n.includes(String(c.kiwify_produto).toLowerCase()))
  );
}

export const notaMinima = () => CFG.nota_minima || 7;
export const prefixo = () => CFG.prefixo || "WCE";

export function assinaturaKiwifyOk(rawBody, assinatura) {
  const token = process.env.KIWIFY_TOKEN;
  if (!token || !assinatura) return false;
  const esperado = createHmac("sha1", token).update(rawBody).digest("hex");
  const a = Buffer.from(esperado), b = Buffer.from(String(assinatura));
  return a.length === b.length && timingSafeEqual(a, b);
}

export const codigoNovo = () => randomBytes(4).toString("hex").slice(0, 6).toUpperCase();

export const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });

export async function somaStats(cursoId, campo) {
  const s = store();
  for (let i = 0; i < 5; i++) {
    const cur = await s.getWithMetadata("stats", { type: "json" });
    const d = (cur && cur.data) || { total: 0, cursos: {} };
    d.cursos[cursoId] = d.cursos[cursoId] || { emitidos: 0, alunos: 0 };
    d.cursos[cursoId][campo] = (d.cursos[cursoId][campo] || 0) + 1;
    if (campo === "emitidos") d.total = (d.total || 0) + 1;
    const r = await s.setJSON("stats", d, cur ? { onlyIfMatch: cur.etag } : { onlyIfNew: true });
    if (r && r.modified !== false) return;
  }
}
