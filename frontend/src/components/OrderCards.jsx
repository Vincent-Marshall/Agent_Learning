// 订单选择器卡片:interrupt(kind=select_order)渲染。
// 点选 → 禁全部卡片、标记 picked、交给 onPick 续跑。
import React, { useState } from "react";

export default function OrderCards({ orders, onPick }) {
  const [picked, setPicked] = useState(null);
  if (!orders || !orders.length) {
    return <div className="bubble-text">没有查到可选订单，请直接提供订单号。</div>;
  }
  return (
    <>
      <div className="bubble-text">请选择您要处理的订单：</div>
      <div className="order-cards">
        {orders.map((o) => (
          <button
            key={o.order_id}
            type="button"
            className={"order-card" + (picked === o.order_id ? " picked" : "")}
            disabled={picked !== null}
            onClick={() => { setPicked(o.order_id); onPick(o); }}
          >
            <div>
              <div className="oc-top">订单 {o.order_id}</div>
              <div className="oc-mid">{o.product || ""}</div>
              <div className="oc-bot">{o.status || ""}</div>
            </div>
            <span className="oc-amount">¥{o.amount ?? ""}</span>
          </button>
        ))}
      </div>
    </>
  );
}
