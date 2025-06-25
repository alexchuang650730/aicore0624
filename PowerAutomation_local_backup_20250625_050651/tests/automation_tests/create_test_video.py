#!/usr/bin/env python3
"""
TC001測試視頻生成腳本
使用截圖創建測試流程視頻
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

def create_video_from_screenshots():
    """從截圖創建視頻"""
    
    screenshots_dir = Path("/home/ubuntu/TC001_Screenshots")
    output_video = Path("/home/ubuntu/TC001_Manus_Login_Test.mp4")
    
    # 獲取所有截圖文件並按時間排序
    screenshot_files = sorted(screenshots_dir.glob("*.webp"))
    
    if not screenshot_files:
        print("❌ 沒有找到截圖文件")
        return False
    
    print(f"📸 找到 {len(screenshot_files)} 張截圖")
    
    # 創建臨時文件列表
    filelist_path = "/tmp/screenshot_list.txt"
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
        print("🎬 開始創建視頻...")
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ 視頻創建成功: {output_video}")
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

def create_screenshot_info():
    """創建截圖信息文件"""
    
    screenshots_dir = Path("/home/ubuntu/TC001_Screenshots")
    screenshot_files = sorted(screenshots_dir.glob("*.webp"))
    
    info = {
        "test_name": "TC001 Manus登錄驗證測試",
        "test_date": "2025-06-23",
        "total_screenshots": len(screenshot_files),
        "screenshots": []
    }
    
    # 截圖步驟描述
    step_descriptions = [
        "初始導航到Manus平台",
        "頁面滾動查看完整內容", 
        "嘗試點擊Sign in鏈接",
        "重新導航嘗試登錄模式",
        "再次導航到應用頁面",
        "滾動並查看頁面元素",
        "使用JavaScript查找Sign in鏈接 (執行前)",
        "使用JavaScript查找Sign in鏈接 (執行中)",
        "使用JavaScript查找Sign in鏈接 (執行後)",
        "填入登錄憑證 - Email",
        "填入登錄憑證 - Password"
    ]
    
    for i, screenshot in enumerate(screenshot_files):
        # 從文件名提取時間戳
        timestamp = screenshot.stem.split('_')[-1]
        
        screenshot_info = {
            "step": i + 1,
            "filename": screenshot.name,
            "timestamp": timestamp,
            "description": step_descriptions[i] if i < len(step_descriptions) else f"步驟 {i+1}",
            "file_size": screenshot.stat().st_size
        }
        
        info["screenshots"].append(screenshot_info)
    
    # 保存信息文件
    info_file = Path("/home/ubuntu/TC001_Screenshots_Info.json")
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    
    print(f"📋 截圖信息已保存: {info_file}")
    return info_file

if __name__ == "__main__":
    print("🎬 TC001測試視頻生成開始")
    print("=" * 50)
    
    # 創建截圖信息
    info_file = create_screenshot_info()
    
    # 創建視頻
    success = create_video_from_screenshots()
    
    if success:
        print("✅ 所有文件生成完成")
    else:
        print("❌ 視頻生成失敗")
    
    print("=" * 50)
