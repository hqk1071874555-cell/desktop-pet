# 方案 B：Live2D 看板娘 — 优秀参考手册

> 专为 Tauri + React + Live2D + AI 技术栈整理

---

## 一、核心参考项目（4 个）

### 1. Hiyori — 最匹配你技术栈的完整项目 ⭐⭐⭐⭐⭐

| 项 | 详情 |
|---|------|
| **GitHub** | https://github.com/devjiro76/hiyori |
| **Stars** | 2（新项目，质量高） |
| **技术栈** | Tauri v2 + React 19 + PixiJS 6 + OpenAI API + SQLite |
| **平台** | macOS（Windows/Linux 计划中） |
| **许可证** | MIT |

**为什么是最佳参考：**
- 技术栈跟你一模一样：Tauri v2 + React 19 + TypeScript
- 实现了完整的 Live2D 桌面伴侣：渲染 + 交互 + AI 对话 + 情感系统
- 代码语言占比 TS 88.3%，Rust 3.7%，前端为主
- 结构清晰：`src-tauri/` Rust 后端 + `src/` React 前端

**核心功能清单：**

| 功能 | 实现方式 |
|------|----------|
| 👁️ 眼球追踪 | 鼠标位置 → Live2D 眼睛参数实时跟随 |
| 😊 情感反应 | LLM 回复含 VAD 情感数据 → 映射 Live2D 表情 |
| 💬 AI 对话 | OpenAI 兼容 API（支持 OpenAI/Anthropic/Google/Groq/Ollama） |
| 🖥️ 桌面代理 | 自然语言操控：打开应用、运行命令、管理剪贴板、发通知 |
| 🎭 角色动画 | 呼吸、物理模拟（头发摆动）、空闲动画 |
| 💾 聊天记忆 | SQLite 本地存储聊天历史 |
| 🔑 隐私安全 | API Key 仅存本地，不离开用户设备 |

**架构流程：**
```
用户聊天 → LLM (用户自己的Key)
              ↓
         回复 + JSON情感数据 {valence, arousal, dominance}
              ↓
         Hiyori 应用
         ├── 情感 → Live2D 表情映射
         ├── PixiJS 渲染器（眼追踪/物理/空闲动画）
         ├── 桌面工具（Shell/剪贴板/通知）
         └── SQLite 聊天记录
```

**目录结构（可直接参考）：**
```
hiyori/
├── src-tauri/        # Rust: 窗口管理、系统交互、API代理
├── src/              # React: UI组件、Live2D渲染、聊天界面
├── .env.example      # API Key 配置模板
├── index.html
├── vite.config.ts
└── package.json
```

---

### 2. tauri-live2d — 仅 5MB 的轻量方案 ⭐⭐⭐⭐

| 项 | 详情 |
|---|------|
| **GitHub** | https://github.com/Chenshennan/tauri-live2d |
| **Stars** | 0（Fork 自 itxve/tauri-live2d） |
| **技术栈** | Tauri + Vue 3 + PixiJS + Vite |
| **包体积** | 仅 ~5MB（vs Electron 近百 MB） |

**为什么值得参考：**
- 证明了 Tauri + Live2D 可以做到极简体积
- 支持 Cubism v2 和 v3 两种模型格式
- 同时支持本地模型加载和远程 URL 加载
- 透明无边框窗口的 Tauri 配置可以照搬

**功能清单：**
- ✅ 基于 PixiJS 加载 Live2D 模型（v2/v3）
- ✅ 本地模型加载（放入指定目录）
- ✅ 远程模型加载（URL 动态获取）
- ✅ 大小缩放
- ✅ 开机自启动
- ✅ 透明无边框窗口
- ⚠️ macOS 下有窗口虚线问题（已知 bug）

**关键配置参考（透明窗口）：**
```json
// src-tauri/tauri.conf.json
{
  "windows": [{
    "label": "live2d",
    "decorations": false,   // 无边框
    "transparent": true,    // 透明
    "alwaysOnTop": true,    // 置顶
    "width": 400,
    "height": 400
  }]
}
```

---

### 3. desktop-live2d-previewer — Live2D 模型查看器 ⭐⭐⭐

| 项 | 详情 |
|---|------|
| **GitHub** | https://github.com/kian-lian/desktop-live2d-previewer |
| **技术栈** | Tauri 2 + React 19 + TS + PixiJS 6 + pixi-live2d-display 0.4 + shadcn/ui |

**核心参考价值：**
- React 19 + Tauri 2 的同版本组合，代码直接可参考
- `use-live2d.ts` Hook 是 Live2D 加载逻辑的教科书级写法
- 8 个预置角色模型（Haru、Mao 等），直接可跑
- 支持眼追踪、点击互动、表情切换、动作播放

**关键代码文件：**
```
src/
├── hooks/
│   └── use-live2d.ts        # 核心！模型加载、交互、眼追踪
├── components/
│   ├── live2d-canvas.tsx    # Live2D 画布容器
│   └── live2d-sidebar.tsx   # 控制面板
├── lib/
│   └── live2d-config.ts     # 模型列表配置
```

---

### 4. Verdent 7 天实战 — 最详细的工程记录 ⭐⭐⭐⭐⭐

| 项 | 详情 |
|---|------|
| **来源** | https://www.verdent.ai/zh-CN/use-cases/desktop-companion-built-in-7-days |
| **技术栈** | Tauri 2 + React + TS + PixiJS 6 + Cubism 4 + Rust WebSocket |

**7 天逐日推进记录：**

```
Day 1 → 脚手架搭建（版本锁定 PIXI v6 + pixi-live2d-display 0.4）
Day 2 → macOS 透明无边框窗口（Rust 调用 NSWindow 原生 API）
Day 3 → Live2D 角色渲染 + 呼吸/眨眼/头部追踪/身体摇摆
Day 4 → WebSocket 控制 API（127.0.0.1:8765，9种消息类型）
Day 5 → 状态推断引擎（纯规则，监控任务状态→表情映射）
Day 6 → 热插拔 Live2D 模型
Day 7 → 跨平台路径解析与最终打磨
```

**完整踩坑清单（直接省时间）：**

| 坑 | 症状 | 解决 |
|----|------|------|
| PIXI v7 不兼容 | pixi-live2d-display 报错 | 锁定 `pixi.js@6` |
| Tauri 2 API 路径 | import 找不到 | v2 用 `@tauri-apps/api/core` |
| 模型冻结无响应 | 角色完全不动 | 调用 `registerTicker(PIXI.Ticker)` |
| 全局 PIXI 缺失 | 内部引用 window.PIXI 失败 | 显式 `window.PIXI = PIXI` |
| macOS 透明有阴影 | 窗口边缘有虚线/阴影 | 用 Rust 调 NSWindow 原生 API |
| 热切换纹理残留 | 旧模型纹理叠加 | URL 加 `?v=` + React `key` |
| 路径硬编码 | 仅支持 macOS | 编译时 `#[cfg]` 按平台分支 |

---

## 二、免费 Live2D 模型资源

### 2.1 官方免费示例（7 个）

| 模型 | 风格 | 特点 |
|------|------|------|
| **Hiyori Momose** | 日系少女 | 标准模型，表情丰富，最推荐入门 |
| **Haru** | 日系少女 | 接待员风格，含问候动画，广为人知 |
| **Mao** | 日系少女 | 颜色混合示例，活泼可爱 |
| **Kei** | 日系少年 | 含唇形同步音频文件 |
| **Hatsune Miku** | 初音未来 | 双马尾 Skinning 效果，知名度高 |
| **Epsilon** | 日系少女 | 含眼泪/愤怒等丰富表情 |
| **Mark-kun** | 简约男孩 | 极简结构 + PSD 源文件，学习用 |

📥 下载：https://www.live2d.com/en/learn/sample/
⚠️ 需同意 Free Material License Agreement，学习/非商业免费

### 2.2 社区模型仓库（大量）

| 仓库 | 地址 | 模型数 |
|------|------|--------|
| **Eikanya/Live2d-model** | github.com/Eikanya/Live2d-model | 大量游戏角色 |
| **imuncle/live2d** | github.com/imuncle/live2d | 多个角色 |
| **oh-my-live2d/live2d-models** | github.com/oh-my-live2d/live2d-models | Pio、仙狐、黑猫等 |
| **guansss/pixi-live2d-display** | github.com/guansss/pixi-live2d-display | 测试用 shizuku/haru |
| **zenghongtu/live2d-model-assets** | github.com/zenghongtu/live2d-model-assets | tauri-live2d 推荐 |

### 2.3 最推荐的入门模型组合

| 用途 | 推荐模型 | 理由 |
|------|----------|------|
| 开发调试 | shizuku | 最简模型，pixi-live2d-display 自带 |
| 正式展示 | Hiyori Momose | 官方标准模型，表情丰富 |
| 高知名度 | Hatsune Miku | 初音未来，面试官也可能认识 |
| 可爱风 | cat-black（黑猫） | oml2d 提供，动物主题 |

---

## 三、核心技术要点

### 3.1 依赖版本锁定（CRITICAL）

```json
// package.json — 必须锁定的版本组合
{
  "pixi.js": "^6.5.10",           // 必须 v6，v7+ 不兼容！
  "pixi-live2d-display": "^0.4.0", // 与 PIXI v6 配套
  "@pixi/unsafe-eval": "^6.5.10"   // 解决 unsafe-eval 报错
}
```

### 3.2 Live2D 模型加载核心代码

```ts
// use-live2d.ts 关键片段
import * as PIXI from 'pixi.js';
import { Live2DModel } from 'pixi-live2d-display';

// 1. 暴露全局 PIXI（pixi-live2d-display 需要）
window.PIXI = PIXI;

// 2. 创建 PIXI 应用（透明背景）
const app = new PIXI.Application({
  view: canvasRef.current,
  backgroundAlpha: 0,      // 透明画布
  autoStart: true,
});

// 3. 加载模型
const model = await Live2DModel.from('/models/hiyori/hiyori.model3.json');

// 4. 关键！注册 ticker，否则模型冻结
app.ticker.add(() => model.update());

// 5. 添加到舞台
app.stage.addChild(model);

// 6. 眼球追踪
model.on('pointermove', (x, y) => {
  // 自动处理眼睛跟随
});
```

### 3.3 Tauri 透明窗口配置

```json
// src-tauri/tauri.conf.json
{
  "app": {
    "windows": [{
      "label": "main",
      "title": "桌面宠物",
      "width": 300,
      "height": 500,
      "decorations": false,    // 无标题栏
      "transparent": true,     // 透明背景
      "alwaysOnTop": true,     // 始终置顶
      "skipTaskbar": true,     // 任务栏不显示
      "resizable": false
    }]
  }
}
```

```css
/* 前端 CSS 配合 */
html, body, #root {
  background-color: transparent;
  margin: 0;
  padding: 0;
  overflow: hidden;
}
```

### 3.4 AI 情感映射（Hiyori 的做法）

```
LLM 返回 → JSON { valence: 0.8, arousal: 0.6, dominance: 0.5 }
                ↓ 映射表
          valence > 0.5 → "happy" 表情
          valence < -0.3 → "sad" 表情
          arousal > 0.7 → "surprised" 表情
                ↓
          model.expression('happy_01')
```

---

## 四、学习路线（建议时长 2 周）

```
第 1 天：环境搭建
  ├── 安装 Rust + Tauri CLI + Node.js
  ├── 跑通 Tauri + React 脚手架
  └── 实现透明无边框窗口

第 2-3 天：Live2D 渲染
  ├── 安装 PIXI v6 + pixi-live2d-display
  ├── 加载第一个模型（shizuku）
  ├── 实现眼追踪 + 点击互动
  └── 参考：desktop-live2d-previewer 源码

第 4-5 天：交互系统
  ├── 表情切换、动作播放
  ├── 窗口拖拽、缩放
  ├── 右键菜单
  └── 参考：Hiyori 源码

第 6-7 天：AI 集成
  ├── 接入 Ollama 本地模型（免费）
  ├── 对话气泡 UI
  ├── 情感数据 → 表情映射
  └── 参考：Hiyori 的情感系统

第 8-10 天：打磨上线
  ├── 多模型切换
  ├── 开机自启 + 系统托盘
  ├── 打包发布（.exe/.msi）
  └── 参考：tauri-live2d 的 CI 配置
```

---

## 五、快速起步命令

```bash
# 1. 安装 Tauri CLI
cargo install tauri-cli --version "^2.0"

# 2. 创建项目
npm create tauri-app@latest desktop-pet -- --template react-ts

# 3. 安装 Live2D 依赖
cd desktop-pet
npm install pixi.js@6 pixi-live2d-display @pixi/unsafe-eval

# 4. 下载免费模型（shizuku 最简入门）
# 放入 public/models/shizuku/

# 5. 启动开发
npm run tauri dev
```

---

## 六、额外资源

| 资源 | 链接 |
|------|------|
| Live2D 在线预览 | https://guansss.github.io/live2d-viewer-web/ |
| pixi-live2d-display 文档 | https://github.com/guansss/pixi-live2d-display |
| Tauri 窗口自定义文档 | https://v2.tauri.app/learn/window-customization/ |
| 透明窗口模板 | https://github.com/nooralu/transparent-tauri-app-template |

---

> 下一步：选定使用的 Live2D 模型和 AI 方案，开始搭 Tauri + React 脚手架。
