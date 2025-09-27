"""
Advanced Network Diagnostics Service for SmartFix-AI
Provides comprehensive network troubleshooting and monitoring capabilities
"""

import asyncio
import platform
import socket
import subprocess
import json
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import ipaddress

from .automation_service import AutomationService

logger = logging.getLogger(__name__)

class NetworkDiagnosticsService:
    """
    Comprehensive network diagnostics and troubleshooting service
    """
    
    def __init__(self):
        self.automation_service = AutomationService()
        self.system = platform.system()
        
        # Common DNS servers for testing
        self.dns_servers = [
            "8.8.8.8",      # Google DNS
            "1.1.1.1",      # Cloudflare DNS
            "208.67.222.222" # OpenDNS
        ]
        
        # Common websites for connectivity testing
        self.test_websites = [
            "google.com",
            "cloudflare.com",
            "github.com"
        ]
        
        # Common ports for testing
        self.common_ports = {
            "HTTP": 80,
            "HTTPS": 443,
            "SSH": 22,
            "FTP": 21,
            "SMTP": 25,
            "DNS": 53,
            "POP3": 110,
            "IMAP": 143
        }
    
    async def comprehensive_network_test(self) -> Dict[str, Any]:
        """
        Run a comprehensive network diagnostic test
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "system": self.system,
            "tests": {},
            "summary": {},
            "recommendations": []
        }
        
        try:
            # Test 1: Basic connectivity (ping)
            logger.info("Running connectivity tests...")
            results["tests"]["connectivity"] = await self._test_connectivity()
            
            # Test 2: DNS resolution
            logger.info("Running DNS tests...")
            results["tests"]["dns"] = await self._test_dns_resolution()
            
            # Test 3: Network interface information
            logger.info("Getting network interface info...")
            results["tests"]["interfaces"] = await self._get_network_interfaces()
            
            # Test 4: Port scanning
            logger.info("Running port tests...")
            results["tests"]["ports"] = await self._test_common_ports()
            
            # Test 5: Network speed estimation
            logger.info("Estimating network speed...")
            results["tests"]["speed"] = await self._estimate_network_speed()
            
            # Test 6: Route tracing
            logger.info("Running traceroute...")
            results["tests"]["routing"] = await self._test_routing()
            
            # Generate summary and recommendations
            results["summary"] = self._generate_network_summary(results["tests"])
            results["recommendations"] = self._generate_recommendations(results["tests"])
            
            return results
            
        except Exception as e:
            logger.error(f"Error in comprehensive network test: {e}")
            results["error"] = str(e)
            return results
    
    async def _test_connectivity(self) -> Dict[str, Any]:
        """Test basic internet connectivity"""
        connectivity_results = {
            "status": "testing",
            "tests": {},
            "overall_status": "unknown"
        }
        
        successful_pings = 0
        total_tests = len(self.test_websites)
        
        for website in self.test_websites:
            try:
                if self.system == "Windows":
                    cmd = f"ping -n 4 {website}"
                else:
                    cmd = f"ping -c 4 {website}"
                
                result = await self.automation_service.execute_command(cmd)
                
                if result["success"] and result["return_code"] == 0:
                    # Parse ping statistics
                    ping_stats = self._parse_ping_output(result["stdout"])
                    connectivity_results["tests"][website] = {
                        "status": "success",
                        "stats": ping_stats
                    }
                    successful_pings += 1
                else:
                    connectivity_results["tests"][website] = {
                        "status": "failed",
                        "error": result.get("stderr", "Ping failed")
                    }
                    
            except Exception as e:
                connectivity_results["tests"][website] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Determine overall connectivity status
        if successful_pings == total_tests:
            connectivity_results["overall_status"] = "excellent"
        elif successful_pings >= total_tests * 0.7:
            connectivity_results["overall_status"] = "good"
        elif successful_pings >= total_tests * 0.3:
            connectivity_results["overall_status"] = "poor"
        else:
            connectivity_results["overall_status"] = "failed"
        
        connectivity_results["success_rate"] = successful_pings / total_tests
        return connectivity_results
    
    async def _test_dns_resolution(self) -> Dict[str, Any]:
        """Test DNS resolution capabilities"""
        dns_results = {
            "status": "testing",
            "servers": {},
            "resolution_tests": {},
            "overall_status": "unknown"
        }
        
        # Test different DNS servers
        for dns_server in self.dns_servers:
            try:
                if self.system == "Windows":
                    cmd = f"nslookup google.com {dns_server}"
                else:
                    cmd = f"dig @{dns_server} google.com +short"
                
                result = await self.automation_service.execute_command(cmd)
                
                if result["success"]:
                    dns_results["servers"][dns_server] = {
                        "status": "working",
                        "response_time": "fast",  # Could be enhanced with timing
                        "output": result["stdout"][:200]  # Truncate for brevity
                    }
                else:
                    dns_results["servers"][dns_server] = {
                        "status": "failed",
                        "error": result.get("stderr", "DNS query failed")
                    }
                    
            except Exception as e:
                dns_results["servers"][dns_server] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Test resolution of common websites
        for website in self.test_websites:
            try:
                # Use socket.gethostbyname for cross-platform compatibility
                ip_address = socket.gethostbyname(website)
                dns_results["resolution_tests"][website] = {
                    "status": "success",
                    "ip_address": ip_address
                }
            except socket.gaierror as e:
                dns_results["resolution_tests"][website] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        # Determine overall DNS status
        working_servers = sum(1 for server in dns_results["servers"].values() if server["status"] == "working")
        successful_resolutions = sum(1 for test in dns_results["resolution_tests"].values() if test["status"] == "success")
        
        if working_servers >= 2 and successful_resolutions >= len(self.test_websites) * 0.8:
            dns_results["overall_status"] = "excellent"
        elif working_servers >= 1 and successful_resolutions >= len(self.test_websites) * 0.5:
            dns_results["overall_status"] = "good"
        else:
            dns_results["overall_status"] = "poor"
        
        return dns_results
    
    async def _get_network_interfaces(self) -> Dict[str, Any]:
        """Get network interface information"""
        interface_results = {
            "status": "testing",
            "interfaces": {},
            "active_connections": 0
        }
        
        try:
            if self.system == "Windows":
                # Windows ipconfig command
                result = await self.automation_service.execute_command("ipconfig /all")
            else:
                # Linux/Mac ifconfig or ip command
                result = await self.automation_service.execute_command("ip addr show || ifconfig")
            
            if result["success"]:
                interface_results["raw_output"] = result["stdout"]
                interface_results["interfaces"] = self._parse_interface_output(result["stdout"])
                interface_results["active_connections"] = len([
                    iface for iface in interface_results["interfaces"].values() 
                    if iface.get("status") == "active"
                ])
            else:
                interface_results["error"] = result.get("stderr", "Failed to get interface info")
                
        except Exception as e:
            interface_results["error"] = str(e)
        
        return interface_results
    
    async def _test_common_ports(self) -> Dict[str, Any]:
        """Test connectivity to common ports"""
        port_results = {
            "status": "testing",
            "local_ports": {},
            "remote_connectivity": {},
            "open_ports": []
        }
        
        try:
            # Check local listening ports
            if self.system == "Windows":
                result = await self.automation_service.execute_command("netstat -an")
            else:
                result = await self.automation_service.execute_command("netstat -tuln")
            
            if result["success"]:
                port_results["local_ports"] = self._parse_netstat_output(result["stdout"])
            
            # Test remote port connectivity
            for service, port in self.common_ports.items():
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)  # 5 second timeout
                    result = sock.connect_ex(("google.com", port))
                    sock.close()
                    
                    port_results["remote_connectivity"][service] = {
                        "port": port,
                        "status": "open" if result == 0 else "closed/filtered",
                        "accessible": result == 0
                    }
                    
                    if result == 0:
                        port_results["open_ports"].append(service)
                        
                except Exception as e:
                    port_results["remote_connectivity"][service] = {
                        "port": port,
                        "status": "error",
                        "error": str(e)
                    }
                    
        except Exception as e:
            port_results["error"] = str(e)
        
        return port_results
    
    async def _estimate_network_speed(self) -> Dict[str, Any]:
        """Estimate network speed using ping and simple tests"""
        speed_results = {
            "status": "testing",
            "ping_latency": {},
            "estimated_quality": "unknown"
        }
        
        try:
            # Test latency to different servers
            test_servers = ["8.8.8.8", "1.1.1.1", "google.com"]
            
            for server in test_servers:
                if self.system == "Windows":
                    cmd = f"ping -n 4 {server}"
                else:
                    cmd = f"ping -c 4 {server}"
                
                result = await self.automation_service.execute_command(cmd)
                
                if result["success"]:
                    ping_stats = self._parse_ping_output(result["stdout"])
                    speed_results["ping_latency"][server] = ping_stats
            
            # Estimate connection quality based on average latency
            avg_latency = self._calculate_average_latency(speed_results["ping_latency"])
            
            if avg_latency < 50:
                speed_results["estimated_quality"] = "excellent"
            elif avg_latency < 100:
                speed_results["estimated_quality"] = "good"
            elif avg_latency < 200:
                speed_results["estimated_quality"] = "fair"
            else:
                speed_results["estimated_quality"] = "poor"
            
            speed_results["average_latency_ms"] = avg_latency
            
        except Exception as e:
            speed_results["error"] = str(e)
        
        return speed_results
    
    async def _test_routing(self) -> Dict[str, Any]:
        """Test network routing with traceroute"""
        routing_results = {
            "status": "testing",
            "routes": {},
            "hop_count": {}
        }
        
        try:
            test_destinations = ["8.8.8.8", "google.com"]
            
            for destination in test_destinations:
                if self.system == "Windows":
                    cmd = f"tracert -h 15 {destination}"
                else:
                    cmd = f"traceroute -m 15 {destination}"
                
                result = await self.automation_service.execute_command(cmd)
                
                if result["success"]:
                    route_info = self._parse_traceroute_output(result["stdout"])
                    routing_results["routes"][destination] = route_info
                    routing_results["hop_count"][destination] = route_info.get("hops", 0)
                else:
                    routing_results["routes"][destination] = {
                        "status": "failed",
                        "error": result.get("stderr", "Traceroute failed")
                    }
                    
        except Exception as e:
            routing_results["error"] = str(e)
        
        return routing_results
    
    def _parse_ping_output(self, output: str) -> Dict[str, Any]:
        """Parse ping command output to extract statistics"""
        stats = {
            "packets_sent": 0,
            "packets_received": 0,
            "packet_loss": 0,
            "min_time": 0,
            "max_time": 0,
            "avg_time": 0
        }
        
        try:
            # Extract packet statistics
            if "packets transmitted" in output:
                # Linux/Mac format
                match = re.search(r'(\d+) packets transmitted, (\d+) received', output)
                if match:
                    stats["packets_sent"] = int(match.group(1))
                    stats["packets_received"] = int(match.group(2))
            elif "Packets:" in output:
                # Windows format
                match = re.search(r'Sent = (\d+), Received = (\d+), Lost = (\d+)', output)
                if match:
                    stats["packets_sent"] = int(match.group(1))
                    stats["packets_received"] = int(match.group(2))
            
            # Calculate packet loss
            if stats["packets_sent"] > 0:
                stats["packet_loss"] = ((stats["packets_sent"] - stats["packets_received"]) / stats["packets_sent"]) * 100
            
            # Extract timing statistics
            time_match = re.search(r'min/avg/max.*?=\s*([\d.]+)/([\d.]+)/([\d.]+)', output)
            if time_match:
                stats["min_time"] = float(time_match.group(1))
                stats["avg_time"] = float(time_match.group(2))
                stats["max_time"] = float(time_match.group(3))
            
        except Exception as e:
            logger.error(f"Error parsing ping output: {e}")
        
        return stats
    
    def _parse_interface_output(self, output: str) -> Dict[str, Any]:
        """Parse network interface output"""
        interfaces = {}
        
        try:
            # This is a simplified parser - can be enhanced for specific formats
            lines = output.split('\n')
            current_interface = None
            
            for line in lines:
                line = line.strip()
                
                # Detect interface name
                if ':' in line and ('eth' in line or 'wlan' in line or 'en' in line or 'Wi-Fi' in line):
                    current_interface = line.split(':')[0].strip()
                    interfaces[current_interface] = {"status": "unknown"}
                
                # Extract IP addresses
                if current_interface and ('inet ' in line or 'IPv4' in line):
                    ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        interfaces[current_interface]["ip_address"] = ip_match.group(1)
                        interfaces[current_interface]["status"] = "active"
                        
        except Exception as e:
            logger.error(f"Error parsing interface output: {e}")
        
        return interfaces
    
    def _parse_netstat_output(self, output: str) -> Dict[str, Any]:
        """Parse netstat output to find listening ports"""
        listening_ports = {"tcp": [], "udp": []}
        
        try:
            lines = output.split('\n')
            
            for line in lines:
                if 'LISTEN' in line or 'LISTENING' in line:
                    # Extract port information
                    parts = line.split()
                    if len(parts) >= 4:
                        local_address = parts[3] if len(parts) > 3 else parts[1]
                        if ':' in local_address:
                            port = local_address.split(':')[-1]
                            protocol = 'tcp' if 'tcp' in line.lower() else 'udp'
                            listening_ports[protocol].append(port)
                            
        except Exception as e:
            logger.error(f"Error parsing netstat output: {e}")
        
        return listening_ports
    
    def _parse_traceroute_output(self, output: str) -> Dict[str, Any]:
        """Parse traceroute output"""
        route_info = {
            "hops": 0,
            "destination_reached": False,
            "route_details": []
        }
        
        try:
            lines = output.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Count hops
                if re.match(r'^\s*\d+', line):
                    route_info["hops"] += 1
                    
                    # Extract hop information
                    hop_match = re.search(r'(\d+)\s+([^\s]+)\s+\(([^)]+)\)', line)
                    if hop_match:
                        route_info["route_details"].append({
                            "hop": int(hop_match.group(1)),
                            "hostname": hop_match.group(2),
                            "ip": hop_match.group(3)
                        })
                
                # Check if destination was reached
                if 'reached' in line.lower() or route_info["hops"] > 0:
                    route_info["destination_reached"] = True
                    
        except Exception as e:
            logger.error(f"Error parsing traceroute output: {e}")
        
        return route_info
    
    def _calculate_average_latency(self, ping_data: Dict[str, Any]) -> float:
        """Calculate average latency from ping results"""
        total_latency = 0
        count = 0
        
        for server_data in ping_data.values():
            if isinstance(server_data, dict) and "avg_time" in server_data:
                total_latency += server_data["avg_time"]
                count += 1
        
        return total_latency / count if count > 0 else 999
    
    def _generate_network_summary(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive network summary"""
        summary = {
            "overall_status": "unknown",
            "issues_found": [],
            "strengths": [],
            "key_metrics": {}
        }
        
        try:
            # Analyze connectivity
            connectivity = test_results.get("connectivity", {})
            if connectivity.get("overall_status") == "excellent":
                summary["strengths"].append("Excellent internet connectivity")
            elif connectivity.get("overall_status") in ["poor", "failed"]:
                summary["issues_found"].append("Poor internet connectivity")
            
            # Analyze DNS
            dns = test_results.get("dns", {})
            if dns.get("overall_status") == "excellent":
                summary["strengths"].append("DNS resolution working properly")
            elif dns.get("overall_status") == "poor":
                summary["issues_found"].append("DNS resolution problems")
            
            # Analyze speed
            speed = test_results.get("speed", {})
            avg_latency = speed.get("average_latency_ms", 999)
            summary["key_metrics"]["average_latency_ms"] = avg_latency
            
            if avg_latency < 50:
                summary["strengths"].append("Low network latency")
            elif avg_latency > 200:
                summary["issues_found"].append("High network latency")
            
            # Determine overall status
            if len(summary["issues_found"]) == 0:
                summary["overall_status"] = "excellent"
            elif len(summary["issues_found"]) <= 2:
                summary["overall_status"] = "good"
            else:
                summary["overall_status"] = "needs_attention"
                
        except Exception as e:
            logger.error(f"Error generating network summary: {e}")
            summary["overall_status"] = "error"
        
        return summary
    
    def _generate_recommendations(self, test_results: Dict[str, Any]) -> List[str]:
        """Generate network troubleshooting recommendations"""
        recommendations = []
        
        try:
            # Connectivity recommendations
            connectivity = test_results.get("connectivity", {})
            if connectivity.get("success_rate", 0) < 0.8:
                recommendations.append("Check physical network connections and restart router")
                recommendations.append("Contact your ISP if connectivity issues persist")
            
            # DNS recommendations
            dns = test_results.get("dns", {})
            if dns.get("overall_status") == "poor":
                recommendations.append("Try changing DNS servers to 8.8.8.8 or 1.1.1.1")
                recommendations.append("Flush DNS cache using ipconfig /flushdns (Windows) or sudo dscacheutil -flushcache (Mac)")
            
            # Speed recommendations
            speed = test_results.get("speed", {})
            if speed.get("average_latency_ms", 0) > 200:
                recommendations.append("Close bandwidth-heavy applications")
                recommendations.append("Move closer to WiFi router or use ethernet connection")
            
            # Port recommendations
            ports = test_results.get("ports", {})
            if len(ports.get("open_ports", [])) < 2:
                recommendations.append("Check firewall settings - some services may be blocked")
            
            # Default recommendations if no specific issues found
            if not recommendations:
                recommendations.append("Network appears healthy - no immediate action required")
                recommendations.append("Consider running periodic network tests for monitoring")
                
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append("Unable to generate specific recommendations")
        
        return recommendations[:5]  # Limit to 5 recommendations

# Create singleton instance
network_diagnostics = NetworkDiagnosticsService()

def get_network_diagnostics() -> NetworkDiagnosticsService:
    """Get the network diagnostics service instance"""
    return network_diagnostics
