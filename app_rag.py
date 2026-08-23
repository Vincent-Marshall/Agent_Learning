import streamlit as st
from pathlib import Path
import tempfile
import json
import uuid
from datetime import datetime
from ai import chat_stream
from indexer import index_directory
from retriever import retrieve


st.set_page_config(page_title="知识库问答", page_icon=":books:")
st.title("知识库问答助手")


# ----------------会话持久化配置----------------
SESSIONS_DIR = Path("./sessions")
SESSIONS_DIR.mkdir(exist_ok=True)


def save_session(session_id: str, messages: list[dict], title: str = None):
    """保存会话：同时存标题和消息"""
    file = SESSIONS_DIR / f"{session_id}.json"
    payload = {
        "session_id": session_id,
        "title": title if title is not None else "新会话",
        "created_at": datetime.now().isoformat(),
        "messages": messages
    }
    file.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2)
    )


def load_session(session_id: str):
    """读取会话，返回 dict: {session_id,title,created_at,messages}"""
    file = SESSIONS_DIR / f"{session_id}.json"
    if file.exists():
        try:
            data = json.loads(file.read_text())
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    # 兜底空会话
    return {
        "session_id": session_id,
        "title": "新会话",
        "created_at": datetime.now().isoformat(),
        "messages": []
    }


def get_all_sessions():
    """获取全部会话列表，返回[{session_id,title,...}]，兼容旧文件"""
    files = list(SESSIONS_DIR.glob("*.json"))
    res = []
    for f in files:
        try:
            data = json.loads(f.read_text())
            if isinstance(data, dict):
                res.append(data)
        except Exception:
            continue
    # 按创建时间倒序，新会话放最上面，get兜底防止缺少字段
    res.sort(key=lambda x: x.get("created_at", "1970-01-01T00:00:00"), reverse=True)
    return res


def delete_session(session_id: str):
    f = SESSIONS_DIR / f"{session_id}.json"
    if f.exists():
        f.unlink()


def gen_session_title(user_query: str) -> str:
    """调用模型生成简短会话标题，10个字以内，不输出多余内容"""
    prompt = f"把下面用户提问压缩成简短会话标题，最多10个字，不要标点，不要解释，只输出标题：\n{user_query}"
    buf = ""
    for chunk in chat_stream([{"role":"user","content":prompt}]):
        buf += chunk
    t = buf.strip()
    return t[:12] if t else "新会话"


def rewrite_query(raw_query: str) -> str:
    """查询改写：生成更适合向量检索的检索问句，用于RAG召回"""
    rewrite_prompt = f"""将用户问题改写成1条适合知识库检索的查询语句，优化关键词、补全语义，只输出改写后的问题，不要多余解释。
用户原始问题：{raw_query}
"""
    buf = ""
    for chunk in chat_stream([{"role":"user","content":rewrite_prompt}]):
        buf += chunk
    return buf.strip()


RETRIEVE_SCORE_THRESHOLD = 0.6


# ----------------初始化session_state----------------
if "current_session_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    init_messages = [
        {
            "role": "system",
            "content": """你优先使用参考资料内容回答用户问题。
1. 如果参考资料标记【本地知识库没有找到匹配文档】，代表知识库无相关内容，你可以使用自身的知识回答，开头明确提示：> 提示：该回答来自模型内置知识，不在本地文档范围。
2. 如果有参考资料，则严格依据参考资料，禁止编造知识库不存在的事实。
3. 不要无依据拓展无关信息。"""
        }
    ]
    st.session_state.current_session_id = new_id
    st.session_state.messages = init_messages
    st.session_state.session_title = "新会话"
    save_session(new_id, init_messages, title="新会话")


# ----------------侧边栏----------------
with st.sidebar:
    st.header("会话管理")
    all_sessions = get_all_sessions()
    display_options = [f"{item['title']}" for item in all_sessions]
    id_options = [item["session_id"] for item in all_sessions]


    # 新建会话按钮
    if st.button("➕ 新建会话"):
        new_id = str(uuid.uuid4())
        init_messages = [
            {
                "role": "system",
                "content": """你优先使用参考资料内容回答用户问题。
1. 如果参考资料标记【本地知识库没有找到匹配文档】，代表知识库无相关内容，你可以使用自身的知识回答，开头明确提示：> 提示：该回答来自模型内置知识，不在本地文档范围。
2. 如果有参考资料，则严格依据参考资料，禁止编造知识库不存在的事实。
3. 不要无依据拓展无关信息。"""
            }
        ]
        st.session_state.current_session_id = new_id
        st.session_state.messages = init_messages
        st.session_state.session_title = "新会话"
        save_session(new_id, init_messages, title="新会话")


    selected_idx = 0
    if st.session_state.current_session_id in id_options:
        selected_idx = id_options.index(st.session_state.current_session_id)


    selected_display = st.selectbox(
        "历史会话",
        options=display_options,
        index=selected_idx
    )
    real_selected_id = id_options[display_options.index(selected_display)]


    # 切换会话
    if real_selected_id != st.session_state.current_session_id:
        sess_data = load_session(real_selected_id)
        st.session_state.current_session_id = real_selected_id
        st.session_state.messages = sess_data["messages"]
        st.session_state.session_title = sess_data.get("title", "新会话")


    # 删除会话
    if st.button("🗑️ 删除当前会话"):
        delete_session(st.session_state.current_session_id)
        new_id = str(uuid.uuid4())
        init_messages = [
            {
                "role": "system",
                "content": """你优先使用参考资料内容回答用户问题。
1. 如果参考资料标记【本地知识库没有找到匹配文档】，代表知识库无相关内容，你可以使用自身的知识回答，开头明确提示：> 提示：该回答来自模型内置知识，不在本地文档范围。
2. 如果有参考资料，则严格依据参考资料，禁止编造知识库不存在的事实。
3. 不要无依据拓展无关信息。"""
            }]
        st.session_state.current_session_id = new_id
        st.session_state.messages = init_messages
        st.session_state.session_title = "新会话"
        save_session(new_id, init_messages, title="新会话")


    st.divider()
    st.header("知识库")
    uploaded = st.file_uploader(
        "上传文档",
        type=["md", "pdf"],
        accept_multiple_files=True,
    )


    if uploaded and st.button("建立索引"):
        with st.spinner("正在索引..."):
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                for f in uploaded:
                    (tmp_path / f.name).write_bytes(f.getbuffer())
                index_directory(tmp_path)
        st.success(f"已索引 {len(uploaded)} 个文档")


# 渲染聊天历史，跳过system消息
for m in st.session_state.messages:
    if m["role"] == "system":
        continue
    with st.chat_message(m["role"]):
        st.markdown(m["content"])


if user_input := st.chat_input("针对你的文档问我问题"):
    # 如果当前标题是【新会话】，代表第一条消息，生成标题
    if st.session_state.session_title == "新会话":
        with st.spinner("生成会话标题..."):
            new_title = gen_session_title(user_input)
            st.session_state.session_title = new_title

    # ========== 查询改写，使用改写后的query做检索 ==========
    with st.spinner("正在改写查询..."):
        rewritten_q = rewrite_query(user_input)
    hits = retrieve(rewritten_q, top_k=3)

    max_score = max((h["score"] for h in hits), default=0.0)

    # 混合模式：低于阈值不直接stop，给标记，交给模型降级处理
    if max_score < RETRIEVE_SCORE_THRESHOLD:
        context = "【本地知识库没有找到匹配文档】"
        expander_text = "本次检索未命中知识库片段"
    else:
        context = "\n---\n".join(f"[来源:{h['source']}]\n{h['text']}" for h in hits)
        expander_text = "查看引用的文档片段"

    prompt_context_block = f"参考资料：\n{context}\n\n用户问题：{user_input}"

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full = ""
        temp_messages = st.session_state.messages.copy()
        temp_messages[-1] = {"role":"user", "content": prompt_context_block}

        for piece in chat_stream(temp_messages):
            full += piece
            placeholder.markdown(full + "▌")
        placeholder.markdown(full)

        with st.expander(expander_text):
            if max_score >= RETRIEVE_SCORE_THRESHOLD:
                st.caption(f"改写后的检索query：{rewritten_q}")
                for h in hits:
                    st.caption(f"{h['source']}  ·  相似度 {h['score']:.3f}")
                    st.text(h["text"][:300] + "...")
            else:
                st.caption(f"改写后的检索query：{rewritten_q}")
                st.info(f"最高相似度 {max_score:.3f}，低于阈值 {RETRIEVE_SCORE_THRESHOLD}")

    st.session_state.messages.append({"role": "assistant", "content": full})
    save_session(st.session_state.current_session_id, st.session_state.messages, title=st.session_state.session_title)