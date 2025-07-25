"""
基本面分析师智能体
移植自tradingagents，负责财务数据分析和公司基本面评估
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..base.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class FundamentalsAnalyst(BaseAgent):
    """
    基本面分析师智能体
    专注于财务数据分析、公司基本面评估和价值投资分析
    """
    
    def __init__(self, llm_client=None, data_client=None):
        super().__init__(
            name="FundamentalsAnalyst",
            description="专业的基本面分析师，擅长财务分析和公司价值评估",
            llm_client=llm_client,
            data_client=data_client
        )
        self.prompt_template = None
    
    async def _load_prompts(self):
        """加载基本面分析提示词模板"""
        self.prompt_template = """
你是一位专业的基本面分析师，具有丰富的财务分析和公司估值经验。

请对公司 {symbol} 进行全面的基本面分析，包括：

## 分析要求：
1. **财务健康状况**：资产负债表、现金流量表分析
2. **盈利能力分析**：ROE、ROA、毛利率、净利率等
3. **成长性分析**：营收增长、利润增长趋势
4. **估值分析**：P/E、P/B、PEG等估值指标
5. **行业对比**：与同行业公司的对比分析
6. **风险评估**：财务风险、经营风险识别

## 财务数据：
{financial_data}

## 行业信息：
{industry_data}

## 输出格式：
请提供详细的基本面分析报告，包含具体的财务数据和专业判断。

## 投资建议：
基于基本面分析给出投资价值评估和建议。
"""
    
    async def analyze(self, symbol: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行基本面分析
        
        Args:
            symbol: 股票代码
            context: 分析上下文
            
        Returns:
            基本面分析结果
        """
        self._log_analysis_start(symbol)
        
        try:
            # 1. 获取财务数据
            financial_data = await self._get_financial_data(symbol, context)
            
            # 2. 获取行业数据
            industry_data = await self._get_industry_data(symbol, context)
            
            # 3. 计算财务指标
            financial_ratios = await self._calculate_financial_ratios(financial_data)
            
            # 4. 生成AI分析报告
            ai_analysis = await self._generate_ai_analysis(
                symbol, financial_data, industry_data, financial_ratios
            )
            
            # 5. 整合分析结果
            result = {
                "analysis_type": "fundamentals_analysis",
                "symbol": symbol,
                "analyst": self.name,
                "timestamp": datetime.now().isoformat(),
                "financial_data_summary": financial_data.get("summary", ""),
                "financial_ratios": financial_ratios,
                "industry_comparison": industry_data,
                "ai_analysis": ai_analysis,
                "valuation": self._extract_valuation(ai_analysis),
                "investment_grade": self._calculate_investment_grade(financial_ratios)
            }
            
            self._log_analysis_complete(symbol, f"评级: {result['investment_grade']}")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ [{self.name}] 分析失败: {symbol} - {e}")
            return {
                "analysis_type": "fundamentals_analysis",
                "symbol": symbol,
                "analyst": self.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_financial_data(self, symbol: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取财务数据"""
        try:
            if self.data_client:
                data = await self.data_client.get_financial_statements(symbol)
                return data
            else:
                # 模拟财务数据
                return {
                    "symbol": symbol,
                    "revenue": 1000000000,  # 10亿营收
                    "net_income": 100000000,  # 1亿净利润
                    "total_assets": 2000000000,  # 20亿总资产
                    "total_equity": 800000000,  # 8亿股东权益
                    "cash": 200000000,  # 2亿现金
                    "debt": 500000000,  # 5亿负债
                    "summary": f"获取到{symbol}的财务数据"
                }
        except Exception as e:
            self.logger.error(f"❌ 获取财务数据失败: {e}")
            return {"error": str(e)}
    
    async def _get_industry_data(self, symbol: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取行业数据"""
        try:
            if self.data_client:
                data = await self.data_client.get_industry_data(symbol)
                return data
            else:
                # 模拟行业数据
                return {
                    "industry": "科技",
                    "industry_pe": 25.5,
                    "industry_pb": 3.2,
                    "industry_roe": 0.15,
                    "market_cap_rank": "大盘股"
                }
        except Exception as e:
            self.logger.error(f"❌ 获取行业数据失败: {e}")
            return {}
    
    async def _calculate_financial_ratios(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算财务比率"""
        try:
            if "error" in financial_data:
                return {}
            
            revenue = financial_data.get("revenue", 0)
            net_income = financial_data.get("net_income", 0)
            total_assets = financial_data.get("total_assets", 1)
            total_equity = financial_data.get("total_equity", 1)
            
            return {
                "roe": net_income / total_equity if total_equity > 0 else 0,  # 净资产收益率
                "roa": net_income / total_assets if total_assets > 0 else 0,  # 总资产收益率
                "profit_margin": net_income / revenue if revenue > 0 else 0,  # 净利率
                "debt_to_equity": financial_data.get("debt", 0) / total_equity if total_equity > 0 else 0,
                "current_ratio": financial_data.get("cash", 0) / financial_data.get("debt", 1),  # 简化的流动比率
            }
        except Exception as e:
            self.logger.error(f"❌ 计算财务比率失败: {e}")
            return {}
    
    async def _generate_ai_analysis(self, symbol: str, financial_data: Dict, 
                                  industry_data: Dict, financial_ratios: Dict) -> str:
        """生成AI分析报告"""
        try:
            if self.llm_client:
                prompt = self.prompt_template.format(
                    symbol=symbol,
                    financial_data=str(financial_data),
                    industry_data=str(industry_data)
                )
                
                response = await self.llm_client.generate(
                    prompt=prompt,
                    context={"financial_ratios": financial_ratios}
                )
                
                return response.get("content", "AI分析生成失败")
            else:
                # 模拟AI分析
                roe = financial_ratios.get("roe", 0)
                profit_margin = financial_ratios.get("profit_margin", 0)
                debt_to_equity = financial_ratios.get("debt_to_equity", 0)
                
                return f"""
## {symbol} 基本面分析报告

### 财务健康状况
- 净资产收益率(ROE): {roe:.2%}
- 净利率: {profit_margin:.2%}
- 资产负债率: {debt_to_equity:.2f}

### 盈利能力分析
公司盈利能力{'良好' if roe > 0.1 else '一般'}，净利率{'较高' if profit_margin > 0.1 else '适中'}。

### 财务风险评估
债务水平{'偏高' if debt_to_equity > 1 else '合理'}，财务结构{'需要关注' if debt_to_equity > 1.5 else '稳健'}。

### 投资价值评估
基于当前财务状况，公司{'具有投资价值' if roe > 0.1 and debt_to_equity < 1 else '需要谨慎评估'}。
"""
        except Exception as e:
            self.logger.error(f"❌ AI分析生成失败: {e}")
            return f"AI分析生成失败: {str(e)}"
    
    def _extract_valuation(self, ai_analysis: str) -> str:
        """从AI分析中提取估值结论"""
        try:
            if "高估" in ai_analysis:
                return "高估"
            elif "低估" in ai_analysis:
                return "低估"
            else:
                return "合理估值"
        except:
            return "合理估值"
    
    def _calculate_investment_grade(self, financial_ratios: Dict) -> str:
        """计算投资评级"""
        try:
            roe = financial_ratios.get("roe", 0)
            debt_to_equity = financial_ratios.get("debt_to_equity", 0)
            profit_margin = financial_ratios.get("profit_margin", 0)
            
            score = 0
            if roe > 0.15:
                score += 2
            elif roe > 0.1:
                score += 1
            
            if debt_to_equity < 0.5:
                score += 2
            elif debt_to_equity < 1:
                score += 1
            
            if profit_margin > 0.1:
                score += 1
            
            if score >= 4:
                return "A级"
            elif score >= 2:
                return "B级"
            else:
                return "C级"
        except:
            return "B级"
