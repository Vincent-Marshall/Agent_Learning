from ai import chat, chat_stream

# 一次性拿完整回答
print(chat([{"role": "user", "content": "你好"}]))

# 流式打印
for piece in chat_stream([{"role": "user", "content": "背一首李白的诗"}]):
    print(piece, end="", flush=True)
