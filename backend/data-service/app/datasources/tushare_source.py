#!/usr/bin/env python3
"""
Tushare 数据源实现
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from .base import (
    BaseDataSource, DataSourceConfig, DataSourceType, MarketType, 
    DataCategory, DataSourceError, RateLimitError, DataNotFoundError
)

logger = logging.getLogger(__name__)

class TushareDataSource(BaseDataSource):
    """Tushare 数据源"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self._client = None
        self._init_client()
    
    def _init_client(self):
        """初始化 Tushare 客户端"""
        try:
            import tushare as ts
            if self.config.api_key:
                ts.set_token(self.config.api_key)
                self._client = ts.pro_api()
                logger.info("✅ Tushare 客户端初始化成功")
            else:
                logger.warning("⚠️ Tushare API Key 未配置")
        except ImportError:
            logger.error("❌ Tushare 库未安装")
        except Exception as e:
            logger.error(f"❌ Tushare 客户端初始化失败: {e}")
    
    @property
    def supported_markets(self) -> List[MarketType]:
        return [MarketType.A_SHARE]
    
    @property
    def supported_categories(self) -> List[DataCategory]:
        return [
            DataCategory.BASIC_INFO,
            DataCategory.PRICE_DATA,
            DataCategory.FUNDAMENTALS
        ]
    
    async def get_stock_info(self, symbol: str, market: MarketType) -> Optional[Dict[str, Any]]:
        """获取股票基本信息"""
        if not self._client or market != MarketType.A_SHARE:
            return None
        
        try:
            self.record_request()
            
            # 转换股票代码格式
            ts_symbol = self._convert_symbol(symbol)
            
            # 获取股票基本信息
            df = self._client.stock_basic(ts_code=ts_symbol, fields='ts_code,symbol,name,area,industry,market,list_date')
            
            if df.empty:
                raise DataNotFoundError(self.source_type, f"股票信息未找到: {symbol}")
            
            stock_info = df.iloc[0].to_dict()
            
            # 格式化返回数据
            result = {
                "symbol": symbol,
                "name": stock_info.get("name"),
                "market": "A股",
                "industry": stock_info.get("industry"),
                "area": stock_info.get("area"),
                "list_date": stock_info.get("list_date"),
                "source": self.source_type.value,
                "timestamp": datetime.now().isoformat()
            }
            
            self.reset_error_count()
            return result
            
        except Exception as e:
            self.record_error()
            logger.error(f"❌ Tushare 获取股票信息失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, f"获取股票信息失败: {e}", e)
    
    async def get_stock_data(self, symbol: str, market: MarketType, 
                           start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """获取股票价格数据"""
        if not self._client or market != MarketType.A_SHARE:
            return None
        
        try:
            self.record_request()
            
            # 转换股票代码格式
            ts_symbol = self._convert_symbol(symbol)
            
            # 获取日线数据
            df = self._client.daily(
                ts_code=ts_symbol,
                start_date=start_date.replace("-", ""),
                end_date=end_date.replace("-", ""),
                fields='ts_code,trade_date,open,high,low,close,vol,amount'
            )
            
            if df.empty:
                raise DataNotFoundError(self.source_type, f"股票数据未找到: {symbol}")
            
            # 转换为标准格式
            result = []
            for _, row in df.iterrows():
                result.append({
                    "date": row["trade_date"][:4] + "-" + row["trade_date"][4:6] + "-" + row["trade_date"][6:8],
                    "open": float(row["open"]) if row["open"] else None,
                    "high": float(row["high"]) if row["high"] else None,
                    "low": float(row["low"]) if row["low"] else None,
                    "close": float(row["close"]) if row["close"] else None,
                    "volume": int(row["vol"]) if row["vol"] else None,
                    "amount": float(row["amount"]) if row["amount"] else None,
                })
            
            # 按日期排序
            result.sort(key=lambda x: x["date"])
            
            self.reset_error_count()
            return result
            
        except Exception as e:
            self.record_error()
            logger.error(f"❌ Tushare 获取股票数据失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, f"获取股票数据失败: {e}", e)
    
    async def get_fundamentals(self, symbol: str, market: MarketType,
                             start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """获取基本面数据"""
        if not self._client or market != MarketType.A_SHARE:
            return None
        
        try:
            self.record_request()
            
            # 转换股票代码格式
            ts_symbol = self._convert_symbol(symbol)
            
            # 获取财务数据
            df = self._client.fina_indicator(
                ts_code=ts_symbol,
                start_date=start_date.replace("-", ""),
                end_date=end_date.replace("-", ""),
                fields='ts_code,ann_date,end_date,eps,dt_eps,total_revenue_ps,revenue_ps,capital_rese_ps,surplus_rese_ps,undist_profit_ps,extra_item,profit_dedt,gross_margin,current_ratio,quick_ratio,cash_ratio,invturn_days,arturn_days,inv_turn,ar_turn,ca_turn,fa_turn,assets_turn,op_income,valuechange_income,interst_income,daa,ebit,ebitda,fcff,fcfe,current_exint,noncurrent_exint,interestdebt,netdebt,tangible_asset,working_capital,networking_capital,invest_capital,retained_earnings,diluted2_eps,bps,ocfps,retainedps,cfps,ebit_ps,fcff_ps,fcfe_ps,netprofit_margin,grossprofit_margin,cogs_of_sales,expense_of_sales,profit_to_gr,saleexp_to_gr,adminexp_of_gr,finaexp_of_gr,impai_ttm,gc_of_gr,op_of_gr,ebit_of_gr,roe,roe_waa,roe_dt,roa,npta,roic,roe_yearly,roa_yearly,roe_avg,opincome_of_ebt,investincome_of_ebt,n_op_profit_of_ebt,tax_to_ebt,dtprofit_to_profit,salescash_to_or,ocf_to_or,ocf_to_opincome,capitalized_to_da,debt_to_assets,assets_to_eqt,dp_assets_to_eqt,ca_to_assets,nca_to_assets,tbassets_to_totalassets,int_to_talcap,eqt_to_talcapital,currentdebt_to_debt,longdeb_to_debt,ocf_to_shortdebt,debt_to_eqt,eqt_to_debt,eqt_to_interestdebt,tangibleasset_to_debt,tangasset_to_intdebt,tangibleasset_to_netdebt,ocf_to_debt,ocf_to_interestdebt,ocf_to_netdebt,ebit_to_interest,longdebt_to_workingcapital,ebitda_to_debt,turn_days,roa_yearly,roa_dp,fixed_assets,profit_prefin_exp,non_op_profit,op_to_ebt,nop_to_ebt,ocf_to_profit,cash_to_liqdebt,cash_to_liqdebt_withinterest,op_to_liqdebt,op_to_debt,roic_yearly,total_fa_trun,profit_to_op,q_opincome,q_investincome,q_dtprofit,q_eps,q_netprofit_margin,q_gsprofit_margin,q_exp_to_sales,q_profit_to_gr,q_saleexp_to_gr,q_adminexp_to_gr,q_finaexp_to_gr,q_impair_to_gr_ttm,q_gc_to_gr,q_op_to_gr,q_roe,q_dt_roe,q_npta,q_opincome_to_ebt,q_investincome_to_ebt,q_dtprofit_to_profit,q_salescash_to_or,q_ocf_to_sales,q_ocf_to_or,basic_eps_yoy,dt_eps_yoy,cfps_yoy,op_yoy,ebt_yoy,netprofit_yoy,dt_netprofit_yoy,ocf_yoy,roe_yoy,bps_yoy,assets_yoy,eqt_yoy,tr_yoy,or_yoy,q_gr_yoy,q_gr_qoq,q_sales_yoy,q_sales_qoq,q_op_yoy,q_op_qoq,q_profit_yoy,q_profit_qoq,q_netprofit_yoy,q_netprofit_qoq,equity_yoy,rd_exp,update_flag'
            )
            
            if df.empty:
                raise DataNotFoundError(self.source_type, f"基本面数据未找到: {symbol}")
            
            # 取最新的数据
            latest_data = df.iloc[0].to_dict()
            
            # 格式化返回数据
            result = {
                "symbol": symbol,
                "report_date": latest_data.get("end_date"),
                "announce_date": latest_data.get("ann_date"),
                "eps": float(latest_data.get("eps")) if latest_data.get("eps") else None,
                "roe": float(latest_data.get("roe")) if latest_data.get("roe") else None,
                "roa": float(latest_data.get("roa")) if latest_data.get("roa") else None,
                "gross_margin": float(latest_data.get("gross_margin")) if latest_data.get("gross_margin") else None,
                "net_margin": float(latest_data.get("netprofit_margin")) if latest_data.get("netprofit_margin") else None,
                "current_ratio": float(latest_data.get("current_ratio")) if latest_data.get("current_ratio") else None,
                "quick_ratio": float(latest_data.get("quick_ratio")) if latest_data.get("quick_ratio") else None,
                "debt_to_assets": float(latest_data.get("debt_to_assets")) if latest_data.get("debt_to_assets") else None,
                "source": self.source_type.value,
                "timestamp": datetime.now().isoformat()
            }
            
            self.reset_error_count()
            return result
            
        except Exception as e:
            self.record_error()
            logger.error(f"❌ Tushare 获取基本面数据失败 {symbol}: {e}")
            raise DataSourceError(self.source_type, f"获取基本面数据失败: {e}", e)
    
    async def get_news(self, symbol: str, market: MarketType,
                      start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """获取新闻数据 - Tushare 不支持新闻数据"""
        return None
    
    def _convert_symbol(self, symbol: str) -> str:
        """转换股票代码为 Tushare 格式"""
        if "." in symbol:
            return symbol
        
        # A股代码转换
        if symbol.startswith("00") or symbol.startswith("30"):
            return f"{symbol}.SZ"  # 深交所
        elif symbol.startswith("60") or symbol.startswith("68"):
            return f"{symbol}.SH"  # 上交所
        else:
            return symbol
    
    async def health_check(self) -> bool:
        """健康检查"""
        if not self._client:
            return False
        
        try:
            # 尝试获取一个简单的数据
            df = self._client.trade_cal(start_date='20240101', end_date='20240102')
            return not df.empty
        except Exception as e:
            logger.error(f"❌ Tushare 健康检查失败: {e}")
            self.status = DataSourceStatus.ERROR
            return False
