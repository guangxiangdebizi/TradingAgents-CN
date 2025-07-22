"""
基本面分析师智能体
负责财务数据分析和估值评估
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from backend.shared.logging_config import get_logger
from backend.shared.clients.llm_client import LLMClient
from backend.shared.clients.data_client import DataClient

from ..base_agent import BaseAgent, AgentType, AgentCapability, TaskContext, TaskResult

logger = get_logger("agent-service.fundamentals_analyst")


class FundamentalsAnalyst(BaseAgent):
    """基本面分析师智能体"""
    
    def __init__(self, agent_type: AgentType, agent_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_type, agent_id, config)
        self.llm_client = LLMClient()
        self.data_client = DataClient()
        
        # 分析模板
        self.analysis_template = self._get_analysis_template()
        
        logger.info(f"🏗️ 基本面分析师初始化完成: {self.agent_id}")
    
    def _define_capabilities(self) -> List[AgentCapability]:
        """定义智能体能力"""
        return [
            AgentCapability(
                name="fundamentals_analysis",
                description="基本面分析 - 财务数据分析和估值评估",
                required_tools=["get_financial_data", "get_company_info", "calculate_ratios"],
                supported_markets=["US", "CN", "HK"],
                max_concurrent_tasks=2,
                estimated_duration=120
            ),
            AgentCapability(
                name="valuation_analysis",
                description="估值分析 - PE、PB、DCF等估值模型",
                required_tools=["get_financial_data", "get_market_data"],
                supported_markets=["US", "CN", "HK"],
                max_concurrent_tasks=1,
                estimated_duration=180
            ),
            AgentCapability(
                name="financial_health_check",
                description="财务健康检查 - 资产负债表和现金流分析",
                required_tools=["get_financial_statements"],
                supported_markets=["US", "CN", "HK"],
                max_concurrent_tasks=3,
                estimated_duration=90
            )
        ]
    
    async def process_task(self, context: TaskContext) -> TaskResult:
        """处理基本面分析任务"""
        try:
            logger.info(f"📊 开始基本面分析: {context.symbol}")
            
            # 1. 获取公司基本信息
            company_info = await self._get_company_info(context.symbol, context.market)
            
            # 2. 获取财务数据
            financial_data = await self._get_financial_data(context.symbol, context.market)
            
            # 3. 计算财务比率
            financial_ratios = await self._calculate_financial_ratios(financial_data)
            
            # 4. 进行估值分析
            valuation_analysis = await self._perform_valuation_analysis(
                context.symbol, financial_data, context.market
            )
            
            # 5. 生成分析报告
            analysis_report = await self._generate_analysis_report(
                context, company_info, financial_data, financial_ratios, valuation_analysis
            )
            
            # 6. 生成投资建议
            investment_recommendation = await self._generate_investment_recommendation(
                analysis_report, financial_ratios, valuation_analysis
            )
            
            result = {
                "analysis_type": "fundamentals_analysis",
                "symbol": context.symbol,
                "company_name": context.company_name,
                "market": context.market,
                "analysis_date": context.analysis_date,
                "company_info": company_info,
                "financial_data": financial_data,
                "financial_ratios": financial_ratios,
                "valuation_analysis": valuation_analysis,
                "analysis_report": analysis_report,
                "investment_recommendation": investment_recommendation,
                "confidence_score": self._calculate_confidence_score(financial_ratios, valuation_analysis),
                "risk_factors": self._identify_risk_factors(financial_data, financial_ratios),
                "strengths": self._identify_strengths(financial_data, financial_ratios),
                "analyst_id": self.agent_id,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ 基本面分析完成: {context.symbol}")
            
            return TaskResult(
                task_id=context.task_id,
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                status="success",
                result=result
            )
            
        except Exception as e:
            logger.error(f"❌ 基本面分析失败: {context.symbol} - {e}")
            raise
    
    async def _get_company_info(self, symbol: str, market: str) -> Dict[str, Any]:
        """获取公司基本信息"""
        try:
            response = await self.data_client.get_company_info(symbol, market)
            return response.get("data", {})
        except Exception as e:
            logger.error(f"❌ 获取公司信息失败: {symbol} - {e}")
            return {}
    
    async def _get_financial_data(self, symbol: str, market: str) -> Dict[str, Any]:
        """获取财务数据"""
        try:
            # 获取财务报表数据
            income_statement = await self.data_client.get_income_statement(symbol, market)
            balance_sheet = await self.data_client.get_balance_sheet(symbol, market)
            cash_flow = await self.data_client.get_cash_flow(symbol, market)
            
            return {
                "income_statement": income_statement.get("data", {}),
                "balance_sheet": balance_sheet.get("data", {}),
                "cash_flow": cash_flow.get("data", {}),
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ 获取财务数据失败: {symbol} - {e}")
            return {}
    
    async def _calculate_financial_ratios(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算财务比率"""
        try:
            income_statement = financial_data.get("income_statement", {})
            balance_sheet = financial_data.get("balance_sheet", {})
            
            # 提取关键财务指标
            revenue = income_statement.get("total_revenue", 0)
            net_income = income_statement.get("net_income", 0)
            total_assets = balance_sheet.get("total_assets", 0)
            total_equity = balance_sheet.get("total_equity", 0)
            total_debt = balance_sheet.get("total_debt", 0)
            current_assets = balance_sheet.get("current_assets", 0)
            current_liabilities = balance_sheet.get("current_liabilities", 0)
            
            # 计算财务比率
            ratios = {
                "profitability_ratios": {
                    "net_profit_margin": (net_income / revenue * 100) if revenue > 0 else 0,
                    "roa": (net_income / total_assets * 100) if total_assets > 0 else 0,
                    "roe": (net_income / total_equity * 100) if total_equity > 0 else 0,
                },
                "liquidity_ratios": {
                    "current_ratio": (current_assets / current_liabilities) if current_liabilities > 0 else 0,
                    "quick_ratio": ((current_assets - balance_sheet.get("inventory", 0)) / current_liabilities) if current_liabilities > 0 else 0,
                },
                "leverage_ratios": {
                    "debt_to_equity": (total_debt / total_equity) if total_equity > 0 else 0,
                    "debt_to_assets": (total_debt / total_assets) if total_assets > 0 else 0,
                },
                "efficiency_ratios": {
                    "asset_turnover": (revenue / total_assets) if total_assets > 0 else 0,
                    "equity_turnover": (revenue / total_equity) if total_equity > 0 else 0,
                }
            }
            
            return ratios
            
        except Exception as e:
            logger.error(f"❌ 计算财务比率失败: {e}")
            return {}
    
    async def _perform_valuation_analysis(self, symbol: str, financial_data: Dict[str, Any], market: str) -> Dict[str, Any]:
        """进行估值分析"""
        try:
            # 获取市场数据
            market_data = await self.data_client.get_market_data(symbol, market)
            current_price = market_data.get("data", {}).get("current_price", 0)
            market_cap = market_data.get("data", {}).get("market_cap", 0)
            
            income_statement = financial_data.get("income_statement", {})
            balance_sheet = financial_data.get("balance_sheet", {})
            
            net_income = income_statement.get("net_income", 0)
            book_value = balance_sheet.get("total_equity", 0)
            revenue = income_statement.get("total_revenue", 0)
            
            # 计算估值指标
            valuation = {
                "current_price": current_price,
                "market_cap": market_cap,
                "valuation_ratios": {
                    "pe_ratio": (market_cap / net_income) if net_income > 0 else 0,
                    "pb_ratio": (market_cap / book_value) if book_value > 0 else 0,
                    "ps_ratio": (market_cap / revenue) if revenue > 0 else 0,
                },
                "intrinsic_value_estimates": {
                    "dcf_value": await self._calculate_dcf_value(financial_data),
                    "book_value_per_share": book_value / market_data.get("data", {}).get("shares_outstanding", 1),
                },
                "valuation_summary": "待分析"
            }
            
            # 估值总结
            pe_ratio = valuation["valuation_ratios"]["pe_ratio"]
            if pe_ratio > 0:
                if pe_ratio < 15:
                    valuation["valuation_summary"] = "估值偏低，可能被低估"
                elif pe_ratio > 25:
                    valuation["valuation_summary"] = "估值偏高，可能被高估"
                else:
                    valuation["valuation_summary"] = "估值合理"
            
            return valuation
            
        except Exception as e:
            logger.error(f"❌ 估值分析失败: {e}")
            return {}
    
    async def _calculate_dcf_value(self, financial_data: Dict[str, Any]) -> float:
        """计算DCF估值（简化版）"""
        try:
            cash_flow = financial_data.get("cash_flow", {})
            free_cash_flow = cash_flow.get("free_cash_flow", 0)
            
            # 简化的DCF计算（假设5%增长率，10%折现率）
            growth_rate = 0.05
            discount_rate = 0.10
            terminal_growth = 0.02
            
            # 计算未来5年现金流现值
            dcf_value = 0
            for year in range(1, 6):
                future_cf = free_cash_flow * ((1 + growth_rate) ** year)
                present_value = future_cf / ((1 + discount_rate) ** year)
                dcf_value += present_value
            
            # 计算终值
            terminal_cf = free_cash_flow * ((1 + growth_rate) ** 5) * (1 + terminal_growth)
            terminal_value = terminal_cf / (discount_rate - terminal_growth)
            terminal_pv = terminal_value / ((1 + discount_rate) ** 5)
            
            dcf_value += terminal_pv
            
            return dcf_value
            
        except Exception as e:
            logger.error(f"❌ DCF计算失败: {e}")
            return 0
    
    async def _generate_analysis_report(
        self,
        context: TaskContext,
        company_info: Dict[str, Any],
        financial_data: Dict[str, Any],
        financial_ratios: Dict[str, Any],
        valuation_analysis: Dict[str, Any]
    ) -> str:
        """生成分析报告"""
        try:
            prompt = self.analysis_template.format(
                symbol=context.symbol,
                company_name=context.company_name,
                analysis_date=context.analysis_date,
                company_info=company_info,
                financial_data=financial_data,
                financial_ratios=financial_ratios,
                valuation_analysis=valuation_analysis
            )
            
            response = await self.llm_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="deepseek-chat",
                temperature=0.1
            )
            
            return response.get("content", "分析报告生成失败")
            
        except Exception as e:
            logger.error(f"❌ 生成分析报告失败: {e}")
            return f"分析报告生成失败: {str(e)}"
    
    async def _generate_investment_recommendation(
        self,
        analysis_report: str,
        financial_ratios: Dict[str, Any],
        valuation_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成投资建议"""
        try:
            # 基于财务比率和估值分析生成建议
            profitability = financial_ratios.get("profitability_ratios", {})
            liquidity = financial_ratios.get("liquidity_ratios", {})
            leverage = financial_ratios.get("leverage_ratios", {})
            valuation_ratios = valuation_analysis.get("valuation_ratios", {})
            
            # 计算综合评分
            score = 0
            max_score = 0
            
            # 盈利能力评分
            if profitability.get("roe", 0) > 15:
                score += 2
            elif profitability.get("roe", 0) > 10:
                score += 1
            max_score += 2
            
            # 流动性评分
            if liquidity.get("current_ratio", 0) > 2:
                score += 2
            elif liquidity.get("current_ratio", 0) > 1.5:
                score += 1
            max_score += 2
            
            # 杠杆评分
            if leverage.get("debt_to_equity", 0) < 0.3:
                score += 2
            elif leverage.get("debt_to_equity", 0) < 0.5:
                score += 1
            max_score += 2
            
            # 估值评分
            pe_ratio = valuation_ratios.get("pe_ratio", 0)
            if 0 < pe_ratio < 15:
                score += 2
            elif 15 <= pe_ratio <= 25:
                score += 1
            max_score += 2
            
            # 计算最终评分
            final_score = (score / max_score) * 100 if max_score > 0 else 0
            
            # 生成建议
            if final_score >= 80:
                recommendation = "强烈买入"
                confidence = "高"
            elif final_score >= 60:
                recommendation = "买入"
                confidence = "中"
            elif final_score >= 40:
                recommendation = "持有"
                confidence = "中"
            elif final_score >= 20:
                recommendation = "卖出"
                confidence = "中"
            else:
                recommendation = "强烈卖出"
                confidence = "高"
            
            return {
                "recommendation": recommendation,
                "confidence": confidence,
                "score": final_score,
                "reasoning": f"基于财务分析，综合评分为{final_score:.1f}分",
                "key_factors": self._get_key_factors(financial_ratios, valuation_analysis)
            }
            
        except Exception as e:
            logger.error(f"❌ 生成投资建议失败: {e}")
            return {
                "recommendation": "无法确定",
                "confidence": "低",
                "score": 0,
                "reasoning": f"分析失败: {str(e)}",
                "key_factors": []
            }
    
    def _calculate_confidence_score(self, financial_ratios: Dict[str, Any], valuation_analysis: Dict[str, Any]) -> float:
        """计算置信度评分"""
        # 基于数据完整性和一致性计算置信度
        confidence = 0.5  # 基础置信度
        
        # 检查数据完整性
        if financial_ratios and valuation_analysis:
            confidence += 0.3
        
        # 检查关键指标的合理性
        profitability = financial_ratios.get("profitability_ratios", {})
        if profitability.get("roe", 0) > 0:
            confidence += 0.1
        
        valuation_ratios = valuation_analysis.get("valuation_ratios", {})
        if valuation_ratios.get("pe_ratio", 0) > 0:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _identify_risk_factors(self, financial_data: Dict[str, Any], financial_ratios: Dict[str, Any]) -> List[str]:
        """识别风险因素"""
        risks = []
        
        leverage = financial_ratios.get("leverage_ratios", {})
        liquidity = financial_ratios.get("liquidity_ratios", {})
        profitability = financial_ratios.get("profitability_ratios", {})
        
        if leverage.get("debt_to_equity", 0) > 0.7:
            risks.append("高负债比率，财务杠杆风险较高")
        
        if liquidity.get("current_ratio", 0) < 1.2:
            risks.append("流动比率偏低，短期偿债能力不足")
        
        if profitability.get("net_profit_margin", 0) < 5:
            risks.append("净利润率偏低，盈利能力较弱")
        
        return risks
    
    def _identify_strengths(self, financial_data: Dict[str, Any], financial_ratios: Dict[str, Any]) -> List[str]:
        """识别优势"""
        strengths = []
        
        profitability = financial_ratios.get("profitability_ratios", {})
        liquidity = financial_ratios.get("liquidity_ratios", {})
        efficiency = financial_ratios.get("efficiency_ratios", {})
        
        if profitability.get("roe", 0) > 15:
            strengths.append("股东权益回报率优秀，盈利能力强")
        
        if liquidity.get("current_ratio", 0) > 2:
            strengths.append("流动比率良好，短期偿债能力强")
        
        if efficiency.get("asset_turnover", 0) > 1:
            strengths.append("资产周转率良好，资产使用效率高")
        
        return strengths
    
    def _get_key_factors(self, financial_ratios: Dict[str, Any], valuation_analysis: Dict[str, Any]) -> List[str]:
        """获取关键因素"""
        factors = []
        
        profitability = financial_ratios.get("profitability_ratios", {})
        valuation_ratios = valuation_analysis.get("valuation_ratios", {})
        
        factors.append(f"ROE: {profitability.get('roe', 0):.1f}%")
        factors.append(f"PE比率: {valuation_ratios.get('pe_ratio', 0):.1f}")
        factors.append(f"PB比率: {valuation_ratios.get('pb_ratio', 0):.1f}")
        
        return factors
    
    def _get_analysis_template(self) -> str:
        """获取分析模板"""
        return """
作为专业的基本面分析师，请对股票 {symbol} ({company_name}) 进行全面的基本面分析。

分析日期：{analysis_date}

公司信息：
{company_info}

财务数据：
{financial_data}

财务比率：
{financial_ratios}

估值分析：
{valuation_analysis}

请提供详细的基本面分析报告，包括：
1. 公司业务概况和竞争优势
2. 财务健康状况分析
3. 盈利能力评估
4. 估值水平判断
5. 主要风险因素
6. 投资亮点总结

请用专业、客观的语言进行分析，并提供具体的数据支撑。
"""
