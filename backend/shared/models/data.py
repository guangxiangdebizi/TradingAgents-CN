"""
数据相关的模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class StockDataRequest(BaseModel):
    """股票数据请求模型"""
    symbol: str = Field(..., description="股票代码")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    data_source: Optional[str] = Field(default=None, description="数据源")


class StockInfo(BaseModel):
    """股票基本信息模型"""
    symbol: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    market: str = Field(..., description="市场")
    industry: Optional[str] = Field(default=None, description="行业")
    sector: Optional[str] = Field(default=None, description="板块")
    market_cap: Optional[float] = Field(default=None, description="市值")
    currency: Optional[str] = Field(default=None, description="货币")


class StockPrice(BaseModel):
    """股票价格数据模型"""
    symbol: str = Field(..., description="股票代码")
    date: str = Field(..., description="日期")
    open: float = Field(..., description="开盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    close: float = Field(..., description="收盘价")
    volume: Optional[int] = Field(default=None, description="成交量")
    amount: Optional[float] = Field(default=None, description="成交额")


class MarketData(BaseModel):
    """市场数据模型"""
    symbol: str = Field(..., description="股票代码")
    current_price: float = Field(..., description="当前价格")
    change: float = Field(..., description="价格变化")
    change_percent: float = Field(..., description="变化百分比")
    volume: Optional[int] = Field(default=None, description="成交量")
    market_cap: Optional[float] = Field(default=None, description="市值")
    pe_ratio: Optional[float] = Field(default=None, description="市盈率")
    pb_ratio: Optional[float] = Field(default=None, description="市净率")
    timestamp: datetime = Field(default_factory=datetime.now, description="数据时间")


class NewsItem(BaseModel):
    """新闻数据模型"""
    title: str = Field(..., description="新闻标题")
    content: Optional[str] = Field(default=None, description="新闻内容")
    source: str = Field(..., description="新闻来源")
    url: Optional[str] = Field(default=None, description="新闻链接")
    publish_time: datetime = Field(..., description="发布时间")
    sentiment: Optional[str] = Field(default=None, description="情绪倾向")


class FundamentalData(BaseModel):
    """基本面数据模型"""
    symbol: str = Field(..., description="股票代码")
    revenue: Optional[float] = Field(default=None, description="营业收入")
    net_income: Optional[float] = Field(default=None, description="净利润")
    total_assets: Optional[float] = Field(default=None, description="总资产")
    total_equity: Optional[float] = Field(default=None, description="股东权益")
    roe: Optional[float] = Field(default=None, description="净资产收益率")
    roa: Optional[float] = Field(default=None, description="总资产收益率")
    debt_ratio: Optional[float] = Field(default=None, description="资产负债率")
    report_date: str = Field(..., description="报告期")


class DataSourceStatus(BaseModel):
    """数据源状态模型"""
    source_name: str = Field(..., description="数据源名称")
    status: str = Field(..., description="状态")
    last_update: datetime = Field(..., description="最后更新时间")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    api_calls_today: Optional[int] = Field(default=None, description="今日API调用次数")
    api_limit: Optional[int] = Field(default=None, description="API调用限制")
