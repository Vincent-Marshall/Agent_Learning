// 聊天页应用:消息流 / SSE 流式渲染 / 动作按钮 / 中断续跑 / 表单弹窗 / 会话侧栏 / 反馈。
import React, { useCallback, useEffect, useRef, useState } from "react";
import Bubble from "./components/Bubble.jsx";
import ChatInput from "./components/ChatInput.jsx";
import CitePopover from "./components/CitePopover.jsx";
import EmptyState from "./components/EmptyState.jsx";
import ActionBar from "./components/ActionBar.jsx";
import OrderCards from "./components/OrderCards.jsx";
import TicketConfirmCard from "./components/TicketConfirmCard.jsx";
import TicketModal from "./components/TicketModal.jsx";
import RefundModal from "./components/RefundModal.jsx";
import FeedbackBar from "./components/FeedbackBar.jsx";
import Sidebar from "./components/Sidebar.jsx";
import {
  chatStream, resumeStream, readSSEStream, sendFeedback,
  loadConversations, loadMessages,
  getConversationId, setConversationId, clearConversationId,
} from "./api.js";

// 历史回载时补挂按钮:话术与后端 prompts.py 的固定文案精确匹配(单一来源在后端)。
const REPLAY_ACTIONS = [
  { text: "抱歉,这个问题我暂时没有查到确切信息,不敢乱答。建议您联系人工客服进一步确认,以免给您错误的指引。",
    actions: [{ type: "transfer_human" }] },
  { text: "非常抱歉给您带来了不好的体验,我理解您的心情。您可以选择转接人工客服,或让我为您登记一张工单跟进处理。",
    actions: [{ type: "transfer_human" }, { type: "create_ticket", draft: {} }] },
];

export default function App() {
  const [messages, setMessages] = useState([]);
  const [busy, setBusy] = useState(false);
  const [cite, setCite] = useState(null);        // { citation, anchorEl }
  const [convs, setConvs] = useState([]);
  const [convId, setConvIdState] = useState(getConversationId());
  const [modal, setModal] = useState(null);      // { type, msgId, draft? }
  const msgsRef = useRef(null);
  const busyRef = useRef(false);                 // send 的异步闭包用,避免依赖 busy state

  const setConvId = useCallback((id) => {
    setConversationId(id);
    setConvIdState(id);
  }, []);

  const refreshConvs = useCallback(async () => {
    try { setConvs(await loadConversations()); } catch (e) { /* 侧栏失败不影响聊天 */ }
  }, []);

  useEffect(() => { refreshConvs(); }, [refreshConvs]);

  useEffect(() => {
    const el = msgsRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  const updateLastBot = useCallback((fn) => {
    setMessages((prev) => {
      const next = [...prev];
      for (let i = next.length - 1; i >= 0; i--) {
        if (next[i].role === "bot") { next[i] = fn(next[i]); break; }
      }
      return next;
    });
  }, []);

  const patchMessage = useCallback((id, fn) => {
    setMessages((prev) => prev.map((m) => (m.id === id ? fn(m) : m)));
  }, []);

  const appendBot = useCallback((text, extra = {}) => {
    setMessages((prev) => [...prev, { id: String(Date.now()), role: "bot", text, badges: [], citations: [], actions: [], ...extra }]);
  }, []);

  // 一段 SSE 流的通用流程:可选加一条用户气泡,开客服占位气泡,逐帧渲染,收尾刷新侧栏
  const runStream = useCallback(async (fetchFn, userText) => {
    if (busyRef.current) return;
    busyRef.current = true;
    setBusy(true);
    const id = String(Date.now());
    setMessages((prev) => [
      ...prev,
      ...(userText ? [{ id: id + "-u", role: "user", text: userText }] : []),
      { id: id + "-b", role: "bot", text: "", badges: [], citations: [], actions: [], streaming: true },
    ]);
    try {
      const resp = await fetchFn();
      await readSSEStream(resp, {
        delta: (d) => updateLastBot((m) => ({ ...m, text: m.text + d })),
        tool: (name) => updateLastBot((m) => ({ ...m, badges: [...m.badges, name] })),
        citations: (items) => updateLastBot((m) => ({ ...m, citations: items })),
        actions: (items) => updateLastBot((m) => ({ ...m, actions: items })),
        interrupt: (data) => updateLastBot((m) => ({ ...m, interrupt: data })),
      });
    } catch (e) {
      updateLastBot((m) => ({ ...m, error: true, text: "回复失败，请稍后重试" }));
    } finally {
      updateLastBot((m) => ({ ...m, streaming: false }));
      busyRef.current = false;
      setBusy(false);
      setConvId(getConversationId());
      refreshConvs();   // 每轮后刷新侧栏(新会话入列/摘要标记更新)
    }
  }, [updateLastBot, setConvId, refreshConvs]);

  const send = useCallback((text) => {
    runStream(() => chatStream(text, getConversationId()), text);
  }, [runStream]);

  // 订单点选续跑 / 工单预览确认续跑
  const resumeOrder = useCallback((o) => {
    runStream(
      () => resumeStream(getConversationId(), { order_id: o.order_id }),
      `选择订单 ${o.order_id}`,
    );
  }, [runStream]);

  const resumeConfirm = useCallback((confirmed) => {
    runStream(
      () => resumeStream(getConversationId(), { confirmed }),
      confirmed ? "确认提交工单" : "取消建单",
    );
  }, [runStream]);

  // 转人工:纯前端模拟(后端不接真人系统)
  const transferHuman = useCallback((msgId) => {
    patchMessage(msgId, (m) => ({ ...m, doneActions: [...(m.doneActions || []), "transfer_human"] }));
    appendBot("已转接人工客服");
    appendBot("您好，我是客服小猫，请问有什么可以帮您的");
  }, [patchMessage, appendBot]);

  // 工单建成 / 退款提交完成
  const onTicketDone = useCallback((msgId, ticketNo) => {
    patchMessage(msgId, (m) => ({ ...m, doneActions: [...(m.doneActions || []), "create_ticket"] }));
    appendBot(`工单已创建：${ticketNo}`);
    setModal(null);
  }, [patchMessage, appendBot]);

  const onRefundDone = useCallback((msgId, ticketNo) => {
    patchMessage(msgId, (m) => ({ ...m, doneActions: [...(m.doneActions || []), "refund_form"] }));
    appendBot(`退款申请已提交：${ticketNo}`);
    setModal(null);
  }, [patchMessage, appendBot]);

  // 👍/👎:一次性,后端静默落池(👎)/记日志(👍)
  const onFeedback = useCallback((msgId, rating) => {
    let question = "";
    setMessages((prev) => {
      // 找该气泡之前最近的用户消息
      for (let i = 0; i < prev.length; i++) {
        if (prev[i].id === msgId) {
          for (let j = i - 1; j >= 0; j--) {
            if (prev[j].role === "user") { question = prev[j].text || ""; break; }
          }
          break;
        }
      }
      return prev.map((m) => (m.id === msgId ? { ...m, feedback: rating } : m));
    });
    sendFeedback(getConversationId(), rating, question);
  }, []);

  // 会话切换:回载历史,按固定文案补挂按钮
  const switchConversation = useCallback(async (cid) => {
    if (cid === convId && messages.length) return;
    setConvId(cid);
    try {
      const items = await loadMessages(cid);
      const rebuilt = [];
      for (const m of items) {
        if (!m.content) continue;
        if (m.role === "user") {
          rebuilt.push({ id: "h" + m.id + "-u", role: "user", text: m.content });
        } else {
          const hit = REPLAY_ACTIONS.find((ra) => m.content.trim() === ra.text);
          rebuilt.push({
            id: "h" + m.id + "-b", role: "bot", text: m.content,
            badges: [], citations: [], actions: hit ? hit.actions : [], feedback: null,
          });
        }
      }
      setMessages(rebuilt);
    } catch (e) { /* 历史加载失败仍可继续聊 */ }
    refreshConvs();
  }, [convId, messages.length, setConvId, refreshConvs]);

  const newChat = useCallback(() => {
    clearConversationId();
    setConvIdState(null);
    setMessages([]);
    refreshConvs();
  }, [refreshConvs]);

  const onCite = useCallback((anchorEl, citation) => setCite({ citation, anchorEl }), []);

  return (
    <div className="app-shell">
      <Sidebar convs={convs} currentId={convId} onSwitch={switchConversation} onNewChat={newChat} />
      <main className="chat-main glass">
        <header className="chat-head">
          <div className="agent-name"><span className="dot" /> 客服小喵 · 在线</div>
          <span className="ci-preview">喵喵优选 · 智能客服</span>
        </header>
        <div className="msgs" ref={msgsRef}>
          {messages.length === 0 && <EmptyState busy={busy} onPick={send} />}
          {messages.map((m) => {
            return (
              <Bubble key={m.id} msg={m} onCite={onCite}>
                {m.role === "bot" && !m.error && (
                  <>
                    {m.interrupt && m.interrupt.kind === "confirm_ticket" && (
                      <TicketConfirmCard preview={m.interrupt.preview || {}} onConfirm={resumeConfirm} />
                    )}
                    {m.interrupt && m.interrupt.kind !== "confirm_ticket" && (
                      <OrderCards orders={m.interrupt.orders || []} onPick={resumeOrder} />
                    )}
                    {!m.interrupt && (m.actions?.length > 0) && (
                      <ActionBar
                        msg={m}
                        onTransfer={transferHuman}
                        onTicket={(mid) => setModal({ type: "ticket", msgId: mid })}
                        onRefund={(mid, draft) => setModal({ type: "refund", msgId: mid, draft })}
                      />
                    )}
                    {!m.interrupt && m.text && !m.streaming && (
                      <FeedbackBar rating={m.feedback} onFeedback={(r) => onFeedback(m.id, r)} />
                    )}
                  </>
                )}
              </Bubble>
            );
          })}
        </div>
        <ChatInput busy={busy} onSend={send} />
      </main>
      <CitePopover
        citation={cite?.citation || null}
        anchorEl={cite?.anchorEl || null}
        onClose={() => setCite(null)}
      />
      {modal?.type === "ticket" && (
        <TicketModal
          onClose={() => setModal(null)}
          onDone={(no) => onTicketDone(modal.msgId, no)}
        />
      )}
      {modal?.type === "refund" && (
        <RefundModal
          draft={modal.draft}
          onClose={() => setModal(null)}
          onDone={(no) => onRefundDone(modal.msgId, no)}
        />
      )}
    </div>
  );
}
