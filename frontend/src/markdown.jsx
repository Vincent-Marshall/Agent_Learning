// 轻量 markdown 渲染器 + 引用角标装饰。
// 从原生版原样移植:零依赖、先转义再解析(防注入)、链接仅放行 http(s)。
// 引用角标用 DOM 树遍历把 [n] 换成可点 sup——协议与行为不变,只换宿主。

export function escapeHtml(s) {
  return s.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
}

function renderInline(s) {
  s = s.replace(/`([^`]+)`/g, (m, c) => "<code>" + c + "</code>");
  s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  s = s.replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<em>$2</em>");
  s = s.replace(/~~([^~]+)~~/g, "<del>$1</del>");
  s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener">$1</a>');
  return s;
}

export function renderMarkdown(md) {
  const lines = escapeHtml(md).split("\n");
  const out = [];
  const isTableSep = (l) => l && l.includes("-") && /^\s*\|?[\s:|-]+\|[\s:|-]*$/.test(l);
  const splitRow = (l) => l.replace(/^\s*\|/, "").replace(/\|\s*$/, "").split("|").map((c) => c.trim());
  const isSpecial = (l, next) =>
    /^```/.test(l) || /^(#{1,6})\s/.test(l) || /^\s*[-*+]\s+/.test(l) ||
    /^\s*\d+\.\s+/.test(l) || /^\s*(---|\*\*\*|___)\s*$/.test(l) || /^\s*>\s?/.test(l) ||
    (l.includes("|") && isTableSep(next));
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    let m;
    if (/^```/.test(line)) {
      const buf = []; i++;
      while (i < lines.length && !/^```\s*$/.test(lines[i])) { buf.push(lines[i]); i++; }
      i++;
      out.push("<pre><code>" + buf.join("\n") + "</code></pre>"); continue;
    }
    if ((m = line.match(/^(#{1,6})\s+(.*)$/))) {
      const n = m[1].length; out.push(`<h${n}>` + renderInline(m[2]) + `</h${n}>`); i++; continue;
    }
    if (/^\s*(---|\*\*\*|___)\s*$/.test(line)) { out.push("<hr>"); i++; continue; }
    if (line.includes("|") && isTableSep(lines[i + 1])) {
      const headers = splitRow(line); i += 2; const rows = [];
      while (i < lines.length && lines[i].includes("|") && lines[i].trim() !== "") {
        rows.push(splitRow(lines[i])); i++;
      }
      let t = "<table><thead><tr>" + headers.map((c) => "<th>" + renderInline(c) + "</th>").join("") + "</tr></thead><tbody>";
      for (const r of rows) t += "<tr>" + r.map((c) => "<td>" + renderInline(c) + "</td>").join("") + "</tr>";
      out.push(t + "</tbody></table>"); continue;
    }
    if (/^\s*[-*+]\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*[-*+]\s+/.test(lines[i])) {
        items.push("<li>" + renderInline(lines[i].replace(/^\s*[-*+]\s+/, "")) + "</li>"); i++;
      }
      out.push("<ul>" + items.join("") + "</ul>"); continue;
    }
    if (/^\s*\d+\.\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
        items.push("<li>" + renderInline(lines[i].replace(/^\s*\d+\.\s+/, "")) + "</li>"); i++;
      }
      out.push("<ol>" + items.join("") + "</ol>"); continue;
    }
    if (/^\s*>\s?/.test(line)) {
      const buf = [];
      while (i < lines.length && /^\s*>\s?/.test(lines[i])) { buf.push(lines[i].replace(/^\s*>\s?/, "")); i++; }
      out.push("<blockquote>" + buf.map(renderInline).join("<br>") + "</blockquote>"); continue;
    }
    if (line.trim() === "") { i++; continue; }
    const para = [];
    while (i < lines.length && lines[i].trim() !== "" && !isSpecial(lines[i], lines[i + 1])) {
      para.push(lines[i]); i++;
    }
    out.push("<p>" + para.map(renderInline).join("<br>") + "</p>");
  }
  return out.join("");
}

/**
 * 在容器 DOM 里把 [n] 文本换成可点 sup(引用角标)。
 * 幂等:已装饰的文本节点被 sup 替换后不会再次命中。
 */
export function decorateCitations(container, citations, onCite) {
  const byN = new Map(citations.map((c) => [String(c.n), c]));
  const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT);
  const targets = [];
  let node;
  while ((node = walker.nextNode())) {
    if (node.parentElement.classList.contains("cite")) continue;
    if (/\[\d+\]/.test(node.nodeValue)) targets.push(node);
  }
  for (const textNode of targets) {
    const frag = document.createDocumentFragment();
    let last = 0;
    const re = /\[(\d+)\]/g;
    let m;
    while ((m = re.exec(textNode.nodeValue))) {
      const c = byN.get(m[1]);
      if (!c) continue;
      if (m.index > last) frag.appendChild(document.createTextNode(textNode.nodeValue.slice(last, m.index)));
      const sup = document.createElement("sup");
      sup.className = "cite";
      sup.textContent = "[" + m[1] + "]";
      sup.title = c.section_path || "查看来源";
      sup.addEventListener("click", (e) => { e.stopPropagation(); onCite(sup, c); });
      frag.appendChild(sup);
      last = m.index + m[0].length;
    }
    if (last > 0) {
      if (last < textNode.nodeValue.length) frag.appendChild(document.createTextNode(textNode.nodeValue.slice(last)));
      textNode.parentNode.replaceChild(frag, textNode);
    }
  }
}
