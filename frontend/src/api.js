// 后端契约封装:SSE 帧解析 + 各端点请求。
// 帧类型与 /api/chat、/api/actions/resume 的后端实现一一对应(协议层,勿改)。

const SESSION_KEY = "mewhelp_user_id";
const CONV_KEY = "mewhelp_conv_id";

// crypto.randomUUID 仅在安全上下文(HTTPS/localhost)可用;公网 http://IP 直连时
// 未定义,直接调用会抛 TypeError。这里做降级生成,两种环境都稳。
function genUserId() {
  if (window.crypto && typeof window.crypto.randomUUID === "function") {
    return window.crypto.randomUUID();
  }
  return "u-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 10);
}

export function getUserId() {
  let id = localStorage.getItem(SESSION_KEY);
  if (!id) {
    id = genUserId();
    localStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

export function getConversationId() {
  const v = localStorage.getItem(CONV_KEY);
  return v ? Number(v) : null;
}

export function setConversationId(id) {
  if (id != null) localStorage.setItem(CONV_KEY, String(id));
}

export function clearConversationId() {
  localStorage.removeItem(CONV_KEY);
}

/**
 * 读一条 SSE 流,按帧分发到 handlers:
 *   handlers.delta(text)            最终回答的 token 片段
 *   handlers.tool(name)             工具调用帧
 *   handlers.citations(items)       知识证据(编号→来源)
 *   handlers.actions(items)         转人工/建工单/退款表单等动作
 *   handlers.interrupt(data)        中断帧(kind=select_order|confirm_ticket),带 conversation_id
 * done 帧自动记录 conversation_id;event: error 抛异常。
 */
export async function readSSEStream(resp, handlers) {
  if (!resp.ok || !resp.body) throw new Error("bad response");
  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const frames = buffer.split("\n\n");
    buffer = frames.pop() ?? "";
    for (const frame of frames) {
      if (frame.startsWith("event: error")) throw new Error("stream error");
      const line = frame.split("\n").find((l) => l.startsWith("data: "));
      if (!line) continue;
      const payload = line.slice(6);
      if (payload === "[DONE]") return;
      const data = JSON.parse(payload);
      if (data.event === "tool") handlers.tool && handlers.tool(data.name);
      else if (data.event === "citations") handlers.citations && handlers.citations(data.items || []);
      else if (data.event === "interrupt") {
        // 中断无 done 帧,会话号靠 interrupt 帧带回,续跑要用
        if (data.conversation_id) setConversationId(data.conversation_id);
        handlers.interrupt && handlers.interrupt(data);
      } else if (data.event === "actions") handlers.actions && handlers.actions(data.items || []);
      else if (data.event === "done") setConversationId(data.conversation_id);
      else if (data.delta !== undefined) handlers.delta && handlers.delta(data.delta);
    }
  }
}

/** 发起一轮聊天(或续跑),返回 fetch 的响应交给 readSSEStream 消费。 */
export function chatStream(message, conversationId) {
  return fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: getUserId(), message, conversation_id: conversationId }),
  });
}

/** 中断续跑:订单点选回 order_id;工单预览卡回 confirmed。 */
export function resumeStream(conversationId, resumeValue) {
  return fetch("/api/actions/resume", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conversation_id: conversationId, ...resumeValue }),
  });
}

export async function createTicket(conversationId, description, ticketType) {
  const resp = await fetch("/api/actions/create-ticket", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conversation_id: conversationId, description, ticket_type: ticketType }),
  });
  const data = await resp.json();
  if (!resp.ok) throw new Error(data.detail || "创建失败");
  return data;
}

export async function createRefund(conversationId, orderId, reason) {
  const resp = await fetch("/api/actions/create-refund", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conversation_id: conversationId, order_id: orderId, reason }),
  });
  const data = await resp.json();
  if (!resp.ok) throw new Error(data.detail || "提交失败");
  return data;
}

/** 👍/👎 反馈:👎 会把该轮用户原话落低置信池(后端行为,前端静默)。 */
export function sendFeedback(conversationId, rating, question) {
  return fetch("/api/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conversation_id: conversationId, rating, question }),
  }).catch(() => {});
}

export async function loadConversations() {
  const r = await fetch("/api/conversations?user_id=" + encodeURIComponent(getUserId()));
  if (!r.ok) return [];
  return ((await r.json()).items) || [];
}

export async function loadMessages(conversationId) {
  const r = await fetch(`/api/conversations/${conversationId}/messages`);
  if (!r.ok) return [];
  return ((await r.json()).items) || [];
}
