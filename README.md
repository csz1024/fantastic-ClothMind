# OutfitWindow 搭搭橱窗

基于个人已有衣物与真实商品库存的场景穿搭组购智能体 MVP。

## 在线体验

👉 **[点击体验 OutfitWindow](https://你的用户名.github.io/outfitwindow)**

（部署后替换上方链接）

## 本地运行

### 方式一：双击运行（无需安装）

1. 下载 `outfitwindow-offline.zip`
2. 解压到任意文件夹
3. 双击 `index.html` 即可在浏览器中运行

### 方式二：命令行

```bash
cd outfitwindow
python scripts/pipeline.py --demo --output-dir data/outputs
```

## 项目结构

```
outfitwindow/
├── web/                 ← 前端页面源码
│   ├── pages/           ← 7 个 HTML 页面
│   └── assets/          ← CSS/JS/图片资源
├── scripts/             ← Python 技能模块
│   ├── pipeline.py      ← 主工作流管道
│   └── skills_lib/      ← 11 个可复用技能
├── data/                ← 演示数据
│   ├── inputs/raw/      ← 30 条商品 CSV
│   └── outputs/         ← 管道产物
├── tests/               ← 测试用例
└── deploy/              ← GitHub Pages 部署文件
```

## 核心功能

- **衣物录入**：上传/选择一件衣物，确认识别结果
- **需求填写**：场景、预算、尺码偏好
- **穿搭橱窗**：生成 1-3 套方案，支持锁定/替换单品
- **缺货重规划**：库存不足时自动保留有效项重新规划
- **购物意向清单**：最终生成含免责声明的意向清单

## 技术栈

- 前端：纯 HTML5 / CSS3 / JavaScript（无框架依赖）
- 数据存储：浏览器 localStorage
- 后端逻辑：Python 3.13（本地管道）
- 商品数据：CSV 静态数据（含边界状态）

## 边界状态验证

| 状态 | 示例 |
|---|---|
| M码缺货 | V006 库存=0 |
| 价格缺失 | V008/V009 |
| 库存为零 | 9 个变体 |
| 下架/停产 | OW-BTM-003/OW-OUT-006/OW-ACC-003 |
| 运费未知 | 5 个变体 |
| 超预算 | OW-OUT-004 ¥599 |
| 赞助商品 | OW-TOP-006（紫色角标标识） |

## 免责声明

本系统为演示项目，商品数据均为合成演示数据（SYNTHETIC_DEMO），不构成真实购买与下单。价格、库存以实际商家页面为准。

## 测试

```bash
# 边界测试
python tests/test_skills_lib.py

# 端到端验收测试
python tests/test_e2e_acceptance.py
```

## License

MIT