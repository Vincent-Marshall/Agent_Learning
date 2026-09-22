// 建工单表单弹窗:类别必选(不预选)+ 描述必填,提交调后端写 tickets 表。
import React, { useState } from "react";
import { createTicket, getConversationId } from "../api.js";

export default function TicketModal({ onClose, onDone }) {
  const [type, setType] = useState("");
  const [desc, setDesc] = useState("");
  const [err, setErr] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async () => {
    if (!type) { setErr("请选择反馈类别"); return; }
    if (!desc.trim()) { setErr("请填写反馈描述"); return; }
    setErr("");
    setSubmitting(true);
    try {
      const data = await createTicket(getConversationId(), desc.trim(), type);
      onDone(data.ticket_no);
    } catch (e) {
      setErr("工单创建失败，请稍后重试");
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-mask" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="modal">
        <h3>创建工单</h3>
        <label>反馈类别（必选）</label>
        <select value={type} onChange={(e) => setType(e.target.value)}>
          <option value="">请选择类别</option>
          <option value="售后">售后</option>
          <option value="投诉">投诉</option>
          <option value="咨询">咨询</option>
        </select>
        <label style={{ marginTop: 12 }}>反馈描述（必填）</label>
        <textarea
          value={desc}
          onChange={(e) => setDesc(e.target.value)}
          placeholder="请描述您遇到的问题…"
          autoFocus
        />
        <div className="form-err">{err}</div>
        <div className="modal-actions">
          <button type="button" className="btn btn-ghost" onClick={onClose} disabled={submitting}>取消</button>
          <button type="button" className="btn btn-primary" onClick={submit} disabled={submitting}>
            {submitting ? "提交中…" : "提交工单"}
          </button>
        </div>
      </div>
    </div>
  );
}
