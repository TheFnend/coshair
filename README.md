# 07妙妙屋订单管理系统

一个基于Flask的Cosplay假发订单管理系统，专为07妙妙屋设计开发。

## 📋 功能特性

### 🎯 核心功能
- **订单管理**：添加、编辑、删除、查看订单
- **智能筛选**：按状态、紧急程度、日期范围筛选
- **排序功能**：支持多字段排序（日期、金额、状态等）
- **批量操作**：批量删除订单
- **数据导出**：支持JSON和CSV格式导出
- **数据备份**：完整的数据库备份和恢复功能

### 🎨 界面特性
- **响应式设计**：支持桌面和移动设备
- **视觉提醒**：订单紧急程度颜色标识
- **自定义背景**：支持上传背景图片和透明度调节
- **统计面板**：实时显示订单数量和金额统计
- **图例说明**：清晰的颜色含义说明

### 📊 数据管理
- **SQLite数据库**：轻量级本地数据库
- **数据导入导出**：JSON/CSV格式支持
- **自动备份**：支持定时备份和手动备份
- **数据恢复**：从备份文件快速恢复数据

## 🚀 快速开始

### 环境要求
- Python 3.7+
- pip包管理器

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd coshair
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动应用**
   ```bash
   python app.py
   ```

4. **访问系统**
   打开浏览器访问：`http://localhost:5000`

## 📁 项目结构

```
coshair/
├── app.py                 # Flask应用主文件
├── data_manager.py        # 数据管理工具
├── requirements.txt       # 依赖包列表
├── README.md             # 项目说明文档
├── instance/             # 数据库文件目录
│   └── coswig_orders.db  # SQLite数据库
├── static/               # 静态资源
│   ├── favicon.svg       # 网站图标
│   ├── iconfont.css      # 图标字体样式
│   ├── iconfont.ttf      # 图标字体文件
│   ├── qq.svg           # QQ图标
│   ├── wechat.svg       # 微信图标
│   ├── xianyu.svg       # 闲鱼图标
│   └── 头像_耀骑士临光.png # 默认头像
├── templates/            # HTML模板
│   ├── base.html        # 基础模板
│   ├── index.html       # 主页模板
│   ├── add_order.html   # 添加订单模板
│   └── edit_order.html  # 编辑订单模板
├── backups/             # 备份文件目录
└── fontawesome-free-7.0.0-web/  # FontAwesome图标库
```

## 🎮 使用指南

### 订单管理

#### 添加订单
1. 点击"添加新订单"按钮
2. 填写订单信息：
   - **基本信息**：Coser姓名、角色名称、联系平台
   - **时间信息**：客户需要日期、下单日期
   - **财务信息**：尾款金额、是否包含邮费
   - **制作信息**：毛坯购买状态、蛋糕盒需求
3. 点击"保存"提交订单

#### 编辑订单
1. 在订单列表中点击"编辑"按钮
2. 修改需要更新的字段
3. 点击"保存"确认修改

#### 删除订单
- **单个删除**：点击订单行的"删除"按钮
- **批量删除**：勾选多个订单，点击"批量删除"

### 筛选和排序

#### 状态筛选
- 全部订单
- 待制作
- 制作中
- 已完成
- 已发货
- 已取消

#### 紧急程度筛选
- 普通（7天以上）
- 较急（3-7天）
- 通急（3天内）

#### 排序选项
- 按下单日期
- 按需要日期
- 按尾款金额
- 按创建时间

### 数据管理

#### 使用数据管理工具
```bash
python data_manager.py
```

功能菜单：
1. **查看数据库信息** - 显示订单统计和文件信息
2. **导出数据到JSON** - 备份所有订单数据
3. **导出数据到CSV** - Excel兼容格式导出
4. **从JSON导入数据** - 从备份文件恢复数据
5. **备份数据库** - 完整备份SQLite文件
6. **恢复数据库** - 从备份文件恢复数据库

## 🎨 界面说明

### 颜色标识

#### 紧急程度
- 🟡 **黄色**：较急订单（3-7天内需要）
- 🔴 **红色**：通急订单（3天内需要）
- ⚫ **深红色**：已过期订单（排单日期已过但未完成）

#### 订单状态
- 🟢 **绿色**：已完成订单
- 🔵 **蓝色**：已发货订单
- ⚪ **白色**：其他状态订单

### 统计卡片
- **总订单数**：当前显示的订单总数
- **待收尾款**：未完成订单的尾款总额
- **已完成**：已完成状态的订单数量
- **制作中**：正在制作的订单数量
- **待制作**：等待开始制作的订单数量

## 🔧 技术栈

### 后端技术
- **Flask 2.3.3** - Python Web框架
- **SQLAlchemy 3.0.5** - 数据库ORM
- **SQLite** - 轻量级数据库
- **Flask-CORS** - 跨域支持

### 前端技术
- **Bootstrap 5.1.3** - CSS框架
- **jQuery** - JavaScript库
- **FontAwesome** - 图标库
- **Bootstrap Icons** - 图标库

### 数据格式
- **JSON** - 数据交换格式
- **CSV** - 表格数据导出
- **SQLite** - 数据库存储

## 📝 数据库结构

### Order表字段

| 字段名 | 类型 | 说明 | 必填 |
|--------|------|------|------|
| id | Integer | 主键ID | 是 |
| cn | String(100) | Coser姓名 | 是 |
| character | String(200) | 角色名称 | 是 |
| contact | String(200) | 联系平台 | 是 |
| needed_date | Date | 客户需要日期 | 是 |
| order_date | Date | 下单日期 | 是 |
| created_at | DateTime | 创建时间 | 自动 |
| deposit_paid | Boolean | 定金支付状态 | 否 |
| final_amount | Float | 尾款金额 | 是 |
| shipping_included | Boolean | 尾款包含邮费 | 否 |
| blank_purchased | Boolean | 毛坯购买状态 | 否 |
| cake_box | String(10) | 蛋糕盒需求 | 否 |
| status | String(50) | 订单状态 | 否 |

## 🛠️ 开发说明

### 本地开发

1. **开启调试模式**
   ```python
   app.run(debug=True, host='0.0.0.0', port=5000)
   ```

2. **数据库初始化**
   ```python
   with app.app_context():
       db.create_all()
   ```

### API接口

#### 获取所有订单
```
GET /api/orders
```

#### 更新订单
```
POST /api/update_order/<id>
Content-Type: application/json

{
    "status": "已完成",
    "deposit_paid": true
}
```

#### 批量删除
```
POST /api/batch_delete
Content-Type: application/json

{
    "order_ids": [1, 2, 3]
}
```

## 🔒 安全说明

- 使用Flask内置的安全机制
- 数据库查询使用SQLAlchemy ORM防止SQL注入
- 文件上传限制图片格式
- 敏感配置使用环境变量

## 📞 支持与反馈

如有问题或建议，请通过以下方式联系：

- 项目Issues
- 邮件联系
- QQ/微信群组

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

感谢以下开源项目的支持：
- Flask Web框架
- Bootstrap CSS框架
- FontAwesome图标库
- SQLAlchemy ORM

---

**07妙妙屋订单管理系统** - 让订单管理更简单高效！ 🎭✨