import streamlit as st
from ai import chat_stream, DEFAULT_MODEL  # 沿用 02 篇封装

st.set_page_config(page_title="Python AI 聊天助手", page_icon=":robot_face:")
st.title("Python AI 聊天助手")

# ========== 把示例代码粘贴在这里 ==========
# 缓存一个 embedding 模型，避免每次交互都重新加载
@st.cache_resource
def load_embedder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("BAAI/bge-m3")

embedder = load_embedder()  # 第一次真的加载，后续直接拿缓存
# ========================================


# session_state 是 Streamlit 存持久状态的地方，每个用户会话独立
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "你是一位简洁专业的 Python 助手。"}
    ]


# 把历史消息渲染出来（跳过 system）
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# 底部输入框
if user_input := st.chat_input("有什么我可以帮你的？"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)


    # 流式渲染助手回复
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full = ""
        for piece in chat_stream(st.session_state.messages):
            full += piece
            placeholder.markdown(full + "▌")  # 光标效果
        placeholder.markdown(full)


    st.session_state.messages.append({"role": "assistant", "content": full})


with st.sidebar:
    st.header("设置")

    model = st.selectbox(
        "模型",
        ["deepseek-chat", "deepseek-reasoner", "qwen2.5:7b"],
        index=0,
    )

    temperature = st.slider("temperature", 0.0, 2.0, 0.7, 0.1)

    if st.button("清空对话"):
        st.session_state.messages = [st.session_state.messages[0]]  # 保留 system
        st.rerun()
