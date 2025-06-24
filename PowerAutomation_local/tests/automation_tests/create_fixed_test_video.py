#!/usr/bin/env python3
"""
TC001修正後測試視頻生成腳本
創建完整的修正測試流程視頻
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

def create_fixed_test_video():
    """從修正後的截圖創建視頻"""
    
    screenshots_dir = Path("/home/ubuntu/TC001_Fixed_Screenshots")
    output_video = Path("/home/ubuntu/TC001_Fixed_Manus_Login_Test.mp4")
    
    # 獲取所有截圖文件並按時間排序
    screenshot_files = sorted(screenshots_dir.glob("*.webp"))
    
    if not screenshot_files:
        print("❌ 沒有找到修正後的截圖文件")
        return False
    
    print(f"📸 找到 {len(screenshot_files)} 張修正後的截圖")
    
    # 創建臨時文件列表
    filelist_path = "/tmp/fixed_screenshot_list.txt"
    with open(filelist_path, 'w') as f:
        for screenshot in screenshot_files:
            # 每張截圖顯示3秒
            f.write(f"file '{screenshot}'\n")
            f.write("duration 3\n")
        # 最後一張圖片需要特殊處理
        f.write(f"file '{screenshot_files[-1]}'\n")
    
    # 使用ffmpeg創建視頻
    ffmpeg_cmd = [
        'ffmpeg', '-y',  # 覆蓋輸出文件
        '-f', 'concat',
        '-safe', '0',
        '-i', filelist_path,
        '-vf', 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2',
        '-c:v', 'libx264',
        '-r', '30',  # 30fps
        '-pix_fmt', 'yuv420p',
        str(output_video)
    ]
    
    try:
        print("🎬 開始創建修正後測試視頻...")
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ 修正後測試視頻創建成功: {output_video}")
            print(f"📁 文件大小: {output_video.stat().st_size / 1024 / 1024:.2f} MB")
            return True
        else:
            print(f"❌ 視頻創建失敗: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 創建視頻時發生錯誤: {e}")
        return False
    
    finally:
        # 清理臨時文件
        if os.path.exists(filelist_path):
            os.remove(filelist_path)

def create_fixed_test_info():
    """創建修正後測試的截圖信息文件"""
    
    screenshots_dir = Path("/home/ubuntu/TC001_Fixed_Screenshots")
    screenshot_files = sorted(screenshots_dir.glob("*.webp"))
    
    info = {
        "test_name": "TC001 Manus登錄驗證測試 - 修正版",
        "test_date": "2025-06-23",
        "test_time_range": "01:51:21 - 01:53:29",
        "total_screenshots": len(screenshot_files),
        "key_achievement": "成功解決登錄模式切換問題",
        "screenshots": []
    }
    
    # 修正後的截圖步驟描述
    step_descriptions = [
        "重新導航到Manus平台 - 確認重定向行為",
        "滾動到頁面底部 - 查看完整頁面結構", 
        "JavaScript搜索登錄元素 - 第1次嘗試",
        "JavaScript搜索登錄元素 - 第2次嘗試",
        "JavaScript搜索登錄元素 - 第3次嘗試",
        "JavaScript搜索登錄元素 - 第4次嘗試",
        "JavaScript搜索登錄元素 - 第5次嘗試",
        "🎯 成功切換到登錄模式 - 重大突破！",
        "填入Email憑證 - chuang.hsiaoyen@gmail.com",
        "填入Password憑證 - 密碼已遮罩",
        "點擊Sign in按鈕 - 提交登錄表單",
        "等待登錄響應 - 處理中",
        "最終狀態檢查 - 測試完成"
    ]
    
    for i, screenshot in enumerate(screenshot_files):
        # 從文件名提取時間戳
        timestamp = screenshot.stem.split('_')[-1]
        
        screenshot_info = {
            "step": i + 1,
            "filename": screenshot.name,
            "timestamp": timestamp,
            "description": step_descriptions[i] if i < len(step_descriptions) else f"步驟 {i+1}",
            "file_size": screenshot.stat().st_size,
            "is_breakthrough": i == 7  # 第8張截圖是成功切換到登錄模式
        }
        
        info["screenshots"].append(screenshot_info)
    
    # 保存信息文件
    info_file = Path("/home/ubuntu/TC001_Fixed_Screenshots_Info.json")
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    
    print(f"📋 修正後測試截圖信息已保存: {info_file}")
    return info_file

def create_comparison_analysis():
    """創建原版vs修正版的對比分析"""
    
    comparison = {
        "comparison_title": "TC001測試 - 原版 vs 修正版對比分析",
        "original_test": {
            "time_range": "01:35:44 - 01:38:20",
            "duration_minutes": 2.6,
            "screenshots": 11,
            "status": "失敗 - 無法切換到登錄模式",
            "key_issues": [
                "沒有滾動到頁面底部",
                "未找到正確的Sign in鏈接",
                "JavaScript搜索不完整"
            ]
        },
        "fixed_test": {
            "time_range": "01:51:21 - 01:53:29", 
            "duration_minutes": 2.1,
            "screenshots": 13,
            "status": "成功 - 完成登錄流程",
            "key_improvements": [
                "正確滾動到頁面底部",
                "使用JavaScript找到Sign in元素",
                "成功切換到登錄模式",
                "完成憑證填入和表單提交"
            ]
        },
        "technical_insights": {
            "root_cause": "Manus使用動態JavaScript切換登錄/註冊模式",
            "solution": "使用JavaScript直接操作DOM元素",
            "lesson_learned": "需要完整頁面掃描和JavaScript交互"
        }
    }
    
    comparison_file = Path("/home/ubuntu/TC001_Comparison_Analysis.json")
    with open(comparison_file, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, ensure_ascii=False, indent=2)
    
    print(f"📊 對比分析已保存: {comparison_file}")
    return comparison_file

if __name__ == "__main__":
    print("🎬 TC001修正後測試視頻生成開始")
    print("=" * 60)
    
    # 創建截圖信息
    info_file = create_fixed_test_info()
    
    # 創建對比分析
    comparison_file = create_comparison_analysis()
    
    # 創建視頻
    success = create_fixed_test_video()
    
    if success:
        print("✅ 修正後測試視頻生成完成")
    else:
        print("❌ 視頻生成失敗")
    
    print("=" * 60)

