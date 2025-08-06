#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
07妙妙屋订单管理系统 - 数据管理工具

功能模块：
1. 数据导出 - 支持JSON和CSV格式
2. 数据导入 - 从JSON文件恢复数据
3. 数据库备份 - 完整备份SQLite数据库
4. 数据库恢复 - 从备份文件恢复数据库
5. 数据库信息查看 - 显示统计信息

使用方法：
    python data_manager.py
"""

import json
import csv
import sqlite3
import shutil
from datetime import datetime, date
import os
from app import app, db, Order

def export_to_json(filename=None):
    """
    导出所有订单数据到JSON文件
    
    Args:
        filename (str, optional): 输出文件名，默认为带时间戳的文件名
    
    Returns:
        str: 导出的文件名
    """
    # 生成默认文件名（包含时间戳）
    if filename is None:
        filename = f"orders_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with app.app_context():
        # 查询所有订单
        orders = Order.query.all()
        orders_data = []
        
        # 将订单对象转换为字典格式
        for order in orders:
            orders_data.append({
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
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'status': order.status
            })
    
    # 写入JSON文件
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(orders_data, f, ensure_ascii=False, indent=2)
    
    print(f"数据已导出到: {filename}")
    print(f"共导出 {len(orders_data)} 条订单记录")
    return filename

def export_to_csv(filename=None):
    """
    导出所有订单数据到CSV文件（Excel兼容格式）
    
    Args:
        filename (str, optional): 输出文件名，默认为带时间戳的文件名
    
    Returns:
        str: 导出的文件名
    """
    # 生成默认文件名（包含时间戳）
    if filename is None:
        filename = f"orders_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with app.app_context():
        # 查询所有订单
        orders = Order.query.all()
        
        # 使用utf-8-sig编码确保Excel正确显示中文
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            # 定义CSV列标题（中文）
            fieldnames = ['ID', 'CN', '动漫角色', '联系方式', '客户排单', 'DDL', 
                         '定金已付', '尾款金额', '尾款含邮', '毛坯已购', '创建时间', '订单状态']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # 写入表头
            writer.writeheader()
            
            # 写入订单数据
            for order in orders:
                writer.writerow({
                    'ID': order.id,
                    'CN': order.cn,
                    '动漫角色': order.character,
                    '联系方式': order.contact,
                    '客户排单': order.needed_date.strftime('%Y-%m-%d'),
                    'DDL': order.order_date.strftime('%Y-%m-%d'),
                    '定金已付': '是' if order.deposit_paid else '否',
                    '尾款金额': order.final_amount,
                    '尾款含邮': '是' if order.shipping_included else '否',
                    '毛坯已购': '是' if order.blank_purchased else '否',
                    '创建时间': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    '订单状态': order.status
                })
    
    print(f"数据已导出到: {filename}")
    print(f"共导出 {len(orders)} 条订单记录")
    return filename

def import_from_json(filename):
    """
    从JSON文件导入订单数据到数据库
    
    Args:
        filename (str): JSON文件路径
    
    Returns:
        bool: 导入是否成功
    """
    # 检查文件是否存在
    if not os.path.exists(filename):
        print(f"文件不存在: {filename}")
        return False
    
    try:
        # 读取JSON文件
        with open(filename, 'r', encoding='utf-8') as f:
            orders_data = json.load(f)
        
        with app.app_context():
            # 询问是否清空现有数据
            confirm = input("是否清空现有数据？(y/N): ")
            if confirm.lower() == 'y':
                Order.query.delete()
                db.session.commit()
                print("已清空现有数据")
            
            imported_count = 0
            # 逐条导入订单数据
            for order_data in orders_data:
                try:
                    # 检查是否已存在相同ID的订单（避免重复导入）
                    existing_order = Order.query.get(order_data['id'])
                    if existing_order and confirm.lower() != 'y':
                        print(f"跳过重复订单 ID: {order_data['id']}")
                        continue
                    
                    # 创建新订单对象
                    order = Order(
                        cn=order_data['cn'],
                        character=order_data['character'],
                        contact=order_data['contact'],
                        needed_date=datetime.strptime(order_data['needed_date'], '%Y-%m-%d').date(),
                        order_date=datetime.strptime(order_data['order_date'], '%Y-%m-%d').date(),
                        deposit_paid=order_data['deposit_paid'],
                        final_amount=order_data['final_amount'],
                        shipping_included=order_data['shipping_included'],
                        blank_purchased=order_data['blank_purchased'],
                        status=order_data['status']
                    )
                    
                    # 如果备份文件包含创建时间，保持原始时间
                    if 'created_at' in order_data:
                        order.created_at = datetime.strptime(order_data['created_at'], '%Y-%m-%d %H:%M:%S')
                    
                    db.session.add(order)
                    imported_count += 1
                    
                except Exception as e:
                    print(f"导入订单失败: {order_data.get('cn', 'Unknown')} - {str(e)}")
                    continue
            
            # 提交所有更改
            db.session.commit()
            print(f"成功导入 {imported_count} 条订单记录")
            return True
            
    except Exception as e:
        print(f"导入失败: {str(e)}")
        return False

def backup_database(backup_dir="backups"):
    """
    备份SQLite数据库文件
    
    Args:
        backup_dir (str): 备份目录，默认为'backups'
    
    Returns:
        str or False: 成功时返回备份文件路径，失败时返回False
    """
    # 确保备份目录存在
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # 数据库文件路径
    db_path = "instance/coswig_orders.db"
    if not os.path.exists(db_path):
        print("数据库文件不存在")
        return False
    
    # 生成带时间戳的备份文件名
    backup_filename = f"coswig_orders_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        # 复制数据库文件到备份目录
        shutil.copy2(db_path, backup_path)
        print(f"数据库已备份到: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"备份失败: {str(e)}")
        return False

def restore_database(backup_file):
    """
    从备份文件恢复数据库
    
    Args:
        backup_file (str): 备份文件路径
    
    Returns:
        bool: 恢复是否成功
    """
    # 检查备份文件是否存在
    if not os.path.exists(backup_file):
        print(f"备份文件不存在: {backup_file}")
        return False
    
    db_path = "instance/coswig_orders.db"
    
    # 在恢复前备份当前数据库（安全措施）
    if os.path.exists(db_path):
        current_backup = f"coswig_orders_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(db_path, current_backup)
        print(f"当前数据库已备份为: {current_backup}")
    
    try:
        # 用备份文件替换当前数据库
        shutil.copy2(backup_file, db_path)
        print(f"数据库已从 {backup_file} 恢复")
        return True
    except Exception as e:
        print(f"恢复失败: {str(e)}")
        return False

def show_database_info():
    """
    显示数据库详细信息和统计数据
    
    包括文件信息、订单总数和按状态分类统计
    """
    db_path = "instance/coswig_orders.db"
    
    print("=== 数据库信息 ===")
    print(f"数据库位置: {os.path.abspath(db_path)}")
    
    if os.path.exists(db_path):
        # 显示文件基本信息
        file_size = os.path.getsize(db_path)
        print(f"文件大小: {file_size} 字节 ({file_size/1024:.2f} KB)")
        
        # 获取文件修改时间
        mtime = os.path.getmtime(db_path)
        print(f"最后修改: {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 获取订单统计信息
        with app.app_context():
            total_orders = Order.query.count()
            print(f"总订单数: {total_orders}")
            
            # 按状态统计订单数量
            if total_orders > 0:
                statuses = ['待制作', '制作中', '已完成', '已发货', '已取消']
                print("\n按状态统计:")
                for status in statuses:
                    count = Order.query.filter(Order.status == status).count()
                    if count > 0:
                        print(f"  {status}: {count}")
    else:
        print("数据库文件不存在")

def main():
    """
    数据管理工具主菜单
    
    提供交互式命令行界面，支持数据导入导出、备份恢复等操作
    """
    while True:
        # 显示主菜单
        print("\n=== 07妙妙屋数据管理工具 ===")
        print("1. 查看数据库信息")
        print("2. 导出数据到JSON")
        print("3. 导出数据到CSV")
        print("4. 从JSON导入数据")
        print("5. 备份数据库")
        print("6. 恢复数据库")
        print("0. 退出")
        
        choice = input("\n请选择操作 (0-6): ").strip()
        
        # 处理用户选择
        if choice == '0':
            print("再见！")
            break
        elif choice == '1':
            show_database_info()
        elif choice == '2':
            filename = input("输入文件名 (留空使用默认名): ").strip()
            export_to_json(filename if filename else None)
        elif choice == '3':
            filename = input("输入文件名 (留空使用默认名): ").strip()
            export_to_csv(filename if filename else None)
        elif choice == '4':
            filename = input("输入JSON文件路径: ").strip()
            if filename:
                import_from_json(filename)
        elif choice == '5':
            backup_dir = input("输入备份目录 (留空使用默认 'backups'): ").strip()
            backup_database(backup_dir if backup_dir else "backups")
        elif choice == '6':
            backup_file = input("输入备份文件路径: ").strip()
            if backup_file:
                restore_database(backup_file)
        else:
            print("无效选择，请重试")

# ==================== 程序入口 ====================

if __name__ == '__main__':
    main()