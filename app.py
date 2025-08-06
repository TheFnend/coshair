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

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, date
import os

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
    
    # 根据参数筛选订单
    if not show_completed:
        query = query.filter(Order.status.notin_(['已完成', '已发货']))
    
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
            'deposit_paid': order.deposit_paid,
            'final_amount': order.final_amount,
            'shipping_included': order.shipping_included,
            'blank_purchased': order.blank_purchased,
            'status': order.status
        })
    
    return render_template('index.html', orders=orders, orders_json=orders_dict, sort_by=sort_by, order=order, show_completed=show_completed, platform_filter=platform_filter)

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

# 添加模板上下文处理器
# ==================== 模板上下文处理器 ====================

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