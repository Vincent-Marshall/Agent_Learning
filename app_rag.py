# app_rag.py
import streamlit as st
from pathlib import Path
import tempfile
from ai import chat_stream
from indexer import index_directory
from retriever import retrieve

st.set_page_config(page_title="知识库问答", page_icon=":books:")
st.title("知识库问答助手")

# 侧边栏：文件上传和索引
with st.sidebar:
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

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "你基于给定的参考资料回答问题，不知道就说不知道。"}
    ]

for m in st.session_state.messages:
    if m["role"] == "system":
        continue
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if user_input := st.chat_input("针对你的文档问我问题"):
    # 先做 RAG 检索
    hits = retrieve(user_input, top_k=3)
    context = "\n---\n".join(f"[来源:{h['source']}]\n{h['text']}" for h in hits)
    augmented = f"参考资料：\n{context}\n\n问题：{user_input}"

    st.session_state.messages.append({"role": "user", "content": augmented})
    with st.chat_message("user"):
        st.markdown(user_input)  # UI 只显示原问题

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full = ""
        for piece in chat_stream(st.session_state.messages):
            full += piece
            placeholder.markdown(full + "▌")
        placeholder.markdown(full)

        # 展示引用来源
        with st.expander("查看引用的文档片段"):
            for h in hits:
                st.caption(f"{h['source']}  ·  相似度 {h['score']:.3f}")
                st.text(h["text"][:300] + "...")

    st.session_state.messages.append({"role": "assistant", "content": full})
