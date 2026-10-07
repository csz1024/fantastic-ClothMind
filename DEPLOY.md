# OutfitWindow GitHub Pages 部署指南

## 方式一：手动创建仓库（推荐，5分钟完成）

### 第1步：在 GitHub 创建新仓库

1. 打开 https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `outfitwindow`（或你喜欢的名字）
   - **Description**: 基于个人已有衣物与真实商品库存的场景穿搭组购智能体
   - **Visibility**: ✅ Public（GitHub Pages 免费版需要公开仓库）
   - ✅ Add a README file（可选，后面会覆盖）
3. 点击 **Create repository**

### 第2步：推送本地代码

在项目目录下执行以下命令（复制粘贴即可）：

```bash
cd outfitwindow

# 重命名分支为 main（GitHub 默认分支）
git branch -m main

# 添加远程仓库（将 YOUR_USERNAME 替换为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/outfitwindow.git

# 推送代码
git push -u origin main
```

### 第3步：启用 GitHub Pages

1. 打开你的仓库页面：`https://github.com/YOUR_USERNAME/outfitwindow`
2. 点击 **Settings**（顶部标签页）
3. 左侧菜单选择 **Pages**
4. 在 "Build and deployment" 区域：
   - **Source**: 选择 **Deploy from a branch**
   - **Branch**: 选择 `main`，文件夹选 `/(root)`
5. 点击 **Save**

### 第4步：访问在线链接

等待 1-2 分钟后，访问：

```
https://YOUR_USERNAME.github.io/outfitwindow
```

🎉 你的 OutfitWindow 就上线啦！

---

## 方式二：只部署前端页面（最小化）

如果你只想部署前端页面（不含 Python 代码和测试），可以使用 `deploy/` 目录：

```bash
cd outfitwindow/deploy

# 初始化新仓库
git init
git add .
git commit -m "Deploy OutfitWindow frontend"

# 推送到 GitHub（仓库需提前创建）
git remote add origin https://github.com/YOUR_USERNAME/outfitwindow.git
git push -u origin main
```

然后在 GitHub Settings > Pages 中启用即可。

---

## 方式三：安装 GitHub CLI 后自动化（可选）

如果你以后经常部署，可以安装 GitHub CLI：

```bash
# Windows (winget)
winget install --id GitHub.cli

# 登录
gh auth login

# 然后一键创建仓库并推送
cd outfitwindow
gh repo create outfitwindow --public --source=. --push
```

---

## 部署后的目录结构

GitHub Pages 会从仓库根目录部署，以下文件会被发布：

```
outfitwindow/
├── index.html              ← 首页入口
├── garment-upload.html     ← 衣物录入
├── requirement.html        ← 需求填写
├── window.html             ← 穿搭橱窗
├── shopping-list.html      ← 购物意向清单
├── merchant.html           ← 商家商品
├── status.html             ← 运行状态
└── assets/                 ← CSS/JS/图片资源
    ├── css/style.css
    ├── js/data.js
    ├── js/engine.js
    └── js/app.js
```

---

## 更新部署

每次修改代码后，重新推送即可自动更新：

```bash
cd outfitwindow
git add .
git commit -m "更新说明"
git push origin main
```

GitHub Pages 会在推送后 1-2 分钟内自动重新部署。

---

## 常见问题

**Q: 页面打开是 404？**
A: 刚启用 Pages 后需要等待 1-2 分钟。如果超过 5 分钟，检查仓库是否为 Public，以及 Pages 设置中的分支是否正确。

**Q: CSS/JS 加载失败？**
A: 检查 `assets/` 文件夹是否已推送到仓库。路径应为相对路径（如 `assets/css/style.css`）。

**Q: 可以用私有仓库吗？**
A: GitHub Pages 免费版只支持 Public 仓库。私有仓库需要 GitHub Pro（付费）。

**Q: 可以绑定自定义域名吗？**
A: 可以。在 Settings > Pages > Custom domain 中设置，并添加 CNAME 文件。

---

## 需要帮助？

如果在部署过程中遇到问题，可以：
1. 检查 GitHub Pages 文档：https://docs.github.com/en/pages
2. 查看仓库的 Actions 标签页（部署日志）
3. 在本项目 Issue 中提问（如果你创建了公开仓库）