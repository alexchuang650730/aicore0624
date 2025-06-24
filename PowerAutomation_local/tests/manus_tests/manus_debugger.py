#!/usr/bin/env python3
"""
Manus頁面結構調試工具
幫助找到正確的選擇器
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

class ManusDebugger:
    def __init__(self, url="https://manus.im/app/ogbxIEerutqP7e4NgIB7oQ"):
        self.url = url
        self.playwright = None
        self.browser = None
        self.page = None
    
    async def initialize(self):
        """初始化"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        self.page = await self.browser.new_page()
        await self.page.goto(self.url, wait_until='networkidle')
        await asyncio.sleep(5)
    
    async def analyze_page_structure(self):
        """分析頁面結構"""
        print("🔍 分析頁面結構...")
        
        # 1. 獲取頁面基本信息
        title = await self.page.title()
        url = self.page.url
        print(f"📄 頁面標題: {title}")
        print(f"🌐 當前URL: {url}")
        
        # 2. 分析可能的對話容器
        print("\n📋 查找對話容器...")
        containers = await self._find_conversation_containers()
        
        # 3. 分析消息元素
        print("\n💬 查找消息元素...")
        messages = await self._find_message_elements()
        
        # 4. 分析輸入元素
        print("\n📝 查找輸入元素...")
        inputs = await self._find_input_elements()
        
        # 5. 生成報告
        await self._generate_debug_report(containers, messages, inputs)
    
    async def _find_conversation_containers(self):
        """查找對話容器"""
        selectors = [
            '.conversation', '.chat', '.messages', '.dialog',
            '[class*="conversation"]', '[class*="chat"]', '[class*="message"]',
            '[id*="conversation"]', '[id*="chat"]', '[id*="message"]',
            '.main-content', '.content', '.chat-container', '.message-container',
            '[role="main"]', '[role="dialog"]', '[role="log"]'
        ]
        
        found_containers = []
        
        for selector in selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                for i, element in enumerate(elements):
                    if await element.is_visible():
                        text_content = await element.inner_text()
                        if len(text_content) > 50:  # 有實際內容
                            class_name = await element.get_attribute('class') or ''
                            element_id = await element.get_attribute('id') or ''
                            tag_name = await element.evaluate('el => el.tagName')
                            
                            found_containers.append({
                                'selector': selector,
                                'index': i,
                                'tag': tag_name,
                                'class': class_name,
                                'id': element_id,
                                'text_length': len(text_content),
                                'text_preview': text_content[:100] + '...' if len(text_content) > 100 else text_content
                            })
                            
                            print(f"  ✅ {selector} - {tag_name}.{class_name} (文本長度: {len(text_content)})")
            except:
                continue
        
        return found_containers
    
    async def _find_message_elements(self):
        """查找消息元素"""
        selectors = [
            '.message', '.msg', '.chat-message', '.conversation-message',
            '[class*="message"]', '[class*="msg"]', '[class*="chat"]',
            '.bubble', '.chat-bubble', '.message-bubble',
            '[role="listitem"]', '[role="article"]',
            'div[data-message]', 'div[data-msg]',
            'p', 'div p', '.text', '.content'
        ]
        
        found_messages = []
        
        for selector in selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                visible_elements = []
                
                for element in elements:
                    if await element.is_visible():
                        text = await element.inner_text()
                        if text and len(text.strip()) > 5:  # 有意義的文本
                            visible_elements.append(element)
                
                if visible_elements:
                    # 分析前幾個元素
                    sample_size = min(3, len(visible_elements))
                    for i in range(sample_size):
                        element = visible_elements[i]
                        text = await element.inner_text()
                        class_name = await element.get_attribute('class') or ''
                        tag_name = await element.evaluate('el => el.tagName')
                        
                        found_messages.append({
                            'selector': selector,
                            'total_count': len(visible_elements),
                            'sample_index': i,
                            'tag': tag_name,
                            'class': class_name,
                            'text_preview': text[:80] + '...' if len(text) > 80 else text
                        })
                    
                    print(f"  ✅ {selector} - 找到 {len(visible_elements)} 個元素")
                    print(f"     示例: {found_messages[-1]['text_preview']}")
            except:
                continue
        
        return found_messages
    
    async def _find_input_elements(self):
        """查找輸入元素"""
        input_selectors = [
            'textarea', 'input[type="text"]', '[contenteditable="true"]',
            '.input', '.message-input', '.chat-input', '.compose',
            '[placeholder*="輸入"]', '[placeholder*="input"]', '[placeholder*="message"]',
            '[class*="input"]', '[class*="compose"]', '[class*="editor"]'
        ]
        
        button_selectors = [
            'button', '.button', '.btn', '.send', '.submit',
            '[type="submit"]', '[role="button"]',
            '[class*="send"]', '[class*="submit"]', '[class*="button"]'
        ]
        
        found_inputs = []
        
        # 查找輸入框
        print("  🔍 查找輸入框...")
        for selector in input_selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                for element in elements:
                    if await element.is_visible() and await element.is_enabled():
                        tag_name = await element.evaluate('el => el.tagName')
                        class_name = await element.get_attribute('class') or ''
                        placeholder = await element.get_attribute('placeholder') or ''
                        
                        found_inputs.append({
                            'type': 'input',
                            'selector': selector,
                            'tag': tag_name,
                            'class': class_name,
                            'placeholder': placeholder
                        })
                        
                        print(f"    ✅ 輸入框: {selector} - {tag_name} (placeholder: {placeholder})")
            except:
                continue
        
        # 查找按鈕
        print("  🔍 查找發送按鈕...")
        for selector in button_selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                for element in elements:
                    if await element.is_visible() and await element.is_enabled():
                        text = await element.inner_text()
                        class_name = await element.get_attribute('class') or ''
                        
                        # 檢查是否是發送按鈕
                        if any(keyword in text.lower() for keyword in ['send', '發送', 'submit', '提交']) or \
                           any(keyword in class_name.lower() for keyword in ['send', 'submit']):
                            found_inputs.append({
                                'type': 'button',
                                'selector': selector,
                                'text': text,
                                'class': class_name
                            })
                            
                            print(f"    ✅ 發送按鈕: {selector} - {text} ({class_name})")
            except:
                continue
        
        return found_inputs
    
    async def _generate_debug_report(self, containers, messages, inputs):
        """生成調試報告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"manus_debug_report_{timestamp}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'page_url': self.page.url,
            'page_title': await self.page.title(),
            'analysis': {
                'conversation_containers': containers,
                'message_elements': messages,
                'input_elements': inputs
            },
            'recommendations': self._generate_recommendations(containers, messages, inputs)
        }
        
        # 保存JSON報告
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 生成可讀報告
        readable_file = f"manus_debug_report_{timestamp}.txt"
        with open(readable_file, 'w', encoding='utf-8') as f:
            f.write("Manus頁面結構分析報告\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("📋 對話容器分析:\n")
            for container in containers:
                f.write(f"  選擇器: {container['selector']}\n")
                f.write(f"  元素: {container['tag']}.{container['class']}\n")
                f.write(f"  文本長度: {container['text_length']}\n")
                f.write(f"  預覽: {container['text_preview']}\n\n")
            
            f.write("💬 消息元素分析:\n")
            for msg in messages:
                f.write(f"  選擇器: {msg['selector']}\n")
                f.write(f"  數量: {msg['total_count']}\n")
                f.write(f"  預覽: {msg['text_preview']}\n\n")
            
            f.write("📝 輸入元素分析:\n")
            for inp in inputs:
                f.write(f"  類型: {inp['type']}\n")
                f.write(f"  選擇器: {inp['selector']}\n")
                if inp['type'] == 'input':
                    f.write(f"  Placeholder: {inp.get('placeholder', '')}\n")
                else:
                    f.write(f"  按鈕文本: {inp.get('text', '')}\n")
                f.write("\n")
        
        print(f"\n📊 調試報告已生成:")
        print(f"  📄 詳細報告: {report_file}")
        print(f"  📋 可讀報告: {readable_file}")
        
        # 顯示推薦選擇器
        recommendations = report['recommendations']
        print(f"\n💡 推薦的選擇器:")
        if recommendations['best_message_selector']:
            print(f"  💬 消息選擇器: {recommendations['best_message_selector']}")
        if recommendations['best_input_selector']:
            print(f"  📝 輸入選擇器: {recommendations['best_input_selector']}")
        if recommendations['best_button_selector']:
            print(f"  🔘 按鈕選擇器: {recommendations['best_button_selector']}")
    
    def _generate_recommendations(self, containers, messages, inputs):
        """生成推薦選擇器"""
        recommendations = {
            'best_message_selector': None,
            'best_input_selector': None,
            'best_button_selector': None,
            'notes': []
        }
        
        # 推薦最佳消息選擇器
        if messages:
            # 優先選擇數量多且有意義的選擇器
            best_msg = max(messages, key=lambda x: x['total_count'])
            recommendations['best_message_selector'] = best_msg['selector']
        
        # 推薦最佳輸入選擇器
        input_elements = [inp for inp in inputs if inp['type'] == 'input']
        if input_elements:
            # 優先選擇有placeholder的textarea
            textarea_inputs = [inp for inp in input_elements if inp['tag'] == 'TEXTAREA']
            if textarea_inputs:
                recommendations['best_input_selector'] = textarea_inputs[0]['selector']
            else:
                recommendations['best_input_selector'] = input_elements[0]['selector']
        
        # 推薦最佳按鈕選擇器
        button_elements = [inp for inp in inputs if inp['type'] == 'button']
        if button_elements:
            recommendations['best_button_selector'] = button_elements[0]['selector']
        
        return recommendations
    
    async def test_selectors(self):
        """測試推薦的選擇器"""
        print("\n🧪 測試選擇器...")
        
        # 測試消息提取
        test_selectors = [
            '.message', '.chat-message', '.conversation-message',
            '[class*="message"]', 'div[role="listitem"]', 'p'
        ]
        
        for selector in test_selectors:
            try:
                elements = await self.page.query_selector_all(selector)
                visible_count = 0
                sample_texts = []
                
                for element in elements[:5]:  # 只檢查前5個
                    if await element.is_visible():
                        text = await element.inner_text()
                        if text and len(text.strip()) > 5:
                            visible_count += 1
                            sample_texts.append(text[:50] + '...' if len(text) > 50 else text)
                
                if visible_count > 0:
                    print(f"  ✅ {selector}: {visible_count} 個可見元素")
                    for i, text in enumerate(sample_texts[:2]):
                        print(f"     示例 {i+1}: {text}")
                else:
                    print(f"  ❌ {selector}: 無可見元素")
            except Exception as e:
                print(f"  ❌ {selector}: 錯誤 - {e}")
    
    async def cleanup(self):
        """清理"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

async def main():
    debugger = ManusDebugger()
    
    try:
        print("🚀 啟動Manus頁面結構調試器...")
        await debugger.initialize()
        
        print("⏳ 等待頁面完全加載...")
        await asyncio.sleep(5)
        
        await debugger.analyze_page_structure()
        await debugger.test_selectors()
        
        print("\n✅ 調試完成！請查看生成的報告文件。")
        
    except Exception as e:
        print(f"❌ 調試過程中發生錯誤: {e}")
    finally:
        await debugger.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

