#!/usr/bin/env python3
"""
ClaudeSDKMCP 性能监控演示
展示实时跟踪和统计分析功能
"""

import asyncio
import json
import time
import sys
from pathlib import Path
from typing import Dict, Any, List
import psutil
import os

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from claude_sdk_mcp_v2 import ClaudeSDKMCP

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, claude_sdk: ClaudeSDKMCP):
        self.claude_sdk = claude_sdk
        self.monitoring_data = []
        self.start_time = time.time()
        self.process = psutil.Process(os.getpid())
    
    def capture_system_metrics(self) -> Dict[str, Any]:
        """捕获系统指标"""
        memory_info = self.process.memory_info()
        cpu_percent = self.process.cpu_percent()
        
        return {
            "timestamp": time.time(),
            "memory_rss": memory_info.rss / 1024 / 1024,  # MB
            "memory_vms": memory_info.vms / 1024 / 1024,  # MB
            "cpu_percent": cpu_percent,
            "uptime": time.time() - self.start_time
        }
    
    def capture_expert_metrics(self) -> Dict[str, Any]:
        """捕获专家系统指标"""
        stats = self.claude_sdk.get_statistics()
        
        expert_metrics = {}
        for expert_id, expert_stats in stats.get('expert_statistics', {}).items():
            expert_metrics[expert_id] = {
                "name": expert_stats['name'],
                "total_requests": expert_stats['total_requests'],
                "success_rate": expert_stats['success_rate'],
                "status": expert_stats['status']
            }
        
        return {
            "total_requests": stats['total_requests'],
            "total_experts": stats['total_experts'],
            "operation_handlers": stats['operation_handlers'],
            "experts": expert_metrics
        }
    
    def capture_performance_snapshot(self) -> Dict[str, Any]:
        """捕获性能快照"""
        return {
            "system": self.capture_system_metrics(),
            "experts": self.capture_expert_metrics(),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def start_monitoring(self, interval: float = 1.0):
        """开始监控"""
        print(f"🔍 开始性能监控 (间隔: {interval}s)")
        print("按 Ctrl+C 停止监控")
        
        try:
            while True:
                snapshot = self.capture_performance_snapshot()
                self.monitoring_data.append(snapshot)
                
                # 显示实时数据
                self.display_realtime_metrics(snapshot)
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n⏹️ 监控已停止")
            self.generate_monitoring_report()
    
    def display_realtime_metrics(self, snapshot: Dict[str, Any]):
        """显示实时指标"""
        system = snapshot['system']
        experts = snapshot['experts']
        
        # 清屏并显示数据
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🔍 ClaudeSDKMCP 实时性能监控")
        print("=" * 60)
        print(f"⏰ 时间: {snapshot['timestamp']}")
        print(f"⏱️ 运行时间: {system['uptime']:.1f}s")
        
        print("\n💾 系统资源:")
        print(f"  内存使用: {system['memory_rss']:.1f} MB")
        print(f"  虚拟内存: {system['memory_vms']:.1f} MB")
        print(f"  CPU使用率: {system['cpu_percent']:.1f}%")
        
        print("\n👨‍💼 专家系统:")
        print(f"  总请求数: {experts['total_requests']}")
        print(f"  专家数量: {experts['total_experts']}")
        print(f"  操作处理器: {experts['operation_handlers']}")
        
        print("\n📊 专家详情:")
        for expert_id, expert_data in experts['experts'].items():
            status_icon = "🟢" if expert_data['status'] == 'active' else "🔴"
            print(f"  {status_icon} {expert_data['name']}: "
                  f"{expert_data['total_requests']} 请求, "
                  f"成功率 {expert_data['success_rate']:.1%}")
        
        print("\n💡 提示: 按 Ctrl+C 停止监控并生成报告")
    
    def generate_monitoring_report(self):
        """生成监控报告"""
        if not self.monitoring_data:
            print("❌ 没有监控数据")
            return
        
        print("\n📋 生成监控报告...")
        
        # 计算统计数据
        total_snapshots = len(self.monitoring_data)
        
        # 内存使用统计
        memory_usage = [snap['system']['memory_rss'] for snap in self.monitoring_data]
        avg_memory = sum(memory_usage) / len(memory_usage)
        max_memory = max(memory_usage)
        min_memory = min(memory_usage)
        
        # CPU使用统计
        cpu_usage = [snap['system']['cpu_percent'] for snap in self.monitoring_data]
        avg_cpu = sum(cpu_usage) / len(cpu_usage)
        max_cpu = max(cpu_usage)
        
        # 专家请求统计
        final_stats = self.monitoring_data[-1]['experts']
        
        report = {
            "monitoring_summary": {
                "total_snapshots": total_snapshots,
                "monitoring_duration": self.monitoring_data[-1]['system']['uptime'],
                "start_time": self.monitoring_data[0]['timestamp'],
                "end_time": self.monitoring_data[-1]['timestamp']
            },
            "system_performance": {
                "memory_usage_mb": {
                    "average": round(avg_memory, 2),
                    "maximum": round(max_memory, 2),
                    "minimum": round(min_memory, 2)
                },
                "cpu_usage_percent": {
                    "average": round(avg_cpu, 2),
                    "maximum": round(max_cpu, 2)
                }
            },
            "expert_performance": final_stats,
            "recommendations": self.generate_performance_recommendations(avg_memory, avg_cpu, final_stats)
        }
        
        # 保存报告
        report_file = Path(__file__).parent / "performance_monitoring_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        # 显示报告摘要
        print("\n📊 监控报告摘要:")
        print(f"  监控时长: {report['monitoring_summary']['monitoring_duration']:.1f}s")
        print(f"  数据点数: {total_snapshots}")
        print(f"  平均内存: {avg_memory:.1f} MB")
        print(f"  平均CPU: {avg_cpu:.1f}%")
        print(f"  总请求数: {final_stats['total_requests']}")
        
        print(f"\n📄 详细报告已保存到: {report_file}")
        
        return report
    
    def generate_performance_recommendations(self, avg_memory: float, avg_cpu: float, expert_stats: Dict) -> List[str]:
        """生成性能建议"""
        recommendations = []
        
        if avg_memory > 100:
            recommendations.append("内存使用较高，建议优化内存管理")
        
        if avg_cpu > 50:
            recommendations.append("CPU使用率较高，建议优化算法性能")
        
        if expert_stats['total_requests'] == 0:
            recommendations.append("系统尚未处理请求，建议进行功能测试")
        
        # 检查专家使用分布
        expert_requests = [exp['total_requests'] for exp in expert_stats['experts'].values()]
        if expert_requests and max(expert_requests) > 0:
            if max(expert_requests) / sum(expert_requests) > 0.8:
                recommendations.append("专家使用不均衡，建议优化负载分配")
        
        if not recommendations:
            recommendations.append("系统性能良好，无需特别优化")
        
        return recommendations

async def demo_with_load():
    """演示带负载的性能监控"""
    print("🚀 启动带负载的性能监控演示")
    
    # 初始化系统
    claude_sdk = ClaudeSDKMCP()
    monitor = PerformanceMonitor(claude_sdk)
    
    # 启动监控（在后台）
    monitoring_task = None
    
    try:
        print("📋 执行测试负载...")
        
        # 执行一些测试请求来产生负载
        test_requests = [
            ("分析Python代码性能", {"code": "def test(): pass", "language": "python"}),
            ("检查安全漏洞", {"code": "sql = f'SELECT * FROM users WHERE id = {user_id}'", "language": "python"}),
            ("优化算法", {"code": "for i in range(1000): result = i * i", "language": "python"}),
            ("API设计审查", {"api": "REST API", "context": "微服务"}),
            ("数据库查询优化", {"query": "SELECT * FROM large_table", "context": "性能优化"})
        ]
        
        print("🔄 开始处理请求...")
        for i, (request, context) in enumerate(test_requests, 1):
            print(f"  处理请求 {i}/{len(test_requests)}: {request}")
            
            start_time = time.time()
            result = await claude_sdk.process_request(request, context)
            processing_time = time.time() - start_time
            
            print(f"    ✅ 完成 - 时间: {processing_time:.2f}s, 专家: {result.expert_used}")
            
            # 显示当前性能快照
            snapshot = monitor.capture_performance_snapshot()
            print(f"    📊 内存: {snapshot['system']['memory_rss']:.1f}MB, "
                  f"总请求: {snapshot['experts']['total_requests']}")
            
            await asyncio.sleep(0.5)  # 模拟间隔
        
        print("\n📈 最终性能统计:")
        final_stats = claude_sdk.get_statistics()
        print(json.dumps(final_stats, ensure_ascii=False, indent=2, default=str))
        
        # 生成最终报告
        final_report = monitor.generate_monitoring_report()
        
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
    
    finally:
        await claude_sdk.close()

async def interactive_monitoring():
    """交互式监控"""
    print("🔍 ClaudeSDKMCP 交互式性能监控")
    print("选择监控模式:")
    print("1. 实时监控 (持续显示)")
    print("2. 负载测试监控")
    print("3. 快照模式")
    
    try:
        choice = input("请选择 (1-3): ").strip()
        
        claude_sdk = ClaudeSDKMCP()
        monitor = PerformanceMonitor(claude_sdk)
        
        if choice == "1":
            monitor.start_monitoring(interval=2.0)
        elif choice == "2":
            await demo_with_load()
        elif choice == "3":
            snapshot = monitor.capture_performance_snapshot()
            print("\n📊 当前性能快照:")
            print(json.dumps(snapshot, ensure_ascii=False, indent=2, default=str))
        else:
            print("❌ 无效选择")
        
        await claude_sdk.close()
        
    except KeyboardInterrupt:
        print("\n👋 监控已停止")
    except Exception as e:
        print(f"❌ 发生错误: {e}")

async def main():
    """主函数"""
    print("🔍 ClaudeSDKMCP 性能监控演示")
    print("=" * 50)
    
    await interactive_monitoring()

if __name__ == "__main__":
    asyncio.run(main())

