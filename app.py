#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
07妙妙屋订单管理系统
主应用程序文件

功能：
- 订单的增删改查
- 订单状态管理
- 数据统计和展示
- RESTful API接口
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, date
import os
import json

# 创建Flask应用实例
app = Flask(__name__)

# 应用配置
app.config['SECRET_KEY'] = 'your-secret-key-here'  # 用于会话加密
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coswig_orders.db'  # 数据库连接
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 禁用SQLAlchemy事件系统

# 启用CORS支持，允许跨域请求
CORS(app)

# 初始化数据库
db = SQLAlchemy(app)

# ==================== 数据库模型 ====================

class Order(db.Model):
    """
    订单数据模型
    
    存储假发制作订单的所有相关信息
    """
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 基本信息
    cn = db.Column(db.String(100), nullable=False)  # Coser姓名
    character = db.Column(db.String(200), nullable=False)  # 角色名称
    contact = db.Column(db.String(200), nullable=False)  # 联系平台(QQ/微信/闲鱼)
    
    # 时间信息
    needed_date = db.Column(db.Date, nullable=False)  # 客户需要的完成时间
    order_date = db.Column(db.Date, nullable=False)  # 下单时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 记录创建时间
    
    # 财务信息
    deposit_paid = db.Column(db.Boolean, default=False)  # 定金支付状态
    final_amount = db.Column(db.Float, nullable=False)  # 尾款金额
    shipping_included = db.Column(db.Boolean, default=False)  # 尾款是否包含邮费
    
    # 制作信息
    blank_purchased = db.Column(db.Boolean, default=False)  # 毛坯购买状态
    cake_box = db.Column(db.String(10), default='不需要')  # 蛋糕盒包装需求
    status = db.Column(db.String(50), default='待制作')  # 订单状态
    
    def __repr__(self):
        """对象的字符串表示"""
        return f'<Order {self.cn} - {self.character}>'

# ==================== 路由定义 ====================

@app.route('/')
def index():
    """
    主页路由 - 显示订单列表
    
    功能：
    - 支持按多种字段排序
    - 支持按平台筛选
    - 支持显示/隐藏已完成订单
    - 计算订单统计信息
    """
    
    # 获取URL参数
    sort_by = request.args.get('sort', 'needed_date')  # 排序字段
    order = request.args.get('order', 'asc')  # 排序方向
    show_completed = request.args.get('show_completed', 'false') == 'true'  # 是否显示已完成
    platform_filter = request.args.get('platform', '')  # 平台筛选
    
    # 构建数据库查询
    query = Order.query
    
    # 注释掉后端筛选，改为前端控制
    # if not show_completed:
    #     query = query.filter(Order.status.notin_(['已完成', '已发货']))
    
    # 平台筛选
    if platform_filter:
        query = query.filter(Order.contact == platform_filter)
    
    # 排序
    if sort_by == 'needed_date':
        if order == 'desc':
            orders = query.order_by(Order.needed_date.desc()).all()
        else:
            orders = query.order_by(Order.needed_date.asc()).all()
    elif sort_by == 'order_date':
        if order == 'desc':
            orders = query.order_by(Order.order_date.desc()).all()
        else:
            orders = query.order_by(Order.order_date.asc()).all()
    else:
        orders = query.order_by(Order.needed_date.asc()).all()
    
    # 将订单对象转换为字典以便JSON序列化
    orders_dict = []
    for order in orders:
        orders_dict.append({
            'id': order.id,
            'cn': order.cn,
            'character': order.character,
            'contact': order.contact,
            'needed_date': order.needed_date.strftime('%Y-%m-%d'),
            'order_date': order.order_date.strftime('%Y-%m-%d'),
            'deposit_paid': bool(order.deposit_paid),
            'final_amount': order.final_amount,
            'shipping_included': bool(order.shipping_included),
            'blank_purchased': bool(order.blank_purchased),
            'status': order.status
        })
    
    return render_template('dashboard_index.html', orders=orders, orders_json=json.dumps(orders_dict), sort_by=sort_by, order=order, show_completed=show_completed, platform_filter=platform_filter)

@app.route('/add', methods=['GET', 'POST'])
def add_order():
    """
    添加新订单路由
    
    GET: 显示添加订单表单
    POST: 处理表单提交，创建新订单
    """
    if request.method == 'POST':
        try:
            # 从表单数据创建新订单对象
            order = Order(
                cn=request.form['cn'],
                character=request.form['character'],
                contact=request.form['contact'],
                needed_date=datetime.strptime(request.form['needed_date'], '%Y-%m-%d').date(),
                order_date=datetime.strptime(request.form['order_date'], '%Y-%m-%d').date(),
                deposit_paid=bool(request.form.get('deposit_paid')),
                final_amount=float(request.form['final_amount']),
                shipping_included=bool(request.form.get('shipping_included')),
                blank_purchased=bool(request.form.get('blank_purchased')),
                cake_box=request.form.get('cake_box', '不需要')
            )
            # 保存到数据库
            db.session.add(order)
            db.session.commit()
            flash('订单添加成功！', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'添加失败：{str(e)}', 'error')
    
    return render_template('add_order.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_order(id):
    """
    编辑订单路由
    
    GET: 显示编辑表单
    POST: 更新订单信息
    """
    order = Order.query.get_or_404(id)  # 获取订单或返回404
    
    if request.method == 'POST':
        try:
            # 更新订单字段
            order.cn = request.form['cn']
            order.character = request.form['character']
            order.contact = request.form['contact']
            order.needed_date = datetime.strptime(request.form['needed_date'], '%Y-%m-%d').date()
            order.order_date = datetime.strptime(request.form['order_date'], '%Y-%m-%d').date()
            order.deposit_paid = bool(request.form.get('deposit_paid'))
            order.final_amount = float(request.form['final_amount'])
            order.shipping_included = bool(request.form.get('shipping_included'))
            order.blank_purchased = bool(request.form.get('blank_purchased'))
            order.cake_box = request.form.get('cake_box', '不需要')
            order.status = request.form['status']
            
            db.session.commit()
            flash('订单更新成功！', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'更新失败：{str(e)}', 'error')
    
    return render_template('edit_order.html', order=order)

@app.route('/dashboard/edit/<int:id>', methods=['GET', 'POST'])
def dashboard_edit_order(id):
    """
    Dashboard编辑订单路由
    
    GET: 显示编辑表单
    POST: 更新订单信息并返回dashboard
    """
    order = Order.query.get_or_404(id)  # 获取订单或返回404
    
    if request.method == 'POST':
        try:
            # 更新订单字段
            order.cn = request.form['cn']
            order.character = request.form['character']
            order.contact = request.form['contact']
            order.needed_date = datetime.strptime(request.form['needed_date'], '%Y-%m-%d').date()
            order.order_date = datetime.strptime(request.form['order_date'], '%Y-%m-%d').date()
            order.deposit_paid = bool(request.form.get('deposit_paid'))
            order.final_amount = float(request.form['final_amount'])
            order.shipping_included = bool(request.form.get('shipping_included'))
            order.blank_purchased = bool(request.form.get('blank_purchased'))
            order.cake_box = request.form.get('cake_box', '不需要')
            order.status = request.form['status']
            
            db.session.commit()
            flash('订单更新成功！', 'success')
            return redirect(url_for('dashboard_index'))
        except Exception as e:
            flash(f'更新失败：{str(e)}', 'error')
    
    return render_template('edit_order.html', order=order)

@app.route('/delete/<int:id>')
def delete_order(id):
    """
    删除订单路由
    
    删除指定ID的订单
    """
    order = Order.query.get_or_404(id)
    try:
        db.session.delete(order)
        db.session.commit()
        flash('订单删除成功！', 'success')
    except Exception as e:
        flash(f'删除失败：{str(e)}', 'error')
    
    return redirect(url_for('index'))

# ==================== API路由 ====================

@app.route('/api/orders')
def api_orders():
    """
    获取所有订单的API接口
    
    返回JSON格式的订单列表
    """
    orders = Order.query.all()
    return jsonify([{
        'id': order.id,
        'cn': order.cn,
        'character': order.character,
        'contact': order.contact,
        'needed_date': order.needed_date.strftime('%Y-%m-%d'),
        'order_date': order.order_date.strftime('%Y-%m-%d'),
        'deposit_paid': order.deposit_paid,
        'final_amount': order.final_amount,
        'shipping_included': order.shipping_included,
        'blank_purchased': order.blank_purchased,
        'status': order.status
    } for order in orders])

@app.route('/api/update_order/<int:id>', methods=['POST'])
def api_update_order(id):
    """
    更新订单API接口
    
    支持部分字段更新，用于前端快速操作
    """
    order = Order.query.get_or_404(id)
    data = request.get_json()
    
    try:
        # 根据传入的数据更新相应字段
        if 'deposit_paid' in data:
            order.deposit_paid = data['deposit_paid']
        if 'blank_purchased' in data:
            order.blank_purchased = data['blank_purchased']
        if 'status' in data:
            order.status = data['status']
        if 'contact' in data:
            order.contact = data['contact']
        if 'shipping_included' in data:
            order.shipping_included = data['shipping_included']
        if 'cake_box' in data:
            order.cake_box = data['cake_box']
        if 'needed_date' in data:
            order.needed_date = datetime.strptime(data['needed_date'], '%Y-%m-%d').date()
        
        db.session.commit()
        return jsonify({'success': True, 'message': '更新成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/batch_delete', methods=['POST'])
def api_batch_delete():
    """
    批量删除订单API接口
    
    接收订单ID列表，批量删除订单
    """
    data = request.get_json()
    order_ids = data.get('order_ids', [])
    
    try:
        if not order_ids:
            return jsonify({'success': False, 'message': '请选择要删除的订单'}), 400
        
        # 批量删除订单
        deleted_count = Order.query.filter(Order.id.in_(order_ids)).delete(synchronize_session=False)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'成功删除 {deleted_count} 个订单'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# ==================== Dashboard页面路由 ====================

@app.route('/dashboard')
def dashboard_index():
    """
    Dashboard主页路由 - 显示订单列表
    
    功能：
    - 支持按多种字段排序
    - 支持按平台筛选
    - 支持显示/隐藏已完成订单
    - 计算订单统计信息
    """
    
    # 获取URL参数
    sort_by = request.args.get('sort', 'needed_date')  # 排序字段
    order = request.args.get('order', 'asc')  # 排序方向
    show_completed = request.args.get('show_completed', 'false') == 'true'  # 是否显示已完成
    platform_filter = request.args.get('platform', '')  # 平台筛选
    
    # 构建数据库查询
    query = Order.query
    
    # 平台筛选
    if platform_filter:
        query = query.filter(Order.contact == platform_filter)
    
    # 排序
    if sort_by == 'needed_date':
        if order == 'desc':
            orders = query.order_by(Order.needed_date.desc()).all()
        else:
            orders = query.order_by(Order.needed_date.asc()).all()
    elif sort_by == 'order_date':
        if order == 'desc':
            orders = query.order_by(Order.order_date.desc()).all()
        else:
            orders = query.order_by(Order.order_date.asc()).all()
    else:
        orders = query.order_by(Order.needed_date.asc()).all()
    
    # 将订单对象转换为字典以便JSON序列化
    orders_dict = []
    for order in orders:
        orders_dict.append({
            'id': order.id,
            'cn': order.cn,
            'character': order.character,
            'contact': order.contact,
            'needed_date': order.needed_date.strftime('%Y-%m-%d'),
            'order_date': order.order_date.strftime('%Y-%m-%d'),
            'deposit_paid': bool(order.deposit_paid),
            'final_amount': order.final_amount,
            'shipping_included': bool(order.shipping_included),
            'blank_purchased': bool(order.blank_purchased),
            'status': order.status
        })
    
    return render_template('dashboard_index.html', orders=orders, orders_json=json.dumps(orders_dict), sort_by=sort_by, order=order, show_completed=show_completed, platform_filter=platform_filter)

@app.route('/analytics')
def analytics():
    """
    订单分析页面
    
    功能：
    - 显示业务指标
    - 图表分析
    - TOP5列表
    """
    orders = Order.query.all()
    
    # 计算基本统计
    total_orders = len(orders)
    completed_orders = len([o for o in orders if o.status in ['已完成', '已发货']])
    total_revenue = sum([o.final_amount for o in orders if o.status in ['已完成', '已发货']])
    avg_order_value = total_revenue / completed_orders if completed_orders > 0 else 0
    
    # 准备图表数据
    status_chart_data = {
        'labels': ['待制作', '已完成', '已发货', '已取消'],
        'data': [
            len([o for o in orders if o.status == '待制作']),
            len([o for o in orders if o.status == '已完成']),
            len([o for o in orders if o.status == '已发货']),
            len([o for o in orders if o.status == '已取消'])
        ]
    }
    
    platform_chart_data = {
        'labels': ['QQ', '微信', '闲鱼'],
        'orders': [
            len([o for o in orders if o.contact == 'QQ']),
            len([o for o in orders if o.contact == '微信']),
            len([o for o in orders if o.contact == '闲鱼'])
        ],
        'revenue': [
            sum([o.final_amount for o in orders if o.contact == 'QQ' and o.status in ['已完成', '已发货']]),
            sum([o.final_amount for o in orders if o.contact == '微信' and o.status in ['已完成', '已发货']]),
            sum([o.final_amount for o in orders if o.contact == '闲鱼' and o.status in ['已完成', '已发货']])
        ]
    }
    
    return render_template('analytics.html',
                         total_orders=total_orders,
                         completed_orders=completed_orders,
                         total_revenue=total_revenue,
                         avg_order_value=avg_order_value,
                         status_chart_data=json.dumps(status_chart_data),
                         platform_chart_data=json.dumps(platform_chart_data),
                         order_growth=12.5,
                         completion_rate=85.2,
                         completion_growth=3.2,
                         avg_completion_days=7,
                         completion_days_change=1,
                         customer_satisfaction=94.8,
                         efficiency_score=92,
                         quality_score=96,
                         on_time_rate=88,
                         risk_orders=3)

@app.route('/inventory')
def inventory():
    """
    材料库存页面
    
    功能：
    - 库存管理
    - 低库存提醒
    """
    # 模拟库存数据
    inventory_items = [
        {'name': '白色毛坯', 'stock': 15, 'min_stock': 10, 'unit': '个'},
        {'name': '黑色毛坯', 'stock': 8, 'min_stock': 10, 'unit': '个'},
        {'name': '金色喷漆', 'stock': 3, 'min_stock': 5, 'unit': '瓶'},
        {'name': '银色喷漆', 'stock': 12, 'min_stock': 5, 'unit': '瓶'},
    ]
    
    return render_template('inventory.html', inventory_items=inventory_items)

@app.route('/calendar')
def calendar():
    """
    订单日历页面
    
    功能：
    - 以日历形式显示订单
    - 按紧急程度标记颜色
    - 显示月度统计信息
    """
    # 获取所有订单
    orders = Order.query.order_by(Order.needed_date.asc()).all()
    
    # 转换为JSON格式
    orders_json = []
    for order in orders:
        orders_json.append({
            'id': order.id,
            'cn': order.cn,
            'character': order.character,
            'contact': order.contact,
            'needed_date': order.needed_date.strftime('%Y-%m-%d'),
            'order_date': order.order_date.strftime('%Y-%m-%d'),
            'status': order.status,
            'final_amount': order.final_amount
        })
    
    # 计算统计信息
    today = date.today()
    current_month_orders = [o for o in orders if o.needed_date.month == today.month and o.needed_date.year == today.year]
    
    urgent_orders = []
    overdue_orders = []
    completed_orders = []
    
    for order in orders:
        days_left = (order.needed_date - today).days
        if order.status in ['已完成', '已发货']:
            completed_orders.append(order)
        elif days_left < 0:
            overdue_orders.append(order)
        elif days_left <= 7:
            urgent_orders.append(order)
    
    return render_template('calendar.html', 
                         orders_json=orders_json,
                         current_date=today,
                         current_month_orders=current_month_orders,
                         urgent_orders=urgent_orders,
                         overdue_orders=overdue_orders,
                         completed_orders=completed_orders)

@app.route('/revenue')
def revenue():
    """
    收入统计页面
    
    功能：
    - 显示总收入和各项统计
    - 按平台分析收入分布
    - 月度收入趋势图表
    """
    from collections import defaultdict
    import calendar
    
    # 获取所有已完成的订单
    completed_orders = Order.query.filter(Order.status.in_(['已完成', '已发货'])).all()
    
    # 计算总收入
    total_revenue = sum(order.final_amount for order in completed_orders)
    
    # 计算平均订单价值
    avg_order_value = total_revenue / len(completed_orders) if completed_orders else 0
    
    # 计算待收款订单
    pending_orders_list = Order.query.filter(Order.status.notin_(['已完成', '已发货', '已取消'])).all()
    pending_orders = len(pending_orders_list)
    pending_revenue = sum(order.final_amount for order in pending_orders_list)
    
    # 按平台统计收入
    platform_revenue = defaultdict(lambda: {'revenue': 0, 'orders': 0})
    for order in completed_orders:
        platform_revenue[order.contact]['revenue'] += order.final_amount
        platform_revenue[order.contact]['orders'] += 1
    
    # 格式化平台收入数据
    platform_revenue_formatted = {}
    for platform, data in platform_revenue.items():
        platform_revenue_formatted[platform] = {
            'revenue': f"{data['revenue']:.0f}",
            'orders': data['orders']
        }
    
    # 按月统计收入
    monthly_revenue = defaultdict(lambda: {'revenue': 0, 'orders': 0})
    for order in completed_orders:
        month_key = order.needed_date.strftime('%Y-%m')
        monthly_revenue[month_key]['revenue'] += order.final_amount
        monthly_revenue[month_key]['orders'] += 1
    
    # 生成月度数据
    monthly_data = []
    monthly_chart_data = {'labels': [], 'data': []}
    
    sorted_months = sorted(monthly_revenue.keys())
    prev_revenue = 0
    
    for month_key in sorted_months:
        data = monthly_revenue[month_key]
        year, month = month_key.split('-')
        month_name = f"{year}年{int(month)}月"
        
        # 计算环比增长
        growth = 0
        if prev_revenue > 0:
            growth = ((data['revenue'] - prev_revenue) / prev_revenue) * 100
        
        monthly_data.append({
            'month': month_name,
            'orders': data['orders'],
            'revenue': f"{data['revenue']:.0f}",
            'avg_value': f"{data['revenue'] / data['orders']:.0f}" if data['orders'] > 0 else "0",
            'growth': f"{growth:.1f}" if growth != 0 else "0"
        })
        
        monthly_chart_data['labels'].append(month_name)
        monthly_chart_data['data'].append(data['revenue'])
        
        prev_revenue = data['revenue']
    
    return render_template('revenue.html',
                         total_revenue=f"{total_revenue:.0f}",
                         completed_orders=len(completed_orders),
                         avg_order_value=f"{avg_order_value:.0f}",
                         pending_orders=pending_orders,
                         pending_revenue=f"{pending_revenue:.0f}",
                         platform_revenue=platform_revenue_formatted,
                         monthly_data=monthly_data,
                         monthly_chart_data=monthly_chart_data)

# 添加模板上下文处理器
# ==================== 模板上下文处理器 ====================

@app.route('/timesheet')
def timesheet():
    """
    工时记录页面
    
    功能：
    - 显示工时统计
    - 计时器功能
    - 工时记录管理
    """
    # 模拟工时数据（实际应用中应从数据库获取）
    time_entries = [
        {
            'id': 1,
            'task_name': '角色A制作',
            'order_info': '订单 #001',
            'start_time': '09:00',
            'end_time': '12:30',
            'duration': '3.5h',
            'status': 'completed',
            'icon': 'brush',
            'date': '2024-01-15'
        },
        {
            'id': 2,
            'task_name': '角色B制作',
            'order_info': '订单 #002',
            'start_time': '14:00',
            'end_time': None,
            'duration': '2.0h',
            'status': 'working',
            'icon': 'palette',
            'date': '2024-01-15'
        },
        {
            'id': 3,
            'task_name': '角色C制作',
            'order_info': '订单 #003',
            'start_time': '10:30',
            'end_time': '11:45',
            'duration': '1.25h',
            'status': 'paused',
            'icon': 'scissors',
            'date': '2024-01-14'
        }
    ]
    
    # 计算工时统计
    today_hours = '6.5h'
    week_hours = '32.5h'
    month_hours = '128h'
    avg_daily_hours = '6.4h'
    
    return render_template('timesheet.html',
                         time_entries=time_entries,
                         today_hours=today_hours,
                         week_hours=week_hours,
                         month_hours=month_hours,
                         avg_daily_hours=avg_daily_hours)

@app.route('/settings')
def settings():
    """
    系统设置页面
    
    功能：
    - 背景设置
    - 系统配置
    - 用户偏好设置
    """
    return render_template('settings.html')

@app.route('/fontawesome-free-7.0.0-web/<path:filename>')
def fontawesome_static(filename):
    """
    提供FontAwesome静态文件
    """
    return send_from_directory('fontawesome-free-7.0.0-web', filename)

@app.context_processor
def inject_today():
    """
    向所有模板注入当前日期
    
    使模板可以直接使用 today 变量
    """
    return dict(today=date.today())

# ==================== 应用启动 ====================

if __name__ == '__main__':
    # 创建应用上下文并初始化数据库
    with app.app_context():
        db.create_all()  # 创建所有数据表
    
    # 启动开发服务器
    app.run(
        debug=True,        # 开启调试模式
        host='0.0.0.0',    # 监听所有网络接口
        port=5000          # 端口号
    )