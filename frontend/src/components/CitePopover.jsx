// 引用浮层:点击角标后展示来源(section_path + 问法 + 原文 + 元信息)。
// 定位逻辑与原版一致:角标下方,超出视口右/下边则回收。
import React, { useEffect, useRef } from "react";
import { escapeHtml } from "../markdown.jsx";

export default function CitePopover({ citation, anchorEl, onClose }) {
  const popRef = useRef(null);

  useEffect(() => {
    if (!citation || !anchorEl || !popRef.current) return;
    const pop = popRef.current;
    const r = anchorEl.getBoundingClientRect();
    const pw = Math.min(320, window.innerWidth - 24);
    pop.style.width = pw + "px";
    let left = Math.min(r.left, window.innerWidth - pw - 12);
    let top = r.bottom + 6;
    if (top + pop.offsetHeight > window.innerHeight - 12) {
      top = Math.max(12, r.top - pop.offsetHeight - 6);
    }
    pop.style.left = Math.max(12, left) + "px";
    pop.style.top = top + "px";

    const outside = (e) => {
      if (popRef.current && !popRef.current.contains(e.target)) onClose();
    };
    const esc = (e) => { if (e.key === "Escape") onClose(); };
    const resize = () => onClose();
    document.addEventListener("click", outside);
    document.addEventListener("keydown", esc);
    window.addEventListener("resize", resize);
    return () => {
      document.removeEventListener("click", outside);
      document.removeEventListener("keydown", esc);
      window.removeEventListener("resize", resize);
    };
  }, [citation, anchorEl, onClose]);

  if (!citation) return null;
  return (
    <div ref={popRef} className="cite-pop">
      <div className="cite-pop-path">{escapeHtml(citation.section_path || "来源")}</div>
      {citation.question && <div className="cite-pop-q">{escapeHtml(citation.question)}</div>}
      <div className="cite-pop-a">{escapeHtml(citation.answer || "")}</div>
      <div className="cite-pop-meta">
        来源编号 [{citation.n}]
        {citation.content_type ? ` · ${escapeHtml(citation.content_type)}` : ""}
      </div>
    </div>
  );
}
