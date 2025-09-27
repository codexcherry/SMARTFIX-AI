import psutil
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import threading
from collections import defaultdict, deque

from .config import settings
from .cache import cache_manager
from .retry import get_all_circuit_breaker_status
from ..database import check_db_connection

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System metrics data structure"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    active_connections: int
    requests_per_minute: float
    error_rate: float
    response_time_avg: float
    cache_hit_rate: float

@dataclass
class ServiceHealth:
    """Service health status"""
    name: str
    status: str  # healthy, degraded, unhealthy
    response_time: float
    last_check: datetime
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class HealthChecker:
    """Health check system for services"""
    
    def __init__(self):
        self.health_checks: Dict[str, Callable] = {}
        self.health_status: Dict[str, ServiceHealth] = {}
        self.register_default_checks()
    
    def register_health_check(self, name: str, check_func: Callable):
        """Register a health check function"""
        self.health_checks[name] = check_func
    
    def register_default_checks(self):
        """Register default health checks"""
        self.register_health_check("database", self._check_database)
        self.register_health_check("cache", self._check_cache)
        self.register_health_check("disk_space", self._check_disk_space)
        self.register_health_check("memory", self._check_memory)
        self.register_health_check("cpu", self._check_cpu)
    
    async def _check_database(self) -> ServiceHealth:
        """Check database health"""
        start_time = time.time()
        try:
            is_healthy = check_db_connection()
            response_time = time.time() - start_time
            
            if is_healthy:
                return ServiceHealth(
                    name="database",
                    status="healthy",
                    response_time=response_time,
                    last_check=datetime.utcnow()
                )
            else:
                return ServiceHealth(
                    name="database",
                    status="unhealthy",
                    response_time=response_time,
                    last_check=datetime.utcnow(),
                    error_message="Database connection failed"
                )
        except Exception as e:
            return ServiceHealth(
                name="database",
                status="unhealthy",
                response_time=time.time() - start_time,
                last_check=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def _check_cache(self) -> ServiceHealth:
        """Check cache health"""
        start_time = time.time()
        try:
            stats = cache_manager.get_stats()
            response_time = time.time() - start_time
            
            if stats.get('type') in ['redis', 'memory']:
                return ServiceHealth(
                    name="cache",
                    status="healthy",
                    response_time=response_time,
                    last_check=datetime.utcnow(),
                    details=stats
                )
            else:
                return ServiceHealth(
                    name="cache",
                    status="degraded",
                    response_time=response_time,
                    last_check=datetime.utcnow(),
                    error_message="Cache not available",
                    details=stats
                )
        except Exception as e:
            return ServiceHealth(
                name="cache",
                status="unhealthy",
                response_time=time.time() - start_time,
                last_check=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def _check_disk_space(self) -> ServiceHealth:
        """Check disk space"""
        start_time = time.time()
        try:
            disk_usage = psutil.disk_usage('/')
            usage_percent = disk_usage.percent
            response_time = time.time() - start_time
            
            if usage_percent < 80:
                status = "healthy"
            elif usage_percent < 90:
                status = "degraded"
            else:
                status = "unhealthy"
            
            return ServiceHealth(
                name="disk_space",
                status=status,
                response_time=response_time,
                last_check=datetime.utcnow(),
                details={
                    "usage_percent": usage_percent,
                    "free_gb": disk_usage.free / (1024**3),
                    "total_gb": disk_usage.total / (1024**3)
                }
            )
        except Exception as e:
            return ServiceHealth(
                name="disk_space",
                status="unhealthy",
                response_time=time.time() - start_time,
                last_check=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def _check_memory(self) -> ServiceHealth:
        """Check memory usage"""
        start_time = time.time()
        try:
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            response_time = time.time() - start_time
            
            if usage_percent < 80:
                status = "healthy"
            elif usage_percent < 90:
                status = "degraded"
            else:
                status = "unhealthy"
            
            return ServiceHealth(
                name="memory",
                status=status,
                response_time=response_time,
                last_check=datetime.utcnow(),
                details={
                    "usage_percent": usage_percent,
                    "available_gb": memory.available / (1024**3),
                    "total_gb": memory.total / (1024**3)
                }
            )
        except Exception as e:
            return ServiceHealth(
                name="memory",
                status="unhealthy",
                response_time=time.time() - start_time,
                last_check=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def _check_cpu(self) -> ServiceHealth:
        """Check CPU usage"""
        start_time = time.time()
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            response_time = time.time() - start_time
            
            if cpu_percent < 80:
                status = "healthy"
            elif cpu_percent < 90:
                status = "degraded"
            else:
                status = "unhealthy"
            
            return ServiceHealth(
                name="cpu",
                status=status,
                response_time=response_time,
                last_check=datetime.utcnow(),
                details={"usage_percent": cpu_percent}
            )
        except Exception as e:
            return ServiceHealth(
                name="cpu",
                status="unhealthy",
                response_time=time.time() - start_time,
                last_check=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def run_all_checks(self) -> Dict[str, ServiceHealth]:
        """Run all health checks"""
        results = {}
        
        for name, check_func in self.health_checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                results[name] = result
                self.health_status[name] = result
            except Exception as e:
                logger.error(f"Health check {name} failed: {e}")
                results[name] = ServiceHealth(
                    name=name,
                    status="unhealthy",
                    response_time=0.0,
                    last_check=datetime.utcnow(),
                    error_message=str(e)
                )
        
        return results

class MetricsCollector:
    """System metrics collection"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history: deque = deque(maxlen=max_history)
        self.request_times: deque = deque(maxlen=1000)
        self.error_count = 0
        self.total_requests = 0
        self.last_reset = datetime.utcnow()
        
        # Network IO tracking
        self.last_network_io = psutil.net_io_counters()
        self.last_network_time = time.time()
    
    def record_request(self, response_time: float, is_error: bool = False):
        """Record a request"""
        self.request_times.append(response_time)
        self.total_requests += 1
        if is_error:
            self.error_count += 1
    
    def collect_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        # System metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network IO
        current_network_io = psutil.net_io_counters()
        current_time = time.time()
        time_diff = current_time - self.last_network_time
        
        network_io = {
            'bytes_sent_per_sec': (current_network_io.bytes_sent - self.last_network_io.bytes_sent) / time_diff,
            'bytes_recv_per_sec': (current_network_io.bytes_recv - self.last_network_io.bytes_recv) / time_diff
        }
        
        self.last_network_io = current_network_io
        self.last_network_time = current_time
        
        # Request metrics
        requests_per_minute = self._calculate_requests_per_minute()
        error_rate = self._calculate_error_rate()
        response_time_avg = self._calculate_avg_response_time()
        
        # Cache metrics
        cache_stats = cache_manager.get_stats()
        cache_hit_rate = self._calculate_cache_hit_rate(cache_stats)
        
        metrics = SystemMetrics(
            timestamp=datetime.utcnow(),
            cpu_usage=cpu_usage,
            memory_usage=memory.percent,
            disk_usage=disk.percent,
            network_io=network_io,
            active_connections=len(psutil.net_connections()),
            requests_per_minute=requests_per_minute,
            error_rate=error_rate,
            response_time_avg=response_time_avg,
            cache_hit_rate=cache_hit_rate
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    def _calculate_requests_per_minute(self) -> float:
        """Calculate requests per minute"""
        now = datetime.utcnow()
        if (now - self.last_reset).total_seconds() >= 60:
            # Reset counters every minute
            self.total_requests = 0
            self.error_count = 0
            self.last_reset = now
            return 0.0
        
        return self.total_requests
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate"""
        if self.total_requests == 0:
            return 0.0
        return (self.error_count / self.total_requests) * 100
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time"""
        if not self.request_times:
            return 0.0
        return sum(self.request_times) / len(self.request_times)
    
    def _calculate_cache_hit_rate(self, cache_stats: Dict[str, Any]) -> float:
        """Calculate cache hit rate"""
        if cache_stats.get('type') == 'redis':
            hits = cache_stats.get('keyspace_hits', 0)
            misses = cache_stats.get('keyspace_misses', 0)
            total = hits + misses
            if total > 0:
                return (hits / total) * 100
        return 0.0
    
    def get_metrics_history(self, minutes: int = 60) -> List[SystemMetrics]:
        """Get metrics history for the last N minutes"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        return [m for m in self.metrics_history if m.timestamp >= cutoff_time]
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = self.get_metrics_history(minutes=5)
        if not recent_metrics:
            return {}
        
        return {
            'avg_cpu': sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics),
            'avg_memory': sum(m.memory_usage for m in recent_metrics) / len(recent_metrics),
            'avg_disk': sum(m.disk_usage for m in recent_metrics) / len(recent_metrics),
            'avg_response_time': sum(m.response_time_avg for m in recent_metrics) / len(recent_metrics),
            'avg_error_rate': sum(m.error_rate for m in recent_metrics) / len(recent_metrics),
            'total_requests': sum(m.requests_per_minute for m in recent_metrics)
        }

class AlertManager:
    """Alert management system"""
    
    def __init__(self):
        self.alerts: List[Dict[str, Any]] = []
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.alert_handlers: List[Callable] = []
        self.setup_default_rules()
    
    def setup_default_rules(self):
        """Setup default alert rules"""
        self.alert_rules = {
            'high_cpu': {
                'metric': 'cpu_usage',
                'threshold': 90.0,
                'operator': '>',
                'severity': 'warning',
                'message': 'CPU usage is above 90%'
            },
            'high_memory': {
                'metric': 'memory_usage',
                'threshold': 90.0,
                'operator': '>',
                'severity': 'warning',
                'message': 'Memory usage is above 90%'
            },
            'high_disk': {
                'metric': 'disk_usage',
                'threshold': 90.0,
                'operator': '>',
                'severity': 'critical',
                'message': 'Disk usage is above 90%'
            },
            'high_error_rate': {
                'metric': 'error_rate',
                'threshold': 10.0,
                'operator': '>',
                'severity': 'critical',
                'message': 'Error rate is above 10%'
            },
            'service_unhealthy': {
                'metric': 'service_status',
                'threshold': 'unhealthy',
                'operator': '==',
                'severity': 'critical',
                'message': 'Service is unhealthy'
            }
        }
    
    def add_alert_handler(self, handler: Callable):
        """Add alert handler function"""
        self.alert_handlers.append(handler)
    
    def check_alerts(self, metrics: SystemMetrics, health_status: Dict[str, ServiceHealth]):
        """Check for alerts based on metrics and health status"""
        alerts = []
        
        # Check metric-based alerts
        for rule_name, rule in self.alert_rules.items():
            if rule['metric'] in ['cpu_usage', 'memory_usage', 'disk_usage', 'error_rate']:
                metric_value = getattr(metrics, rule['metric'])
                
                if self._evaluate_condition(metric_value, rule['operator'], rule['threshold']):
                    alert = {
                        'id': f"{rule_name}_{int(time.time())}",
                        'rule': rule_name,
                        'severity': rule['severity'],
                        'message': rule['message'],
                        'metric': rule['metric'],
                        'value': metric_value,
                        'threshold': rule['threshold'],
                        'timestamp': datetime.utcnow()
                    }
                    alerts.append(alert)
        
        # Check service health alerts
        for service_name, health in health_status.items():
            if health.status == 'unhealthy':
                alert = {
                    'id': f"service_{service_name}_{int(time.time())}",
                    'rule': 'service_unhealthy',
                    'severity': 'critical',
                    'message': f"Service {service_name} is unhealthy: {health.error_message}",
                    'service': service_name,
                    'timestamp': datetime.utcnow()
                }
                alerts.append(alert)
        
        # Process alerts
        for alert in alerts:
            self._process_alert(alert)
    
    def _evaluate_condition(self, value: Any, operator: str, threshold: Any) -> bool:
        """Evaluate alert condition"""
        if operator == '>':
            return value > threshold
        elif operator == '<':
            return value < threshold
        elif operator == '>=':
            return value >= threshold
        elif operator == '<=':
            return value <= threshold
        elif operator == '==':
            return value == threshold
        elif operator == '!=':
            return value != threshold
        return False
    
    def _process_alert(self, alert: Dict[str, Any]):
        """Process an alert"""
        self.alerts.append(alert)
        
        # Call alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
        
        logger.warning(f"Alert triggered: {alert['message']} (Severity: {alert['severity']})")
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [alert for alert in self.alerts if alert['timestamp'] >= cutoff_time]

# Global instances
health_checker = HealthChecker()
metrics_collector = MetricsCollector()
alert_manager = AlertManager()

# Monitoring middleware
class MonitoringMiddleware:
    """FastAPI middleware for request monitoring"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        start_time = time.time()
        is_error = False
        
        try:
            await self.app(scope, receive, send)
        except Exception:
            is_error = True
            raise
        finally:
            response_time = time.time() - start_time
            metrics_collector.record_request(response_time, is_error)

# Health check endpoint data
async def get_health_status() -> Dict[str, Any]:
    """Get comprehensive health status"""
    health_checks = await health_checker.run_all_checks()
    metrics = metrics_collector.collect_metrics()
    circuit_breakers = get_all_circuit_breaker_status()
    
    # Check overall health
    overall_status = "healthy"
    if any(check.status == "unhealthy" for check in health_checks.values()):
        overall_status = "unhealthy"
    elif any(check.status == "degraded" for check in health_checks.values()):
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "services": {name: asdict(check) for name, check in health_checks.items()},
        "metrics": asdict(metrics),
        "circuit_breakers": circuit_breakers
    }

async def get_metrics() -> Dict[str, Any]:
    """Get current metrics"""
    metrics = metrics_collector.collect_metrics()
    summary = metrics_collector.get_summary_stats()
    
    return {
        "current": asdict(metrics),
        "summary": summary,
        "history_count": len(metrics_collector.metrics_history)
    }

async def get_alerts() -> Dict[str, Any]:
    """Get recent alerts"""
    recent_alerts = alert_manager.get_recent_alerts()
    
    return {
        "alerts": recent_alerts,
        "total_alerts": len(alert_manager.alerts),
        "recent_alerts_count": len(recent_alerts)
    }
