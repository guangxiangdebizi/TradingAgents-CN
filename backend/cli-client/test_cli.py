#!/usr/bin/env python3
"""
Backend Trading CLI Client 测试文件
"""

import asyncio
import json
import pytest
import aiohttp
from unittest.mock import AsyncMock, patch, MagicMock
from trading_cli import BackendClient, TradingCLI
from config import ConfigManager, HistoryManager, PresetManager

class TestBackendClient:
    """测试BackendClient类"""
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """测试健康检查成功"""
        mock_response = AsyncMock()
        mock_response.json.return_value = {"success": True, "status": "healthy"}
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with BackendClient() as client:
                result = await client.health_check()
                
                assert result["success"] == True
                assert result["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """测试健康检查失败"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = Exception("Connection refused")
            
            async with BackendClient() as client:
                result = await client.health_check()
                
                assert result["success"] == False
                assert "Connection refused" in result["error"]
    
    @pytest.mark.asyncio
    async def test_start_analysis_success(self):
        """测试启动分析成功"""
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "analysis_id": "test-uuid-12345",
                "status": "started"
            }
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value = mock_response
            
            async with BackendClient() as client:
                result = await client.start_analysis("000001")
                
                assert result["success"] == True
                assert result["data"]["analysis_id"] == "test-uuid-12345"
    
    @pytest.mark.asyncio
    async def test_get_analysis_status(self):
        """测试获取分析状态"""
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "analysis_id": "test-uuid-12345",
                "status": "running",
                "current_step": "market_analyst",
                "progress": {
                    "completed_steps": 3,
                    "total_steps": 12,
                    "percentage": 25.0
                }
            }
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with BackendClient() as client:
                result = await client.get_analysis_status("test-uuid-12345")
                
                assert result["success"] == True
                assert result["data"]["status"] == "running"
                assert result["data"]["progress"]["percentage"] == 25.0
    
    @pytest.mark.asyncio
    async def test_get_analysis_result(self):
        """测试获取分析结果"""
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "result": {
                    "final_recommendation": {
                        "action": "buy",
                        "confidence": 0.75,
                        "target_price": 15.50
                    },
                    "investment_plan": "建议分批买入",
                    "risk_assessment": {
                        "risk_level": "medium",
                        "risk_score": 0.6
                    }
                }
            }
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with BackendClient() as client:
                result = await client.get_analysis_result("test-uuid-12345")
                
                assert result["success"] == True
                assert result["data"]["result"]["final_recommendation"]["action"] == "buy"

class TestConfigManager:
    """测试ConfigManager类"""
    
    def test_load_default_config(self):
        """测试加载默认配置"""
        with patch('pathlib.Path.exists', return_value=False):
            with patch('builtins.open', create=True) as mock_open:
                config_manager = ConfigManager()
                config = config_manager.get_config()
                
                assert config.backend_url == "http://localhost:8001"
                assert config.default_analysis_type == "comprehensive"
                assert config.auto_refresh == True
    
    def test_load_existing_config(self):
        """测试加载现有配置"""
        mock_config = {
            "backend_url": "http://custom:8001",
            "default_analysis_type": "quick",
            "auto_refresh": False
        }
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_config)
                
                config_manager = ConfigManager()
                config = config_manager.get_config()
                
                assert config.backend_url == "http://custom:8001"
                assert config.default_analysis_type == "quick"
                assert config.auto_refresh == False
    
    def test_update_config(self):
        """测试更新配置"""
        with patch('pathlib.Path.exists', return_value=False):
            with patch('builtins.open', create=True):
                config_manager = ConfigManager()
                
                config_manager.update_config(
                    backend_url="http://updated:8001",
                    max_debate_rounds=5
                )
                
                config = config_manager.get_config()
                assert config.backend_url == "http://updated:8001"
                assert config.max_debate_rounds == 5

class TestHistoryManager:
    """测试HistoryManager类"""
    
    def test_add_analysis(self):
        """测试添加分析记录"""
        with patch('pathlib.Path.exists', return_value=False):
            with patch('builtins.open', create=True):
                history_manager = HistoryManager()
                
                history_manager.add_analysis("000001", "test-uuid-12345")
                
                assert len(history_manager.history) == 1
                assert history_manager.history[0]["symbol"] == "000001"
                assert history_manager.history[0]["analysis_id"] == "test-uuid-12345"
    
    def test_update_analysis(self):
        """测试更新分析记录"""
        with patch('pathlib.Path.exists', return_value=False):
            with patch('builtins.open', create=True):
                history_manager = HistoryManager()
                
                # 添加记录
                history_manager.add_analysis("000001", "test-uuid-12345")
                
                # 更新记录
                history_manager.update_analysis("test-uuid-12345", "completed", {"action": "buy"})
                
                record = history_manager.history[0]
                assert record["status"] == "completed"
                assert record["result"]["action"] == "buy"
    
    def test_get_analysis_by_symbol(self):
        """测试根据股票代码获取分析记录"""
        with patch('pathlib.Path.exists', return_value=False):
            with patch('builtins.open', create=True):
                history_manager = HistoryManager()
                
                # 添加多个记录
                history_manager.add_analysis("000001", "uuid-1")
                history_manager.add_analysis("000002", "uuid-2")
                history_manager.add_analysis("000001", "uuid-3")
                
                # 获取000001的记录
                records = history_manager.get_analysis_by_symbol("000001")
                
                assert len(records) == 2
                assert all(record["symbol"] == "000001" for record in records)

class TestPresetManager:
    """测试PresetManager类"""
    
    def test_get_preset(self):
        """测试获取预设配置"""
        preset_manager = PresetManager()
        
        quick_preset = preset_manager.get_preset("quick")
        assert quick_preset is not None
        assert quick_preset["analysis_type"] == "quick"
        assert quick_preset["max_debate_rounds"] == 1
    
    def test_list_presets(self):
        """测试列出所有预设"""
        preset_manager = PresetManager()
        
        presets = preset_manager.list_presets()
        assert "quick" in presets
        assert "standard" in presets
        assert "detailed" in presets
        assert "silent" in presets
    
    def test_apply_preset(self):
        """测试应用预设配置"""
        with patch('pathlib.Path.exists', return_value=False):
            with patch('builtins.open', create=True):
                config_manager = ConfigManager()
                preset_manager = PresetManager()
                
                # 应用quick预设
                success = preset_manager.apply_preset(config_manager, "quick")
                
                assert success == True
                config = config_manager.get_config()
                assert config.max_debate_rounds == 1

class TestTradingCLI:
    """测试TradingCLI类"""
    
    def test_load_config(self):
        """测试加载配置"""
        with patch('pathlib.Path.exists', return_value=False):
            with patch('builtins.open', create=True):
                cli = TradingCLI()
                
                assert cli.config["backend_url"] == "http://localhost:8001"
                assert cli.config["default_analysis_type"] == "comprehensive"
    
    @pytest.mark.asyncio
    async def test_check_backend_health_success(self):
        """测试Backend健康检查成功"""
        with patch('pathlib.Path.exists', return_value=False):
            with patch('builtins.open', create=True):
                cli = TradingCLI()
                
                with patch.object(BackendClient, 'health_check', return_value={"success": True}):
                    result = await cli.check_backend_health()
                    assert result == True
    
    @pytest.mark.asyncio
    async def test_check_backend_health_failure(self):
        """测试Backend健康检查失败"""
        with patch('pathlib.Path.exists', return_value=False):
            with patch('builtins.open', create=True):
                cli = TradingCLI()
                
                with patch.object(BackendClient, 'health_check', return_value={"success": False, "error": "Connection failed"}):
                    result = await cli.check_backend_health()
                    assert result == False

# 集成测试
class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self):
        """测试完整分析工作流"""
        # 模拟Backend响应
        mock_responses = {
            "start_analysis": {
                "success": True,
                "data": {"analysis_id": "test-uuid-12345", "status": "started"}
            },
            "get_status_running": {
                "success": True,
                "data": {
                    "status": "running",
                    "current_step": "market_analyst",
                    "progress": {"percentage": 50.0}
                }
            },
            "get_status_completed": {
                "success": True,
                "data": {
                    "status": "completed",
                    "progress": {"percentage": 100.0}
                }
            },
            "get_result": {
                "success": True,
                "data": {
                    "result": {
                        "final_recommendation": {
                            "action": "buy",
                            "confidence": 0.75
                        }
                    }
                }
            }
        }
        
        with patch('aiohttp.ClientSession') as mock_session:
            # 配置mock响应
            mock_session_instance = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_session_instance
            
            # 模拟API调用序列
            call_count = 0
            async def mock_request(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                
                mock_response = AsyncMock()
                if call_count == 1:  # start_analysis
                    mock_response.json.return_value = mock_responses["start_analysis"]
                elif call_count == 2:  # get_status (running)
                    mock_response.json.return_value = mock_responses["get_status_running"]
                elif call_count == 3:  # get_status (completed)
                    mock_response.json.return_value = mock_responses["get_status_completed"]
                else:  # get_result
                    mock_response.json.return_value = mock_responses["get_result"]
                
                return mock_response
            
            mock_session_instance.post.return_value.__aenter__ = mock_request
            mock_session_instance.get.return_value.__aenter__ = mock_request
            
            # 执行测试
            async with BackendClient() as client:
                # 启动分析
                start_result = await client.start_analysis("000001")
                assert start_result["success"] == True
                
                analysis_id = start_result["data"]["analysis_id"]
                
                # 检查状态
                status_result = await client.get_analysis_status(analysis_id)
                assert status_result["success"] == True
                
                # 获取结果
                result = await client.get_analysis_result(analysis_id)
                assert result["success"] == True
                assert result["data"]["result"]["final_recommendation"]["action"] == "buy"

# 性能测试
class TestPerformance:
    """性能测试"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """测试并发请求"""
        mock_response = AsyncMock()
        mock_response.json.return_value = {"success": True, "status": "healthy"}
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            async with BackendClient() as client:
                # 并发发送10个健康检查请求
                tasks = [client.health_check() for _ in range(10)]
                results = await asyncio.gather(*tasks)
                
                # 验证所有请求都成功
                assert len(results) == 10
                assert all(result["success"] for result in results)

# 运行测试
if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v"])
    
    # 或者运行特定测试
    # pytest.main([__file__ + "::TestBackendClient::test_health_check_success", "-v"])
