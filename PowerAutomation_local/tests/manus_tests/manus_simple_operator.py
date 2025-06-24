#!/usr/bin/env python3
"""
Manus操作簡化腳本
提供簡單的命令行界面來操作Manus頁面
"""

import asyncio
import argparse
import sys
from pathlib import Path

# 導入主要操作類
from manus_playwright_operator import ManusPlaywrightOperator

async def extract_conversations(operator):
    """提取對話歷史"""
    print("📜 正在提取對話歷史...")
    conversations = await operator.extract_conversation_history()
    
    print(f"✅ 成功提取 {len(conversations)} 條對話")
    
    # 顯示最近5條對話
    if conversations:
        print("\n📋 最近的對話:")
        for conv in conversations[-5:]:
            print(f"  [{conv.timestamp.strftime('%H:%M')}] {conv.sender}: {conv.content[:50]}...")
    
    return conversations

async def extract_tasks(operator):
    """提取任務列表"""
    print("📋 正在提取任務列表...")
    tasks = await operator.extract_task_list()
    
    print(f"✅ 成功提取 {len(tasks)} 個任務")
    
    # 顯示任務摘要
    if tasks:
        print("\n📊 任務摘要:")
        status_counts = {}
        for task in tasks:
            status_counts[task.status] = status_counts.get(task.status, 0) + 1
        
        for status, count in status_counts.items():
            print(f"  {status}: {count} 個")
    
    return tasks

async def batch_download(operator, output_dir):
    """批量下載"""
    print(f"📥 正在批量下載到 {output_dir}...")
    success = await operator.batch_download_data(output_dir)
    
    if success:
        print("✅ 批量下載完成")
    else:
        print("❌ 批量下載失敗")
    
    return success

async def send_message(operator, message):
    """發送消息"""
    print(f"📤 正在發送消息: {message[:30]}...")
    success = await operator.send_message(message)
    
    if success:
        print("✅ 消息發送成功")
    else:
        print("❌ 消息發送失敗")
    
    return success

async def monitor_tasks(operator, duration):
    """監控任務變化"""
    print(f"👁️ 開始監控任務變化 ({duration} 秒)...")
    
    change_count = 0
    
    async def change_callback(event_type, data):
        nonlocal change_count
        change_count += 1
        print(f"📊 檢測到變化 #{change_count}: {event_type}")
        
        if event_type == 'task_count_change':
            print(f"   任務數量: {data['old_count']} -> {data['new_count']}")
        elif event_type == 'task_status_change':
            print(f"   任務狀態: {data['task_id']} {data['old_status']} -> {data['new_status']}")
    
    # 啟動監控
    monitor_task = asyncio.create_task(
        operator.monitor_task_changes(callback=change_callback, interval=5)
    )
    
    # 等待指定時間
    await asyncio.sleep(duration)
    
    # 停止監控
    operator.stop_monitoring()
    
    print(f"✅ 監控完成，共檢測到 {change_count} 次變化")

async def interactive_mode(operator):
    """交互模式"""
    print("🎮 進入交互模式")
    print("可用命令:")
    print("  1 - 提取對話歷史")
    print("  2 - 提取任務列表")
    print("  3 - 批量下載")
    print("  4 - 發送消息")
    print("  5 - 監控任務 (30秒)")
    print("  q - 退出")
    
    while True:
        try:
            command = input("\n請輸入命令: ").strip()
            
            if command == 'q':
                break
            elif command == '1':
                await extract_conversations(operator)
            elif command == '2':
                await extract_tasks(operator)
            elif command == '3':
                output_dir = input("輸入下載目錄 (默認: manus_data): ").strip() or "manus_data"
                await batch_download(operator, output_dir)
            elif command == '4':
                message = input("輸入要發送的消息: ").strip()
                if message:
                    await send_message(operator, message)
                else:
                    print("❌ 消息不能為空")
            elif command == '5':
                await monitor_tasks(operator, 30)
            else:
                print("❌ 無效命令")
        
        except KeyboardInterrupt:
            print("\n👋 用戶中斷")
            break
        except Exception as e:
            print(f"❌ 執行命令時發生錯誤: {e}")

async def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='Manus Playwright操作工具')
    parser.add_argument('--url', default='https://manus.im/app/ogbxIEerutqP7e4NgIB7oQ', 
                       help='Manus頁面URL')
    parser.add_argument('--headless', action='store_true', help='無頭模式運行')
    parser.add_argument('--action', choices=['conversations', 'tasks', 'download', 'send', 'monitor', 'interactive'],
                       help='要執行的操作')
    parser.add_argument('--message', help='要發送的消息 (用於send操作)')
    parser.add_argument('--output', default='manus_data', help='下載輸出目錄')
    parser.add_argument('--duration', type=int, default=60, help='監控持續時間(秒)')
    
    args = parser.parse_args()
    
    # 創建操作器
    operator = ManusPlaywrightOperator(args.url)
    
    try:
        print(f"🚀 初始化Manus操作器...")
        print(f"📍 目標URL: {args.url}")
        
        # 初始化
        success = await operator.initialize(headless=args.headless)
        if not success:
            print("❌ 初始化失敗")
            return 1
        
        print("✅ 初始化成功")
        
        # 執行指定操作
        if args.action == 'conversations':
            await extract_conversations(operator)
        elif args.action == 'tasks':
            await extract_tasks(operator)
        elif args.action == 'download':
            await batch_download(operator, args.output)
        elif args.action == 'send':
            if not args.message:
                print("❌ 請使用 --message 指定要發送的消息")
                return 1
            await send_message(operator, args.message)
        elif args.action == 'monitor':
            await monitor_tasks(operator, args.duration)
        elif args.action == 'interactive':
            await interactive_mode(operator)
        else:
            # 默認執行所有操作
            print("🔄 執行完整操作流程...")
            
            await extract_conversations(operator)
            await extract_tasks(operator)
            await batch_download(operator, args.output)
            
            print("✅ 所有操作完成")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 用戶中斷")
        return 0
    except Exception as e:
        print(f"❌ 執行過程中發生錯誤: {e}")
        return 1
    finally:
        await operator.cleanup()

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

