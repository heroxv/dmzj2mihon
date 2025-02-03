# 动漫之家订阅备份与恢复指南

本指南将帮助您在安全环境下进行订阅数据的备份与恢复操作，请仔细阅读每一步操作说明。

------

## 🔐 安全须知

- 重要提示：
  - 请确保所有操作均在您信任的个人设备上进行。
  - 严禁分享您的个人凭证（如 `user_id` 和 `token`）。

------

## 📦 环境准备

### 1. Python 环境配置

请确保您的系统具备以下要求：

- **Python 版本：** 3.6 或更高版本
- **包管理器：** pip

在终端中运行以下命令以验证和安装必要依赖：

```bash
# 验证 Python 版本
python --version

# 安装依赖库
pip install requests pyyaml
```

### 2. 配置文件准备

在脚本所在目录创建 `config.yaml` 文件，并按照下面模板填写相关配置：

```yaml
big_cat_id: 0
letter_filter: "all"
status_id: 1
user_id: ""  # 请填写您的 user_id
token: ""    # 请填写您的 token
max_retries: 3
retry_delay: 2
max_workers: 5
```

------

## 🔑 获取账号凭证

### 步骤概览

1. **安装 Cookie-Editor 浏览器插件：**

   - **Chrome/Edge：** [Cookie-Editor - Chrome 应用商店](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
   - **Firefox：** [Cookie-Editor – Firefox 附加组件](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/)

2. **登录动漫之家账号：**

   - 打开 [动漫之家个人主页](https://i.idmzj.com/) 并登录。

3. **提取必要 Cookie 信息：**

   - 点击浏览器工具栏中的 Cookie-Editor 图标。

   - 在 Cookie 列表中查找以下项，并复制它们的值：

     ![](https://cdn.jsdelivr.net/gh/heroxv/Image/test/202502031926325.png)

     - **my**
     - **dmzj_session**

4. **更新配置文件：**

   - 将复制的值分别填入 `config.yaml` 中对应的 `user_id` 与 `token` 字段。

> **注意：** 确保复制内容时不要包含多余空格或换行符，保证配置文件格式正确。

------

## 💾 执行备份

### 1. 运行备份脚本

在脚本所在目录下运行以下命令：

```bash
python main.py
```

### 2. 备份文件说明

脚本运行结束后，会在 `output` 目录下生成两个文件：

- **all_subscriptions.json**：原始数据备份文件。
- **backup_data.json**：格式化后的备份文件，便于后续导入。

------

## 📱 恢复订阅

### 第一步：使用 [Tachibk Viewer](https://tachibk.netlify.app/)

1. 打开 [Tachibk Viewer](https://tachibk.netlify.app/) 网站。

2. 选择并导入 `backup_data.json` 文件。

3. 等待系统同步完成。

   ![img](https://cdn.jsdelivr.net/gh/heroxv/Image/test/202502031910747.png)

   ![img](https://cdn.jsdelivr.net/gh/heroxv/Image/test/202502031913970.png)

### 第二步：导入 Mihon 应用

1. 打开 **Mihon** 应用。
2. 进入 **更多** → **设置** → **数据与存储** → **备份与还原**。
3. 选择「还原备份」，然后导入 `output.tachibk` 文件。
4. 下拉刷新后确认数据同步。

------

## ⚙️ 进阶设置与性能优化

在 `config.yaml` 中可以根据需要调整以下参数：

- **max_workers：** 控制并发数（建议设置在 5 到 10 之间）。
- **retry_delay：** 设置重试间隔（单位：秒）。
- **max_retries：** 设置最大重试次数，适用于网络波动时的数据请求。

------

## 🔧 故障排查

### 常见问题及解决方案

1. **无法获取 Cookie：**
   - 清除浏览器缓存后重新登录。
   - 检查浏览器插件的权限设置。
2. **导入失败：**
   - 检查文件编码，确保文件为 UTF-8 格式。
   - 验证 JSON 文件的完整性和正确性。
3. **Token 失效：**
   - 避免在网站访问高峰期操作。
   - 如遇频繁错误，可适当增加 `retry_delay` 参数值。