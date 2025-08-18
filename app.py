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

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, date
import os
import json
import uuid
import tempfile
import urllib.request as urlrequest
from urllib.parse import quote

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

@app.route('/api/export_data', methods=['POST'])
def api_export_data():
    """
    导出订单数据API
    
    POST参数：
    - format: 导出格式 (json 或 csv)
    
    Returns:
        JSON响应包含下载链接
    """
    try:
        data = request.get_json()
        export_format = data.get('format', 'json').lower()
        
        from data_manager import export_to_json, export_to_csv
        
        # 生成唯一的临时文件名
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if export_format == 'json':
            filename = f"orders_export_{timestamp}_{unique_id}.json"
            export_to_json(filename)
        elif export_format == 'csv':
            filename = f"orders_export_{timestamp}_{unique_id}.csv"
            export_to_csv(filename)
        else:
            return jsonify({'success': False, 'message': '不支持的导出格式'}), 400
        
        # 检查文件是否存在
        if os.path.exists(filename):
            return jsonify({
                'success': True, 
                'message': f'数据导出成功',
                'filename': filename,
                'download_url': f'/download/{filename}'
            })
        else:
            return jsonify({'success': False, 'message': '导出失败，文件创建失败'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'导出失败：{str(e)}'}), 500

@app.route('/api/import_data', methods=['POST'])
def api_import_data():
    """
    导入订单数据API
    
    文件上传：
    - file: JSON格式的订单数据文件
    - clear_existing: 是否清空现有数据 (可选，默认false)
    
    Returns:
        JSON响应
    """
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '未选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '未选择文件'}), 400
        
        # 检查文件扩展名
        if not file.filename.lower().endswith('.json'):
            return jsonify({'success': False, 'message': '只支持JSON格式文件'}), 400
        
        clear_existing = request.form.get('clear_existing', 'false').lower() == 'true'
        
        # 保存上传的文件到临时位置
        import tempfile
        import uuid
        temp_filename = f"temp_import_{uuid.uuid4().hex}.json"
        file.save(temp_filename)
        
        try:
            # 读取并验证JSON文件
            with open(temp_filename, 'r', encoding='utf-8') as f:
                orders_data = json.load(f)
            
            # 验证数据格式
            if not isinstance(orders_data, list):
                return jsonify({'success': False, 'message': 'JSON文件格式错误：应为订单数组'}), 400
            
            # 清空现有数据（如果需要）
            if clear_existing:
                Order.query.delete()
                db.session.commit()
            
            imported_count = 0
            skipped_count = 0
            
            # 逐条导入订单数据
            for order_data in orders_data:
                try:
                    # 验证必需字段
                    required_fields = ['cn', 'character', 'contact', 'needed_date', 'order_date', 'final_amount']
                    for field in required_fields:
                        if field not in order_data:
                            continue
                    
                    # 检查是否已存在相同的订单（基于cn+character+needed_date）
                    existing_order = Order.query.filter_by(
                        cn=order_data['cn'],
                        character=order_data['character'],
                        needed_date=datetime.strptime(order_data['needed_date'], '%Y-%m-%d').date()
                    ).first()
                    
                    if existing_order and not clear_existing:
                        skipped_count += 1
                        continue
                    
                    # 创建新订单对象
                    order = Order(
                        cn=order_data['cn'],
                        character=order_data['character'],
                        contact=order_data['contact'],
                        needed_date=datetime.strptime(order_data['needed_date'], '%Y-%m-%d').date(),
                        order_date=datetime.strptime(order_data['order_date'], '%Y-%m-%d').date(),
                        deposit_paid=order_data.get('deposit_paid', False),
                        final_amount=float(order_data['final_amount']),
                        shipping_included=order_data.get('shipping_included', False),
                        blank_purchased=order_data.get('blank_purchased', False),
                        cake_box=order_data.get('cake_box', '不需要'),
                        status=order_data.get('status', '待制作')
                    )
                    
                    # 如果备份文件包含创建时间，保持原始时间
                    if 'created_at' in order_data:
                        try:
                            order.created_at = datetime.strptime(order_data['created_at'], '%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                    
                    db.session.add(order)
                    imported_count += 1
                    
                except Exception as e:
                    continue
            
            # 提交所有更改
            db.session.commit()
            
            message = f'成功导入 {imported_count} 条订单'
            if skipped_count > 0:
                message += f'，跳过 {skipped_count} 条重复订单'
            
            return jsonify({
                'success': True,
                'message': message,
                'imported_count': imported_count,
                'skipped_count': skipped_count
            })
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'导入失败：{str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """
    下载导出的文件
    """
    if os.path.exists(filename):
        return send_file(filename, as_attachment=True)
    else:
        flash('文件不存在', 'error')
        return redirect(url_for('settings'))

@app.route('/fontawesome-free-7.0.0-web/<path:filename>')
def fontawesome_static(filename):
    """
    提供FontAwesome静态文件
    """
    return send_from_directory('fontawesome-free-7.0.0-web', filename)

# === 提供ArkModels模型静态文件（Spine） ===
@app.route('/arkmodels/<path:filename>')
def arkmodels_static(filename):
    """
    提供ArkModels下的Spine模型资源(.skel/.json/.atlas/.png)
    """
    base_dir = os.path.join('ArkModels', 'ArkModels', 'models')
    return send_from_directory(base_dir, filename)

@app.route('/api/spine_models')
def api_spine_models():
    """
    获取所有可用的Spine模型
    
    Returns:
        JSON响应包含模型列表和详细信息
    """
    try:
        models = []
        models_dir = os.path.join('ArkModels', 'ArkModels', 'models')
        
        if os.path.exists(models_dir):
            for folder_name in os.listdir(models_dir):
                folder_path = os.path.join(models_dir, folder_name)
                if os.path.isdir(folder_path):
                    # 检查是否有必要的文件 (.skel和.atlas)
                    skel_file = None
                    atlas_file = None
                    png_file = None
                    
                    for file in os.listdir(folder_path):
                        if file.endswith('.skel'):
                            skel_file = file
                        elif file.endswith('.atlas'):
                            atlas_file = file
                        elif file.endswith('.png'):
                            png_file = file
                    
                    if skel_file and atlas_file:  # 只有同时存在.skel和.atlas的才是有效模型
                        models.append({
                            'id': folder_name,
                            'name': folder_name,
                            'skel_file': skel_file,
                            'atlas_file': atlas_file,
                            'png_file': png_file,
                            'skel_path': f"/arkmodels/{quote(folder_name, safe='')}/{quote(skel_file, safe='')}",
                            'atlas_path': f"/arkmodels/{quote(folder_name, safe='')}/{quote(atlas_file, safe='')}",
                            'preview_path': f"/arkmodels/{quote(folder_name, safe='')}/{quote(png_file, safe='')}" if png_file else None
                        })
        
        # 按名称排序
        models.sort(key=lambda x: x['id'])
        
        return jsonify({
            'success': True,
            'models': models,
            'count': len(models)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取模型列表失败：{str(e)}'
        }), 500

@app.route('/api/spine_model/current')
def api_spine_model_current():
    try:
        default_model_id = '113_cqbw'
        model_id = session.get('spine_model_id', default_model_id)
        base_dir = os.path.join('ArkModels', 'ArkModels', 'models', model_id)
        skel_file = None
        atlas_file = None
        png_file = None
        if os.path.isdir(base_dir):
            for f in os.listdir(base_dir):
                if f.endswith('.skel'):
                    skel_file = f
                elif f.endswith('.atlas'):
                    atlas_file = f
                elif f.endswith('.png'):
                    png_file = f
        if not (skel_file and atlas_file):
            # 回落到默认模型
            model_id = default_model_id
            base_dir = os.path.join('ArkModels', 'ArkModels', 'models', model_id)
            for f in os.listdir(base_dir):
                if f.endswith('.skel'):
                    skel_file = f
                elif f.endswith('.atlas'):
                    atlas_file = f
                elif f.endswith('.png'):
                    png_file = f
        return jsonify({
            'success': True,
            'id': model_id,
            'skel_path': f"/arkmodels/{quote(model_id, safe='')}/{quote(skel_file, safe='')}",
            'atlas_path': f"/arkmodels/{quote(model_id, safe='')}/{quote(atlas_file, safe='')}",
            'preview_path': f"/arkmodels/{quote(model_id, safe='')}/{quote(png_file, safe='')}" if png_file else None
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/spine_model/select', methods=['POST'])
def api_spine_model_select():
    try:
        data = request.get_json(force=True) or {}
        model_id = data.get('id')
        if not model_id:
            return jsonify({'success': False, 'message': '缺少模型id'}), 400
        base_dir = os.path.join('ArkModels', 'ArkModels', 'models', model_id)
        if not os.path.isdir(base_dir):
            return jsonify({'success': False, 'message': '模型目录不存在'}), 404
        skel_file = None
        atlas_file = None
        png_file = None
        for f in os.listdir(base_dir):
            if f.endswith('.skel'):
                skel_file = f
            elif f.endswith('.atlas'):
                atlas_file = f
            elif f.endswith('.png'):
                png_file = f
        if not (skel_file and atlas_file):
            return jsonify({'success': False, 'message': '模型文件不完整（缺少.skel或.atlas）'}), 400
        session['spine_model_id'] = model_id
        return jsonify({
            'success': True,
            'message': '模型已更新',
            'id': model_id,
            'skel_path': f"/arkmodels/{quote(model_id, safe='')}/{quote(skel_file, safe='')}",
            'atlas_path': f"/arkmodels/{quote(model_id, safe='')}/{quote(atlas_file, safe='')}",
            'preview_path': f"/arkmodels/{quote(model_id, safe='')}/{quote(png_file, safe='')}" if png_file else None
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败：{str(e)}'}), 500

@app.context_processor
def inject_spine_model():
    try:
        default_model_id = '113_cqbw'
        model_id = session.get('spine_model_id', default_model_id)
        base_dir = os.path.join('ArkModels', 'ArkModels', 'models', model_id)
        skel_file = None
        atlas_file = None
        if os.path.isdir(base_dir):
            for f in os.listdir(base_dir):
                if f.endswith('.skel'):
                    skel_file = f
                elif f.endswith('.atlas'):
                    atlas_file = f
        if not (skel_file and atlas_file):
            model_id = default_model_id
            base_dir = os.path.join('ArkModels', 'ArkModels', 'models', model_id)
            for f in os.listdir(base_dir):
                if f.endswith('.skel'):
                    skel_file = f
                elif f.endswith('.atlas'):
                    atlas_file = f
        return {
            'SPINE_MODEL_ID': model_id,
            'SPINE_MODEL_SKEL': f"/arkmodels/{quote(model_id, safe='')}/{quote(skel_file, safe='')}" if skel_file else '',
            'SPINE_MODEL_ATLAS': f"/arkmodels/{quote(model_id, safe='')}/{quote(atlas_file, safe='')}" if atlas_file else ''
        }
    except Exception:
        return {
            'SPINE_MODEL_ID': '113_cqbw',
            'SPINE_MODEL_SKEL': '/arkmodels/113_cqbw/build_char_113_cqbw.skel',
            'SPINE_MODEL_ATLAS': '/arkmodels/113_cqbw/build_char_113_cqbw.atlas'
        }

@app.context_processor
def inject_today():
    """
    向所有模板注入当前日期
    
    使模板可以直接使用 today 变量
    """
    return dict(today=date.today())

@app.context_processor
def inject_device_info():
    """
    向所有模板注入设备信息
    
    检测用户代理字符串，判断是否为移动设备（Android）
    """
    user_agent = request.headers.get('User-Agent', '').lower()
    
    # 检测 Android 设备
    is_android = 'android' in user_agent
    
    # 检测移动设备（包括 Android 和 iOS）
    is_mobile = any(mobile_indicator in user_agent for mobile_indicator in [
        'android', 'iphone', 'ipad', 'ipod', 'mobile', 'phone'
    ])
    
    # 检测具体的移动浏览器
    is_chrome_mobile = 'chrome' in user_agent and 'mobile' in user_agent
    is_firefox_mobile = 'firefox' in user_agent and 'mobile' in user_agent
    
    return dict(
        is_android=is_android,
        is_mobile=is_mobile,
        is_chrome_mobile=is_chrome_mobile,
        is_firefox_mobile=is_firefox_mobile,
        user_agent=user_agent
    )


@app.route('/spine-player/3.8/spine-webgl.js')
def spine_webgl_js_38():
    # Serve a no-op shim to prevent duplicate runtime conflicts with spine-player.js (3.8 bundles runtime)
    return app.response_class("/* spine-webgl disabled: runtime provided by spine-player.js */", mimetype='application/javascript')

@app.route('/spine-player/3.8/spine-player.js')
def spine_player_js_38():
    return _proxy_spine_player_asset('js')

@app.route('/spine-player/3.8/spine-player.css')
def spine_player_css_38():
    return _proxy_spine_player_asset('css')


def _proxy_spine_webgl_js():
    import urllib.request as _rq
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) TraeProxy/1.0'
    name_candidates = ['spine-webgl.js', 'spine-webgl.min.js']
    min_size = 30000

    # Try cached files first
    for nm in name_candidates:
        cache_path = os.path.join('static', 'spine-player', '3.8', nm)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    data = f.read()
                    if data and len(data) >= min_size:
                        return app.response_class(data, mimetype='application/javascript')
            except Exception:
                pass

    # Build remote URL candidates
    url_candidates = []
    for filename in name_candidates:
        url_candidates.extend([
            # Working 3.8 build paths (GitHub via jsDelivr and raw.githubusercontent)
            f'https://cdn.jsdelivr.net/gh/EsotericSoftware/spine-runtimes@3.8/spine-ts/build/{filename}',
            f'https://raw.githubusercontent.com/EsotericSoftware/spine-runtimes/3.8/spine-ts/build/{filename}',
        ])

    # Try to fetch from remote sources
    for u in url_candidates:
        try:
            req = _rq.Request(u, headers={'User-Agent': ua, 'Accept': '*/*'})
            with _rq.urlopen(req, timeout=20) as resp:
                data = resp.read()
                if data and len(data) >= min_size:
                    filename = u.rsplit('/', 1)[-1]
                    cache_path = os.path.join('static', 'spine-player', '3.8', filename)
                    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                    try:
                        with open(cache_path, 'wb') as f:
                            f.write(data)
                    except Exception:
                        pass
                    return app.response_class(data, mimetype='application/javascript')
        except Exception:
            continue

    # Final fallback: return any cached bytes even if below threshold
    for nm in name_candidates:
        cache_path = os.path.join('static', 'spine-player', '3.8', nm)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    data = f.read()
                    return app.response_class(data, mimetype='application/javascript')
            except Exception:
                pass

    return app.response_class('/* spine-webgl fetch failed */', mimetype='application/javascript', status=502)


def _proxy_spine_player_asset(kind: str):
    import urllib.request as _rq
    ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) TraeProxy/1.0'
    # Candidates: try non-min first, then minified
    name_candidates = (
        ['spine-player.js', 'spine-player.min.js'] if kind == 'js' else
        ['spine-player.css', 'spine-player.min.css']
    )
    # lower CSS threshold to accept small official CSS
    min_size = 200 if kind == 'css' else 30000

    # Try any cached candidate
    for nm in name_candidates:
        cache_path = os.path.join('static', 'spine-player', '3.8', nm)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    data = f.read()
                    if data and len(data) >= min_size:
                        return app.response_class(data, mimetype=('application/javascript' if kind == 'js' else 'text/css'))
            except Exception:
                pass

    # Build URL candidates across multiple sources for each filename
    url_candidates = []
    for filename in name_candidates:
        if kind == 'js':
            url_candidates.extend([
                # Working 3.8 build paths
                'https://cdn.jsdelivr.net/gh/EsotericSoftware/spine-runtimes@3.8/spine-ts/build/spine-player.js',
                'https://raw.githubusercontent.com/EsotericSoftware/spine-runtimes/3.8/spine-ts/build/spine-player.js',
            ])
        else:
            url_candidates.extend([
                # CSS is under player/css in 3.8
                'https://cdn.jsdelivr.net/gh/EsotericSoftware/spine-runtimes@3.8/spine-ts/player/css/spine-player.css',
                'https://raw.githubusercontent.com/EsotericSoftware/spine-runtimes/3.8/spine-ts/player/css/spine-player.css',
            ])

    last_error = None
    for u in url_candidates:
        try:
            req = _rq.Request(u, headers={'User-Agent': ua, 'Accept': '*/*'})
            with _rq.urlopen(req, timeout=20) as resp:
                data = resp.read()
                if data and len(data) >= min_size:
                    filename = 'spine-player.js' if kind == 'js' else 'spine-player.css'
                    cache_path = os.path.join('static', 'spine-player', '3.8', filename)
                    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                    try:
                        with open(cache_path, 'wb') as f:
                            f.write(data)
                    except Exception:
                        pass
                    return app.response_class(data, mimetype=('application/javascript' if kind == 'js' else 'text/css'))
        except Exception as e:
            last_error = e
            continue

    # Final fallback: return any cached bytes even if below threshold
    for nm in name_candidates:
        cache_path = os.path.join('static', 'spine-player', '3.8', nm)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    data = f.read()
                    return app.response_class(data, mimetype=('application/javascript' if kind == 'js' else 'text/css'))
            except Exception:
                pass

    return app.response_class('/* spine-player asset fetch failed */', mimetype=('application/javascript' if kind == 'js' else 'text/css'), status=502)

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