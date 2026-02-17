# Kimi-Coding/K2P5 配置指南

## 当前状态

✅ **系统架构已就绪** - 完全支持 `kimi-coding/k2p5` 模型
❌ **API Key无效** - 需要获取有效Key

---

## 🔧 问题诊断

### 错误信息
```
Invalid Authentication - API Key无效
```

### 可能原因
1. **API Key已过期** - 你的Key可能已过期
2. **账户余额不足** - 账户可能没有可用余额
3. **Key被撤销** - Key可能已被撤销或禁用
4. **不同平台** - 你可能在其他平台（非Moonshot）获取的Key

---

## ✅ 解决方案

### 方案1: 从Moonshot官方获取Key

1. 访问 https://platform.moonshot.cn
2. 注册/登录账户
3. 充值（需要预充值才能使用API）
4. 创建API Key
5. 复制新Key

### 方案2: 从其他平台获取K2P5访问

如果你是通过其他平台接入的 `kimi-coding/k2p5`，请确认：

| 平台 | Base URL | 配置方式 |
|------|----------|----------|
| Moonshot官方 | `https://api.moonshot.cn/v1` | 直接API调用 |
| OpenRouter | `https://openrouter.ai/api/v1` | 需要OpenRouter Key |
| Together AI | `https://api.together.xyz/v1` | 需要Together Key |
| 其他代理 | 自定义URL | 根据代理配置 |

### 方案3: 使用模拟模式继续开发

在获取有效Key之前，可以使用模拟模式：

```bash
# 不设置KIMI_API_KEY，自动使用模拟模式
python3 hybrid_ai_company.py
```

---

## 📝 配置步骤

### 步骤1: 确认你的接入方式

请问你是通过哪个平台接入的 `kimi-coding/k2p5`？

- [ ] Moonshot官方 (platform.moonshot.cn)
- [ ] OpenRouter (openrouter.ai)
- [ ] Together AI (together.xyz)
- [ ] 其他平台/代理

### 步骤2: 根据平台配置

#### Moonshot官方
```bash
export KIMI_API_KEY="sk-moonshot-xxxxx"
export KIMI_BASE_URL="https://api.moonshot.cn/v1"
export KIMI_MODEL="kimi-coding/k2p5"
```

#### OpenRouter
```bash
export KIMI_API_KEY="sk-or-v1-xxxxx"  # OpenRouter的Key
export KIMI_BASE_URL="https://openrouter.ai/api/v1"
export KIMI_MODEL="kimi-coding/k2p5"
```

#### Together AI
```bash
export KIMI_API_KEY="xxxxx"  # Together的Key
export KIMI_BASE_URL="https://api.together.xyz/v1"
export KIMI_MODEL="kimi-coding/k2p5"
```

### 步骤3: 测试连接

```bash
python3 test_k2p5_connection.py
```

---

## 🎮 当前可用功能

即使没有有效API Key，以下功能仍可用：

### ✅ 模拟AI模式
```bash
python3 hybrid_ai_company.py
```
- 7个Agent自动协作
- 完整的公司运营模拟
- 财务、项目、HR管理

### ✅ 可视化界面
```bash
open advanced_dashboard.html
```
- 实时状态监控
- 财务图表
- 项目看板

### ✅ 系统架构
- 完整的多Agent协作框架
- 支持真实/模拟AI无缝切换
- 一旦获取有效Key，立即启用真实AI

---

## 💡 快速验证

### 测试你的Key是否有效

```bash
# 设置你的Key
export KIMI_API_KEY="your-actual-key"

# 测试连接
curl https://api.moonshot.cn/v1/models \
  -H "Authorization: Bearer $KIMI_API_KEY"
```

如果返回模型列表，说明Key有效。

### 直接测试k2p5模型

```bash
curl https://api.moonshot.cn/v1/chat/completions \
  -H "Authorization: Bearer $KIMI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "kimi-coding/k2p5",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

---

## 📞 需要帮助？

### Moonshot官方支持
- 文档: https://platform.moonshot.cn/docs
- 客服: platform.moonshot.cn 控制台内提交工单

### 检查清单
- [ ] API Key是否正确复制（没有多余空格）
- [ ] 账户是否有足够余额
- [ ] Key是否已启用（没有被禁用）
- [ ] 是否使用了正确的Base URL

---

**系统已完全就绪，等待接入有效的k2p5 API Key！**
