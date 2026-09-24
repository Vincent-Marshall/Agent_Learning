/*
  来源：公众号@小林coding
  后端八股网站：xiaolincoding.com
  Agent网站：xiaolinnote.com
  简历模版：jianli.xiaolinnote.com
*/
/* 后台管理外壳:一份导航挂在所有后台页上(知识库录入 / RAG 评估 / 待审队列 / 观测与成本 /
   主题分布 / 分类器验收)。

   这些页面分属不同章、样式各自内联,所以导航自带样式、自己注入,不去动宿主页的 CSS;
   整个文件包在 IIFE 里,只往 window 上挂两个名字,免得和宿主页的 $ / el 撞名。
   模块入口都是各章原本的路径,导航只是把它们收到一处,不做跳转改写——文档里贴的链接照样能用。 */
(function () {
  const NAV = [
    { href: "/admin", label: "后台首页" },
    { href: "/kb", label: "知识库录入" },
    { href: "/rag-eval", label: "RAG 评估" },
    { href: "/review", label: "飞轮待审" },
    { href: "/observability", label: "观测与成本" },
    { href: "/topics", label: "主题分布" },
    {
      href: "/acceptance", label: "分类器验收",
      children: [
        ["/acceptance", "总览"],
        ["/acceptance/eval", "评测详情"],
        ["/acceptance/data", "数据产物"],
        ["/acceptance/errors", "错例复核"],
      ],
    },
  ];

  // 2026-09-24 改造:导航玻璃化 + 宿主页面毛玻璃主题统一(设计 token 与前端聊天页同源)。
  // 注入时机晚于宿主页内联样式,同优先级下本表生效;宿主页专属类名不受影响。
  const CSS = `
  :root {
    --bg-grad: linear-gradient(135deg, #eef2ff 0%, #fce7f3 45%, #e0f2fe 100%);
    --glass: rgba(255,255,255,.58);
    --glass-strong: rgba(255,255,255,.82);
    --glass-soft: rgba(255,255,255,.35);
    --line: rgba(255,255,255,.65);
    --line-strong: rgba(148,163,184,.28);
    --accent: #6366f1; --accent-deep: #4f46e5;
    --accent-grad: linear-gradient(135deg,#6366f1,#8b5cf6);
    --text: #1e293b; --text-sub: #64748b;
    --shadow: 0 8px 32px rgba(99,102,241,.10), 0 2px 8px rgba(30,41,59,.06);
    --font: "PingFang SC","Microsoft YaHei","Segoe UI",system-ui,-apple-system,sans-serif;
  }

  /* ---- 宿主页面主题 ---- */
  body { background: var(--bg-grad) fixed; font-family: var(--font); color: var(--text); font-size: 13.5px; }
  .wrap {
    max-width: 1120px; margin: 20px auto; padding: 22px;
    background: var(--glass);
    backdrop-filter: blur(22px) saturate(1.5); -webkit-backdrop-filter: blur(22px) saturate(1.5);
    border: 1px solid var(--line); border-radius: 20px; box-shadow: var(--shadow);
  }
  .topbar {
    background: transparent !important; border: none !important;
    box-shadow: none !important; padding: 4px 2px 14px !important;
  }
  .topbar h1, .topbar h2 { color: var(--text) !important; }
  .panel, .card {
    background: var(--glass-strong);
    backdrop-filter: blur(22px) saturate(1.5); -webkit-backdrop-filter: blur(22px) saturate(1.5);
    border: 1px solid var(--line-strong) !important; border-radius: 14px;
    box-shadow: 0 2px 10px rgba(30,41,59,.05);
  }
  table, .tbl {
    border-collapse: collapse; width: 100%; font-size: 12.5px;
  }
  th {
    text-align: left; color: var(--text-sub); font-weight: 500;
    padding: 8px 10px; border-bottom: 1px solid var(--line-strong);
  }
  td { padding: 9px 10px; border-bottom: 1px solid rgba(148,163,184,.14); }
  tr:hover td { background: rgba(255,255,255,.35); }
  .btn, button.btn {
    border: none; border-radius: 12px; padding: 8px 16px;
    font-family: var(--font); font-size: 13px; cursor: pointer;
    background: var(--accent-grad); color: #fff;
    box-shadow: 0 4px 14px rgba(99,102,241,.3);
    text-decoration: none; display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  }
  .btn:hover { filter: brightness(1.06); }
  .btn.go { background: var(--accent-grad); color: #fff; }
  input[type="text"], input[type="number"], textarea, select {
    font-family: var(--font); font-size: 13.5px; color: var(--text);
    background: rgba(255,255,255,.7); border: 1px solid var(--line-strong);
    border-radius: 10px; padding: 8px 12px; outline: none;
  }
  input:focus, textarea:focus, select:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(99,102,241,.15); }
  .pill {
    border-radius: 999px; padding: 3px 10px; font-size: 11.5px;
    border: 1px solid var(--line-strong); background: var(--glass-soft); color: var(--text-sub);
  }
  .pill.info { border-color: rgba(99,102,241,.4); background: rgba(99,102,241,.1); color: var(--accent-deep); }
  .lede, .tip { color: var(--text-sub); font-size: 12.5px; }
  .kv { border-bottom: 1px solid rgba(148,163,184,.14); }

  /* ---- 导航(毛玻璃) ---- */
  .mh-nav { margin-top: 12px; }
  .mh-nav .row {
    display: flex; flex-wrap: wrap; align-items: stretch;
    background: var(--glass-strong);
    backdrop-filter: blur(22px) saturate(1.5); -webkit-backdrop-filter: blur(22px) saturate(1.5);
    border: 1px solid var(--line); border-radius: 14px; box-shadow: var(--shadow);
    overflow: hidden;
  }
  .mh-nav .row a {
    display: flex; align-items: center; gap: 6px; padding: 9px 14px; font-size: 13px;
    text-decoration: none; color: var(--text); border-right: 1px solid var(--line-strong); font-weight: 600;
  }
  .mh-nav .row a:last-child { border-right: 0; }
  .mh-nav .row a:hover { background: rgba(99,102,241,.08); }
  .mh-nav .row a.on { background: var(--accent-grad); color: #fff; }
  .mh-nav .row .brand {
    display: flex; align-items: center; padding: 9px 14px; font-size: 12.5px;
    background: var(--accent-grad); color: #fff; border-right: 1px solid var(--line-strong); letter-spacing: 1px;
  }
  .mh-nav .row .grow { flex: 1; border-right: 1px solid var(--line-strong); }
  .mh-nav .sub {
    display: flex; flex-wrap: wrap; border: 1px solid var(--line); border-top: 0;
    background: var(--glass-soft);
    backdrop-filter: blur(22px) saturate(1.5); -webkit-backdrop-filter: blur(22px) saturate(1.5);
    border-radius: 0 0 14px 14px; overflow: hidden;
  }
  .mh-nav .sub a {
    padding: 6px 12px; font-size: 12px; text-decoration: none; color: var(--text-sub);
    border-right: 1px solid var(--line-strong);
  }
  .mh-nav .sub a:last-child { border-right: 0; }
  .mh-nav .sub a:hover { color: var(--text); background: rgba(255,255,255,.4); }
  .mh-nav .sub a.on { background: var(--glass-strong); color: var(--accent-deep); font-weight: 700; }
  @media (max-width: 640px) { .mh-nav .row .grow { display: none; } }
  `;

  function injectCss() {
    if (document.getElementById("mh-nav-css")) return;
    const s = document.createElement("style");
    s.id = "mh-nav-css";
    s.textContent = CSS;
    document.head.appendChild(s);
  }

  function link(href, label, on, cls) {
    const a = document.createElement("a");
    a.href = href;
    a.className = (on ? "on " : "") + (cls || "");
    a.textContent = label;
    return a;
  }

  /** 当前页归属哪个模块:精确命中优先,其次按前缀(/acceptance/eval 归 /acceptance)。 */
  function moduleOf(active) {
    return NAV.find((m) => m.href === active)
      || NAV.find((m) => m.href !== "/" && active.startsWith(m.href + "/"));
  }

  function renderAdminNav(active) {
    injectCss();
    const wrap = document.createElement("div");
    wrap.className = "mh-nav";
    const row = document.createElement("div");
    row.className = "row";
    const brand = document.createElement("span");
    brand.className = "brand";
    brand.textContent = "后台管理";
    row.appendChild(brand);
    const mod = moduleOf(active);
    for (const m of NAV) row.appendChild(link(m.href, m.label, m === mod));
    const grow = document.createElement("span");
    grow.className = "grow";
    row.appendChild(grow);
    row.appendChild(link("/", "聊天页 →", false));
    wrap.appendChild(row);

    if (mod && mod.children) {
      const sub = document.createElement("div");
      sub.className = "sub";
      for (const [href, label] of mod.children) sub.appendChild(link(href, label, href === active));
      wrap.appendChild(sub);
    }
    return wrap;
  }

  /** 挂到顶栏底下(顶栏是每页自己的标题条);找不到顶栏就摆在 .wrap 最前面。 */
  function mountAdminNav(active) {
    const nav = renderAdminNav(active);
    const bar = document.querySelector(".topbar");
    if (bar && bar.parentNode) bar.parentNode.insertBefore(nav, bar.nextSibling);
    else {
      const w = document.querySelector(".wrap") || document.body;
      w.insertBefore(nav, w.firstChild);
    }
    return nav;
  }

  window.renderAdminNav = renderAdminNav;
  window.mountAdminNav = mountAdminNav;
})();
