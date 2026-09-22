// 退款表单弹窗:订单号只读 + 退款原因固定类目下拉,提交调后端写 tickets 表。
import React, { useState } from "react";
import { createRefund, getConversationId } from "../api.js";

const REASONS = ["七天无理由", "质量问题", "发错货", "不想要了", "其他"];

export default function RefundModal({ draft, onClose, onDone }) {
  const [reason, setReason] = useState("");
  const [err, setErr] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async () => {
    if (!reason) { setErr("请选择退款原因"); return; }
    setErr("");
    setSubmitting(true);
    try {
      const data = await createRefund(getConversationId(), draft?.order_id || "", reason);
      onDone(data.ticket_no);
    } catch (e) {
      setErr("退款提交失败，请稍后重试");
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-mask" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="modal">
        <h3>提交退款工单</h3>
        <label>订单号</label>
        <input type="text" value={draft?.order_id || ""} readOnly />
        <label style={{ marginTop: 12 }}>退款原因（必选）</label>
        <select value={reason} onChange={(e) => setReason(e.target.value)}>
          <option value="">请选择退款原因</option>
          {REASONS.map((r) => <option key={r} value={r}>{r}</option>)}
        </select>
        <div className="form-err">{err}</div>
        <div className="modal-actions">
          <button type="button" className="btn btn-ghost" onClick={onClose} disabled={submitting}>取消</button>
          <button type="button" className="btn btn-primary" onClick={submit} disabled={submitting}>
            {submitting ? "提交中…" : "提交退款"}
          </button>
        </div>
      </div>
    </div>
  );
}
