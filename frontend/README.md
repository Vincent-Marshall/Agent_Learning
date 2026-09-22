# 聊天页前端（Vite + React）

2026-09-22 起，聊天页由原生 HTML/CSS/JS（像素风）重构为 **Vite + React**（简约毛玻璃风）。
后台各页（/kb、/rag-eval、/review、/observability、/topics、/acceptance）保持原生实现，计划在后续迭代中陆续 React 化。

## 开发

```bash
make frontend-dev     # Vite 热更新 :5173，/api 代理到 FastAPI :8000
```

浏览器打开 http://localhost:5173。

## 构建与部署

```bash
make frontend-build   # 产物 frontend/dist/
```

FastAPI 启动时检测 `frontend/dist/` 存在则托管：`/` 返回 React 聊天页、`/assets/*` 挂载构建产物；
不存在则回落旧版静态聊天页（后端各页不受影响）。

## 目录结构

```
frontend/
  index.html           # Vite 入口
  vite.config.js       # React 插件 + 开发代理(/api → :8000)
  src/
    main.jsx
    App.jsx            # 应用状态:消息流、中断续跑、弹窗、侧栏、反馈
    styles.css         # 设计规范(毛玻璃 token + 全部组件样式)
    api.js             # 后端契约封装:SSE 帧解析 + 各端点
    markdown.jsx       # 零依赖 markdown 渲染器 + 引用角标装饰(自原生版移植)
    components/
      Bubble.jsx           # 消息气泡(用户主色渐变 / 客服浅灰)+ 徽章 + 引用角标
      CitePopover.jsx      # 引用来源浮层
      ChatInput.jsx        # 输入栏(自动增高/回车发送)
      EmptyState.jsx       # 欢迎区 + 建议问题
      ActionBar.jsx        # 转人工/建工单/退款表单按钮
      OrderCards.jsx       # 订单选择器(interrupt → resume)
      TicketConfirmCard.jsx# 工单预览确认卡(interrupt → resume)
      TicketModal.jsx      # 建工单表单弹窗
      RefundModal.jsx      # 退款表单弹窗(订单只读 + 原因下拉)
      FeedbackBar.jsx      # 👍/👎 一次性反馈
      Sidebar.jsx          # 会话列表/切换/新对话
```

## 协议契约（红线，勿改）

与后端 SSE 帧类型一一对应：`delta`（流式 token）、`tool`（工具徽章）、`citations`（知识证据）、
`actions`（转人工/建工单/退款表单）、`interrupt`（订单选择器/工单预览卡，无 done 帧，会话号藏于帧内）、
`done`、`event: error`、`[DONE]` 哨兵。详见 `src/api.js`。

## 设计规范

简约毛玻璃：蓝紫→粉渐变背景、白色玻璃卡片（blur 22px + 白色半透明描边）、主色渐变（#6366f1→#8b5cf6）
用户气泡、浅灰客服气泡、大圆角大留白。全部 token 见 `src/styles.css` 的 `:root`。
