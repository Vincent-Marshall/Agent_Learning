# MewHelp 电商智能客服 Agent

一个能查订单物流、答政策 FAQ、走退款子流程、挖知识补库的完整电商客服系统。

> **来源声明**：本项目基于课程实战项目 MewHelp 改造（课程授权：源码可用于学习与简历项目）。
> 2026 年 8 月，我在本仓库完成了 Agent 组件的从零学习（RAG → 重排 → 混合检索 → 函数调用 → MCP，见 `previous/`）；
> 自 2026-09-19 起进入「整合改造期」：将组件级认知整合进完整的客服系统，并持续改造（见下方改造历程）。

## 技术栈

Python 3.12 + FastAPI + LangGraph / LangChain + SQLAlchemy / MySQL + Milvus

- 聊天：DeepSeek（OpenAI 兼容协议直连）
- 嵌入 / 重排：硅基流动（BGE-M3 / bge-reranker-v2-m3）
- 向量库：Milvus Standalone（dense + 原生 BM25）
- 部署：Docker Compose 全栈编排

## 系统架构

```
聊天页(SSE) → 指代消解 → 意图识别(九类) → 分流
  ├ 闲聊/其他   → 固定话术（零模型调用）
  ├ 投诉       → 安抚话术 + 转人工/建工单按钮（不进 Agent）
  ├ 商品咨询    → 强制检索 → 生成前证据闸 → 强: Agent / 弱: 拒答落池
  ├ 物流/订单   → 主力 Agent（ReAct 循环，步数封顶）
  └ 退款退货    → 退款子流程：订单选择器(interrupt/resume) → 政策检索 → Agent 判能不能退
```

设计要点：

- **Workflow + Agent 混合**：确定性骨架管稳定可控可观测，主力 Agent 管组合多变的灵活业务
- **RAG 检索管线**：结构化切块 → 双写 MySQL（权威源）+ Milvus（读模型）→ 混合检索（RRF 融合）+ 精排
- **防幻觉体系**：prompt 约束 + 结构化输出 + 生成前置信度闸 + 自评闸 + 拒答落低置信池
- **工程可靠性**：双写幂等（崩溃重跑自愈）、工具写操作「提议-执行」分离、fail-closed/fail-open 分级容错

## 8 月踩过的坑 → 本项目里的生产级答案

| 8 月组件学习时踩的坑 | 本项目中的对应设计 |
| --- | --- |
| 向量相似度分数被当成 reranker 分数 | 生成前证据闸按 rerank 分判，多信号加权口径分明 |
| BM25 中文用 `.split()` 分词完全失效 | Milvus 原生 BM25 + chinese analyzer |
| MCP stdio 死锁 | MCP 服务改走 HTTP transport |
| 硬阈值一刀切导致全部结果被拦 | 机械闸 + 语义闸分层，拒答落池进数据飞轮 |

（学习过程完整记录见 `previous/learning-notes.md`）

## 目录结构

```
app/              # 应用主体：api / graph(LangGraph 图) / core / kb / tools / db / schemas / static
frontend/         # 聊天页前端（Vite + React，毛玻璃风；构建产物由 FastAPI 托管）
mcp_servers/      # 物流 / 售后 MCP 服务（独立进程，HTTP transport）
scripts/          # 建库、评估、训练等离线脚本
sql/              # 建表与种子数据
tests/            # 单测（不打真实模型）
data/kb/          # 电商知识库源文档
docs/superpowers/ # 各章 spec/plan 设计文档（课程实战篇流程范本）
previous/         # 2026-08 组件学习历程（rag / tools / mcp / streamlit-demo / materials）
```

## 快速开始

```bash
cp .env.example .env      # 填 CHAT_* / EMBED_* / RERANK_* 三组
docker compose up -d      # MySQL + Milvus
make seed                 # 灌业务测试数据
make dev                  # 应用 :8000 + MCP :8101/:8102
```

浏览器打开 <http://localhost:8000> 即聊天页。

## 改造历程（持续更新）

- **2026-08**：Agent 组件从零学习（RAG/重排/混合检索/查询改写/函数调用/工具循环/MCP/会话持久化），见 `previous/`
- **2026-09-19**：开始整合改造
  - [x] 归档学习历程至 `previous/`，重组仓库结构
  - [x] 接入电商知识库源文档与建表种子数据
  - [x] 接入知识切块与双写向量化管线，跑通基线
  - [x] 接入 LangGraph 编排骨架与工具系统（DeepSeek 适配，含结构化输出兼容性修复）
  - [x] 接入应用入口，跑通单测（469 通过）与聊天页全链路验证
  - [x] 接入数据飞轮与可观测模块（批处理工具链 + Langfuse 编排适配）
  - [x] 接入各章评估脚本与设计文档，跑通评估：意图 18/18、指代消解 3/3、Query 扩写 3/3、检索 3/5（2 例换说法漏召回，留作调优线索）
  - [x] 前端重构：聊天页 React 化（Vite + 简约毛玻璃，SSE 协议不变；后台页留待后续迭代）
  - [ ] 部署上线

## 授权

项目源码基于 MewHelp 课程实战项目（课程授权：源码可用于学习与简历项目）。`previous/` 为本人 2026 年 8 月的组件学习记录。
