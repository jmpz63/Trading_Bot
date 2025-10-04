"""
Complete Trading Dashboard
Real-time monitoring and management interface
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import json
import sys
import os
from pathlib import Path

# Add the Trade_Bot directory to the path
trade_bot_dir = Path(__file__).parent
sys.path.append(str(trade_bot_dir))

# Import our modules
from enhanced_trading_system import EnhancedTradingSystem
from paper_trading_system import PaperTradingPortfolio
from performance_analytics import TradePerformanceAnalyzer

# Page config
st.set_page_config(
    page_title="Trading Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_market_data(symbols):
    """Load current market data for symbols"""
    data = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="5d")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                change = current_price - prev_close
                change_pct = (change / prev_close) * 100 if prev_close != 0 else 0
                
                data[symbol] = {
                    'current_price': current_price,
                    'change': change,
                    'change_pct': change_pct,
                    'volume': hist['Volume'].iloc[-1],
                    'high_52w': info.get('fiftyTwoWeekHigh', 0),
                    'low_52w': info.get('fiftyTwoWeekLow', 0)
                }
        except Exception as e:
            st.error(f"Error loading data for {symbol}: {e}")
            
    return data

def create_portfolio_chart(portfolio):
    """Create portfolio performance chart"""
    
    daily_file = Path("data/paper_trading/daily_performance.json")
    
    if not daily_file.exists():
        return None
    
    with open(daily_file, 'r') as f:
        daily_data = json.load(f)
    
    if not daily_data:
        return None
    
    df = pd.DataFrame(daily_data)
    df['date'] = pd.to_datetime(df['date'])
    df['return_pct'] = (df['total_portfolio_value'] / df['total_portfolio_value'].iloc[0] - 1) * 100
    
    fig = go.Figure()
    
    # Portfolio value line
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['total_portfolio_value'],
        mode='lines+markers',
        name='Portfolio Value',
        line=dict(color='#1f77b4', width=3),
        hovertemplate='Date: %{x}<br>Value: $%{y:,.2f}<extra></extra>'
    ))
    
    # Add benchmark line (starting value)
    fig.add_hline(
        y=df['total_portfolio_value'].iloc[0],
        line_dash="dash",
        line_color="gray",
        annotation_text="Starting Value"
    )
    
    fig.update_layout(
        title="Portfolio Performance Over Time",
        xaxis_title="Date",
        yaxis_title="Portfolio Value ($)",
        hovermode='x unified',
        showlegend=True
    )
    
    return fig

def create_positions_chart(portfolio):
    """Create current positions chart"""
    
    positions = portfolio.get_positions()
    
    if not positions:
        return None
    
    symbols = list(positions.keys())
    values = []
    colors = []
    
    for symbol in symbols:
        pos = positions[symbol]
        current_value = pos['shares'] * pos['current_price']
        values.append(current_value)
        
        # Color based on P&L
        pnl = pos['unrealized_pnl']
        if pnl > 0:
            colors.append('#00ff00')  # Green for profit
        elif pnl < 0:
            colors.append('#ff0000')  # Red for loss
        else:
            colors.append('#888888')  # Gray for breakeven
    
    fig = go.Figure(data=[
        go.Pie(
            labels=symbols,
            values=values,
            marker_colors=colors,
            textinfo='label+percent',
            hovertemplate='%{label}<br>Value: $%{value:,.2f}<br>Percent: %{percent}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="Current Positions Distribution",
        showlegend=True
    )
    
    return fig

def main():
    """Main dashboard function"""
    
    st.title("📊 Trading Dashboard")
    st.markdown("Real-time trading performance and portfolio monitoring")
    
    # Sidebar
    st.sidebar.title("🎯 Trading Controls")
    
    # Initialize systems
    if 'enhanced_system' not in st.session_state:
        st.session_state.enhanced_system = EnhancedTradingSystem()
    
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = PaperTradingPortfolio()
    
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = TradePerformanceAnalyzer()
    
    enhanced_system = st.session_state.enhanced_system
    portfolio = st.session_state.portfolio
    analyzer = st.session_state.analyzer
    
    # Portfolio summary in sidebar
    portfolio_value = portfolio.get_portfolio_value()
    cash_balance = portfolio.cash_balance
    
    st.sidebar.metric(
        "💰 Portfolio Value",
        f"${portfolio_value:,.2f}",
        f"{((portfolio_value / 10000 - 1) * 100):+.2f}%"
    )
    
    st.sidebar.metric(
        "💵 Cash Balance",
        f"${cash_balance:,.2f}"
    )
    
    # Quick trade section
    st.sidebar.subheader("🚀 Quick Trade")
    
    trade_symbol = st.sidebar.text_input("Symbol", value="SPY")
    trade_action = st.sidebar.selectbox("Action", ["BUY", "SELL"])
    trade_amount = st.sidebar.number_input("Amount ($)", min_value=100, value=1000, step=100)
    
    if st.sidebar.button("Execute Trade"):
        if trade_symbol:
            try:
                if trade_action == "BUY":
                    result = portfolio.buy_stock(trade_symbol, trade_amount)
                else:
                    # For sell, convert amount to approximate shares
                    ticker = yf.Ticker(trade_symbol)
                    current_price = ticker.history(period="1d")['Close'].iloc[-1]
                    shares = int(trade_amount / current_price)
                    result = portfolio.sell_stock(trade_symbol, shares)
                
                if result['success']:
                    st.sidebar.success(f"✅ {trade_action} order executed!")
                else:
                    st.sidebar.error(f"❌ {result['message']}")
                    
            except Exception as e:
                st.sidebar.error(f"❌ Error: {e}")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "📊 Positions", "🎯 Signals", "📋 Performance"])
    
    with tab1:
        st.subheader("📈 Portfolio Overview")
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            daily_pnl = portfolio.calculate_daily_pnl()
            st.metric(
                "📊 Daily P&L",
                f"${daily_pnl:+,.2f}",
                f"{(daily_pnl / portfolio_value * 100):+.2f}%"
            )
        
        with col2:
            positions = portfolio.get_positions()
            unrealized_pnl = sum(pos['unrealized_pnl'] for pos in positions.values())
            st.metric(
                "💹 Unrealized P&L",
                f"${unrealized_pnl:+,.2f}"
            )
        
        with col3:
            total_trades = len(portfolio.trade_history)
            st.metric(
                "🔢 Total Trades",
                total_trades
            )
        
        with col4:
            # Market status
            now = datetime.now()
            market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
            
            if market_open <= now <= market_close and now.weekday() < 5:
                st.metric("🟢 Market", "OPEN", "")
            else:
                st.metric("🔴 Market", "CLOSED", "")
        
        # Portfolio chart
        portfolio_chart = create_portfolio_chart(portfolio)
        if portfolio_chart:
            st.plotly_chart(portfolio_chart, use_container_width=True)
        else:
            st.info("📊 Start trading to see portfolio performance chart")
    
    with tab2:
        st.subheader("📊 Current Positions")
        
        positions = portfolio.get_positions()
        
        if positions:
            # Positions table
            positions_data = []
            
            for symbol, pos in positions.items():
                positions_data.append({
                    'Symbol': symbol,
                    'Shares': pos['shares'],
                    'Avg Cost': f"${pos['avg_price']:.2f}",
                    'Current Price': f"${pos['current_price']:.2f}",
                    'Market Value': f"${pos['shares'] * pos['current_price']:,.2f}",
                    'Unrealized P&L': f"${pos['unrealized_pnl']:+,.2f}",
                    'P&L %': f"{pos['unrealized_pnl_pct']:+.2f}%"
                })
            
            positions_df = pd.DataFrame(positions_data)
            st.dataframe(positions_df, use_container_width=True)
            
            # Positions pie chart
            positions_chart = create_positions_chart(portfolio)
            if positions_chart:
                st.plotly_chart(positions_chart, use_container_width=True)
        else:
            st.info("📊 No current positions. Start trading to build your portfolio!")
        
        # Cash allocation
        st.subheader("💰 Cash Allocation")
        cash_pct = (cash_balance / portfolio_value) * 100
        invested_pct = 100 - cash_pct
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💵 Cash", f"${cash_balance:,.2f}", f"{cash_pct:.1f}%")
        with col2:
            invested_value = portfolio_value - cash_balance
            st.metric("📈 Invested", f"${invested_value:,.2f}", f"{invested_pct:.1f}%")
    
    with tab3:
        st.subheader("🎯 Current Trading Signals")
        
        # Get fresh analysis
        if st.button("🔄 Refresh Signals"):
            with st.spinner("Analyzing market conditions..."):
                try:
                    # Analyze top stocks
                    top_stocks = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'TSLA']
                    
                    signals = []
                    for symbol in top_stocks:
                        try:
                            analysis = enhanced_system.analyze_stock(symbol)
                            signals.append({
                                'Symbol': symbol,
                                'Signal': analysis['recommendation'],
                                'Score': f"{analysis['overall_score']:.1f}/100",
                                'Price': f"${analysis['current_price']:.2f}",
                                'Regime': analysis['market_regime']
                            })
                        except:
                            continue
                    
                    if signals:
                        signals_df = pd.DataFrame(signals)
                        
                        # Color code signals
                        def color_signal(val):
                            if val == 'BUY':
                                return 'background-color: #90EE90'  # Light green
                            elif val == 'SELL':
                                return 'background-color: #FFB6C1'  # Light red
                            else:
                                return 'background-color: #FFFFE0'  # Light yellow
                        
                        styled_df = signals_df.style.applymap(color_signal, subset=['Signal'])
                        st.dataframe(styled_df, use_container_width=True)
                    else:
                        st.error("❌ Unable to fetch current signals")
                        
                except Exception as e:
                    st.error(f"❌ Error analyzing signals: {e}")
        
        # Market overview
        st.subheader("📊 Market Overview")
        
        # Load key market data
        market_symbols = ['SPY', 'QQQ', 'DIA', 'IWM']
        market_data = load_market_data(market_symbols)
        
        if market_data:
            market_cols = st.columns(4)
            
            for i, (symbol, data) in enumerate(market_data.items()):
                with market_cols[i % 4]:
                    st.metric(
                        symbol,
                        f"${data['current_price']:.2f}",
                        f"{data['change_pct']:+.2f}%"
                    )
    
    with tab4:
        st.subheader("📋 Performance Analytics")
        
        # Performance metrics
        if st.button("📊 Generate Performance Report"):
            with st.spinner("Calculating performance metrics..."):
                
                # Get comprehensive metrics
                trade_stats = analyzer.calculate_trade_statistics()
                portfolio_metrics = analyzer.calculate_portfolio_metrics()
                
                if 'error' not in trade_stats:
                    st.subheader("🎯 Trade Statistics")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Trades", trade_stats['total_trades'])
                        st.metric("Win Rate", f"{trade_stats['win_rate']:.1f}%")
                    
                    with col2:
                        st.metric("Avg Win", f"${trade_stats['avg_win']:.2f}")
                        st.metric("Avg Loss", f"${trade_stats['avg_loss']:.2f}")
                    
                    with col3:
                        st.metric("Profit Factor", f"{trade_stats['profit_factor']:.2f}")
                        st.metric("Realized P&L", f"${trade_stats['total_realized_pnl']:+,.2f}")
                
                if 'error' not in portfolio_metrics:
                    st.subheader("📈 Portfolio Metrics")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Return", f"{portfolio_metrics['total_return']:+.2f}%")
                        st.metric("Volatility", f"{portfolio_metrics['volatility']:.2f}%")
                    
                    with col2:
                        st.metric("Sharpe Ratio", f"{portfolio_metrics['sharpe_ratio']:.2f}")
                        st.metric("Max Drawdown", f"{portfolio_metrics['max_drawdown']:.2f}%")
                    
                    with col3:
                        st.metric("Best Day", f"{portfolio_metrics['best_day']:+.2f}%")
                        st.metric("Worst Day", f"{portfolio_metrics['worst_day']:+.2f}%")
                
                # Full report
                st.subheader("📄 Detailed Report")
                report = analyzer.generate_performance_report()
                st.text(report)
        
        # Recent trades
        st.subheader("📋 Recent Trades")
        
        if portfolio.trade_history:
            recent_trades = portfolio.trade_history[-10:]  # Last 10 trades
            
            trades_data = []
            for trade in recent_trades:
                trades_data.append({
                    'Date': pd.to_datetime(trade['timestamp']).strftime('%Y-%m-%d %H:%M'),
                    'Symbol': trade['symbol'],
                    'Action': trade['action'],
                    'Shares': trade['shares'],
                    'Price': f"${trade['price']:.2f}",
                    'Value': f"${trade['trade_value']:,.2f}"
                })
            
            trades_df = pd.DataFrame(trades_data)
            st.dataframe(trades_df, use_container_width=True)
        else:
            st.info("📊 No trades yet. Start trading to see your history!")
    
    # Auto-refresh
    if st.sidebar.checkbox("🔄 Auto-refresh (30s)"):
        st.rerun()

if __name__ == "__main__":
    main()