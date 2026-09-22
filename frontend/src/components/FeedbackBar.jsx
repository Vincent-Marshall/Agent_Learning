// 满意度反馈:👍/👎 一次性,点亮选中、另一侧淡出。
// 提交由父组件处理(👎 会把该轮用户原话落低置信池——后端行为,前端静默)。
import React from "react";

const THUMB_UP_SVG = (
  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"/></svg>
);
const THUMB_DOWN_SVG = (
  <svg viewBox="0 0 24 24" fill="currentColor"><path d="M15 3H6c-.83 0-1.54.5-1.84 1.22l-3.02 7.05c-.09.23-.14.47-.14.73v2c0 1.1.9 2 2 2h6.31l-.95 4.57-.03.32c0 .41.17.79.44 1.06L9.83 23l6.59-6.59c.36-.36.58-.86.58-1.41V5c0-1.1-.9-2-2-2zm4 0v12h4V3h-4z"/></svg>
);

export default function FeedbackBar({ rating, onFeedback }) {
  const given = rating || null;
  return (
    <div className="feedback">
      <button
        type="button"
        className={"fb-btn" + (given === "up" ? " active" : "") + (given && given !== "up" ? " dim" : "")}
        aria-label="这条回答有帮助"
        disabled={!!given}
        onClick={() => onFeedback("up")}
      >{THUMB_UP_SVG}</button>
      <button
        type="button"
        className={"fb-btn" + (given === "down" ? " active" : "") + (given && given !== "down" ? " dim" : "")}
        aria-label="这条回答没帮助"
        disabled={!!given}
        onClick={() => onFeedback("down")}
      >{THUMB_DOWN_SVG}</button>
      {given && <span className="fb-done">已反馈，谢谢～</span>}
    </div>
  );
}
