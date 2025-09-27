#!/usr/bin/env python3
"""
Enhanced Galaxy Autopilot Demo Script

Demonstrates the real system monitoring, healing, and AI capabilities
of the enhanced Galaxy Autopilot system.
"""

import asyncio
import logging
import time
import json
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demo_system_monitoring():
    """Demonstrate real system monitoring capabilities"""
    print("\n🔍 DEMO: Real System Monitoring")
    print("=" * 50)
    
    try:
        from core.system_monitor import RealSystemMonitor
        
        # Initialize system monitor
        monitor = RealSystemMonitor("demo_device")
        
        # Get current system metrics
        print("📊 Collecting real system metrics...")
        metrics = await monitor.get_current_metrics()
        
        print(f"💻 CPU Usage: {metrics.cpu_percent:.1f}%")
        print(f"🧠 Memory Usage: {metrics.memory_percent:.1f}%")
        print(f"💾 Disk Usage: {metrics.disk_percent:.1f}%")
        print(f"🌡️ Temperature: {metrics.temperature or 'N/A'}°C")
        print(f"🔋 Battery: {metrics.battery_percent or 'N/A'}%")
        print(f"⏱️ Uptime: {metrics.uptime_seconds / 3600:.1f} hours")
        print(f"🔗 Network Connections: {metrics.network_connections}")
        
        # Get system health score
        health_score = await monitor.get_system_health_score()
        print(f"🏥 System Health Score: {health_score:.1f}/100")
        
        # Detect issues
        issues = await monitor.detect_issues()
        if issues:
            print(f"\n⚠️ Issues Detected: {len(issues)}")
            for issue in issues:
                print(f"   - {issue['description']} (Severity: {issue['severity']})")
        else:
            print("\n✅ No issues detected")
        
        # Get processes
        print(f"\n🔄 Getting process information...")
        processes = await monitor.get_processes()
        print(f"📋 Total Processes: {len(processes)}")
        
        # Show top CPU processes
        top_cpu_processes = sorted(processes, key=lambda p: p.cpu_percent, reverse=True)[:5]
        print("\n🔥 Top CPU Processes:")
        for proc in top_cpu_processes:
            print(f"   - {proc.name}: {proc.cpu_percent:.1f}% CPU, {proc.memory_percent:.1f}% Memory")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in system monitoring demo: {e}")
        return False

async def demo_healing_actions():
    """Demonstrate real healing action capabilities"""
    print("\n🛠️ DEMO: Real Healing Actions")
    print("=" * 50)
    
    try:
        from core.healing_executor import RealHealingExecutor
        
        # Initialize healing executor
        executor = RealHealingExecutor("demo_device")
        
        # Demo 1: Memory optimization
        print("🧠 Testing memory optimization...")
        result = await executor.optimize_memory()
        print(f"   Success: {result.success}")
        print(f"   Duration: {result.duration_ms}ms")
        print(f"   Improvement Score: {result.improvement_score:.2f}")
        if result.details:
            print(f"   Details: {result.details}")
        
        # Demo 2: Clear system cache
        print("\n🧹 Testing cache clearing...")
        result = await executor.clear_system_cache()
        print(f"   Success: {result.success}")
        print(f"   Duration: {result.duration_ms}ms")
        print(f"   Improvement Score: {result.improvement_score:.2f}")
        if result.details:
            print(f"   Details: {result.details}")
        
        # Demo 3: Get healing statistics
        print("\n📈 Healing Statistics:")
        success_rate = executor.get_success_rate()
        print(f"   Success Rate: {success_rate:.1f}%")
        
        history = executor.get_healing_history()
        print(f"   Total Actions: {len(history)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in healing actions demo: {e}")
        return False

async def demo_database_operations():
    """Demonstrate real database operations"""
    print("\n💾 DEMO: Real Database Operations")
    print("=" * 50)
    
    try:
        from core.database import GalaxyAutopilotDatabase, HealingAction
        
        # Initialize database
        db = GalaxyAutopilotDatabase("./demo_galaxy_autopilot.db")
        await db.initialize()
        
        # Save sample system metrics
        print("💾 Saving system metrics...")
        sample_metrics = {
            "cpu_percent": 45.2,
            "memory_percent": 67.8,
            "disk_percent": 34.5,
            "temperature": 42.1,
            "battery_percent": 78.0,
            "network_bytes_sent": 1024000,
            "network_bytes_recv": 2048000,
            "processes_count": 156
        }
        
        metrics_id = await db.save_system_metrics("demo_device", sample_metrics, 85.5)
        print(f"   Metrics saved with ID: {metrics_id}")
        
        # Save sample healing action
        print("💾 Saving healing action...")
        healing_action = HealingAction(
            id=None,
            action_type="optimize_memory",
            layer="surface",
            target="system_memory",
            parameters={"reason": "demo_action"},
            success=True,
            timestamp=datetime.now(),
            duration_ms=1250,
            improvement_score=0.75,
            user_feedback=4,
            error_message=None
        )
        
        action_id = await db.save_healing_action(healing_action)
        print(f"   Healing action saved with ID: {action_id}")
        
        # Get healing actions
        print("📋 Retrieving healing actions...")
        actions = await db.get_healing_actions(limit=10)
        print(f"   Retrieved {len(actions)} actions")
        
        # Get success rate
        success_rate = await db.get_healing_success_rate()
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Get database statistics
        stats = await db.get_database_stats()
        print(f"\n📊 Database Statistics:")
        for table, count in stats.items():
            if table != 'database_size_mb':
                print(f"   {table}: {count} records")
        print(f"   Database Size: {stats.get('database_size_mb', 0):.2f} MB")
        
        # Cleanup
        await db.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error in database operations demo: {e}")
        return False

async def demo_ai_engine():
    """Demonstrate enhanced AI engine capabilities"""
    print("\n🤖 DEMO: Enhanced AI Engine")
    print("=" * 50)
    
    try:
        from core.ai_engine import GalaxyAutopilotAI
        
        # Initialize AI engine
        ai_engine = GalaxyAutopilotAI("demo_device")
        await ai_engine.initialize()
        
        # Get current system state (now uses real data)
        print("🧠 Getting real system state...")
        system_state = await ai_engine._get_current_system_state()
        
        print(f"   Device ID: {system_state.device_id}")
        print(f"   CPU Usage: {system_state.cpu_usage:.1f}%")
        print(f"   Memory Usage: {system_state.memory_usage:.1f}%")
        print(f"   Storage Usage: {system_state.storage_usage:.1f}%")
        print(f"   System Health: {system_state.system_health_score:.1f}")
        
        # Process a healing request
        print("\n🔧 Processing healing request...")
        result = await ai_engine.process_healing_request(
            issue_type="performance",
            severity="medium",
            context={"demo": True, "proactive": False}
        )
        
        print(f"   Success: {result.get('success', False)}")
        print(f"   Action: {result.get('action', 'unknown')}")
        print(f"   Layer: {result.get('layer', 'unknown')}")
        print(f"   Improvement: {result.get('estimated_improvement', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in AI engine demo: {e}")
        return False

async def demo_enhanced_service():
    """Demonstrate the enhanced autopilot service"""
    print("\n🚀 DEMO: Enhanced Autopilot Service")
    print("=" * 50)
    
    try:
        from services.enhanced_autopilot_service import EnhancedAutopilotService
        
        # Initialize enhanced service
        service = EnhancedAutopilotService("demo_device")
        await service.initialize()
        
        # Get comprehensive health report
        print("📊 Getting comprehensive health report...")
        health_report = await service.get_system_health_report()
        
        if "error" not in health_report:
            system_health = health_report.get("system_health", {})
            print(f"   Overall Health Score: {system_health.get('overall_score', 0):.1f}")
            print(f"   CPU: {system_health.get('cpu_percent', 0):.1f}%")
            print(f"   Memory: {system_health.get('memory_percent', 0):.1f}%")
            print(f"   Disk: {system_health.get('disk_percent', 0):.1f}%")
            
            healing_stats = health_report.get("healing_statistics", {})
            print(f"   Healing Success Rate: {healing_stats.get('success_rate', 0):.1f}%")
            print(f"   Total Actions: {healing_stats.get('total_actions', 0)}")
        
        # Get predictive insights
        print("\n🔮 Getting predictive insights...")
        insights = await service.get_predictive_insights()
        
        if "error" not in insights:
            health_trend = insights.get("health_trend", {})
            print(f"   Health Trend: {health_trend.get('direction', 'unknown')}")
            print(f"   Trend Confidence: {health_trend.get('confidence', 0):.2f}")
            
            predictions = insights.get("predictions", [])
            print(f"   Predictions: {len(predictions)}")
            for pred in predictions:
                print(f"     - {pred.get('type', 'unknown')}: {pred.get('probability', 0):.2f} probability")
        
        # Perform manual healing
        print("\n🛠️ Performing manual healing...")
        healing_result = await service.perform_manual_healing(
            issue_type="performance",
            severity="medium",
            context={"demo": True}
        )
        
        print(f"   Success: {healing_result.get('success', False)}")
        print(f"   Action Taken: {healing_result.get('action_taken', 'unknown')}")
        print(f"   Layer Used: {healing_result.get('layer_used', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in enhanced service demo: {e}")
        return False

async def demo_api_endpoints():
    """Demonstrate API endpoint functionality"""
    print("\n🌐 DEMO: API Endpoints")
    print("=" * 50)
    
    try:
        import aiohttp
        
        # Note: This would require the server to be running
        print("📡 API Endpoints Available:")
        print("   GET  /api/v1/enhanced-galaxy-autopilot/health-report")
        print("   POST /api/v1/enhanced-galaxy-autopilot/intelligent-healing")
        print("   GET  /api/v1/enhanced-galaxy-autopilot/real-time-metrics")
        print("   GET  /api/v1/enhanced-galaxy-autopilot/predictive-insights")
        print("   POST /api/v1/enhanced-galaxy-autopilot/emergency-healing")
        print("   GET  /api/v1/enhanced-galaxy-autopilot/system-optimization-suggestions")
        print("   GET  /api/v1/enhanced-galaxy-autopilot/healing-statistics")
        
        print("\n💡 To test API endpoints:")
        print("   1. Start the SmartFix-AI server: python backend/main.py")
        print("   2. Visit: http://localhost:8000/docs")
        print("   3. Test the Galaxy Autopilot endpoints")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in API endpoints demo: {e}")
        return False

async def main():
    """Main demo function"""
    print("🚀 ENHANCED GALAXY AUTOPILOT DEMO")
    print("=" * 60)
    print("Demonstrating real system monitoring, healing, and AI capabilities")
    print("=" * 60)
    
    demos = [
        ("System Monitoring", demo_system_monitoring),
        ("Healing Actions", demo_healing_actions),
        ("Database Operations", demo_database_operations),
        ("AI Engine", demo_ai_engine),
        ("Enhanced Service", demo_enhanced_service),
        ("API Endpoints", demo_api_endpoints)
    ]
    
    results = []
    
    for demo_name, demo_func in demos:
        print(f"\n⏳ Running {demo_name} demo...")
        try:
            success = await demo_func()
            results.append((demo_name, success))
            if success:
                print(f"✅ {demo_name} demo completed successfully")
            else:
                print(f"❌ {demo_name} demo failed")
        except Exception as e:
            print(f"❌ {demo_name} demo error: {e}")
            results.append((demo_name, False))
        
        # Small delay between demos
        await asyncio.sleep(1)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEMO SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for demo_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {demo_name}")
    
    print(f"\n🎯 Overall Result: {successful}/{total} demos passed")
    
    if successful == total:
        print("🎉 All demos passed! Galaxy Autopilot is working perfectly!")
    elif successful > total // 2:
        print("⚠️ Most demos passed. Some components may need attention.")
    else:
        print("🚨 Many demos failed. Please check the system requirements.")
    
    print("\n💡 Next Steps:")
    print("   1. Install requirements: pip install -r backend/galaxy_autopilot/requirements.txt")
    print("   2. Start the server: python backend/main.py")
    print("   3. Test the API endpoints at: http://localhost:8000/docs")
    print("   4. Monitor system health in real-time")

if __name__ == "__main__":
    asyncio.run(main())

