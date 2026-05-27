# AICodePR — 完整部署指南

## 第一步：获取 API Keys

### DeepSeek API（必填）
1. 打开 https://platform.deepseek.com
2. 注册/登录，进入 API Keys 页面
3. 创建新 Key，复制 `sk-xxx`
4. 充值 ¥10 即可（够审几千个 PR）

### Claude API（可选，高级功能）
1. 打开 https://console.anthropic.com
2. 创建 API Key

---

## 第二步：注册 GitHub App

这是最关键的一步，需要准确操作：

### 2.1 创建 App
1. 打开 https://github.com/settings/apps
2. 点击 **New GitHub App**
3. 填写：
   - **GitHub App name**: `AICodePR`（或你的品牌名）
   - **Homepage URL**: 先填 `http://localhost:8000`（部署后更新）
   - **Webhook URL**: `https://你的域名/webhook`
     - 本地测试：用 ngrok 生成 URL
     - 生产环境：Railway/服务器域名
   - **Webhook secret**: 点 Generate，复制保存

### 2.2 权限设置（Repository permissions）
- **Pull requests**: Read & write
- **Contents**: Read-only

### 2.3 订阅事件（Subscribe to events）
- 勾选 **Pull request**

### 2.4 完成创建
- 点击 **Create GitHub App**
- 生成 Private Key：滚动到底部 → **Generate a private key** → 下载 `.pem` 文件

### 2.5 获取 App ID
- 页面顶部 **App ID** 那串数字，复制

### 2.6 安装 App
- 左侧菜单 → **Install App**
- 选择你的测试仓库 → Install

---

## 第三步：配置 .env

```bash
cp .env.example .env
```

编辑 `.env`，填入：

```ini
# GitHub App（从第二步获取）
GITHUB_APP_ID=你看到的数字
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
整段复制 .pem 文件内容
-----END RSA PRIVATE KEY-----"
GITHUB_WEBHOOK_SECRET=你生成的 webhook secret

# DeepSeek API（第一步获取）
DEEPSEEK_API_KEY=sk-xxx

# 先用 DeepSeek，便宜
REVIEW_MODEL=deepseek
```

---

## 第四步：本地测试

### 4.1 启动 ngrok（让 GitHub 能访问你的 localhost）
```bash
# 安装 ngrok: brew install ngrok
ngrok http 8000
```
复制 ngrok 提供的 URL（如 `https://abc123.ngrok.io`）

### 4.2 更新 GitHub App Webhook URL
回到 GitHub App 设置 → 把 Webhook URL 改成 `https://abc123.ngrok.io/webhook`

### 4.3 启动服务
```bash
chmod +x setup.sh start.sh
./setup.sh   # 首次运行
./start.sh   # 后续启动
```

### 4.4 测试
1. 在安装过 App 的仓库里创建一个 PR
2. 等 30-60 秒
3. 查看 PR 页面，应该出现 AICodePR 评论

---

## 第五步：部署到 Railway（生产）

### 5.1 部署
```bash
# 安装 Railway CLI
brew install railway

# 登录
railway login

# 初始化
cd /Users/liao/ai-code-review
railway init

# 配置环境变量
railway variables set \
  GITHUB_APP_ID=xxx \
  GITHUB_PRIVATE_KEY="$(cat /path/to/key.pem)" \
  GITHUB_WEBHOOK_SECRET=xxx \
  DEEPSEEK_API_KEY=sk-xxx \
  REVIEW_MODEL=deepseek

# 部署
railway up
```

### 5.2 更新 Webhook URL
Railway 会给一个域名（如 `aigate.up.railway.app`），回到 GitHub App 设置，把 Webhook URL 更新为：
```
https://aigate.up.railway.app/webhook
```

---

## 调试

### 查看日志
```bash
# 本地
tail -f server.log

# Railway
railway logs
```

### 常见问题

1. **Webhook 收不到**: 检查 GitHub App → Advanced → 看 Delivery 里有没失败的
2. **401 错误**: Webhook secret 不匹配，检查 .env 里的值
3. **评论发不出去**: 确认 App 已安装到目标仓库，权限开对
4. **AI 返回空**: 看日志，可能是 DeepSeek API Key 不对或者余额不够

---

## 成本预估

DeepSeek 定价极低，单次 PR Review 约 ¥0.001-0.01。
充 ¥10 能跑 1000-10000 个 PR。
