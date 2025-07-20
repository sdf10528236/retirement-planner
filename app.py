import streamlit as st
import numpy as np
import pandas as pd

st.title("退休資產需求推估")

# 投資標的資料
portfolio_data = {
    "60/40 股債配": {"mean_return": 6.0, "std_dev": 8.5},
    "VT (全市場 ETF)": {"mean_return": 8.05, "std_dev": 15.76},
    "0050 (台灣50)": {"mean_return": 8.5, "std_dev": 15.5},
    "0056 (高股息)": {"mean_return": 7.5, "std_dev": 12.5},
}

#提領策略
strategy_data = {
    "每年固定提領": {"value": "fix"},
    "GK動態提領": {"value": "GK"}
}

# 退休後模擬輸入
with st.expander("退休後資產需求模擬", expanded=True):
    monthly_expense = st.number_input("退休後每月花費（萬元）", min_value=0, value=4, key="monthly_expense")
    years_to_live = st.number_input("退休後預期存活年數", min_value=1, value=35, key="years_to_live")
    portfolio = st.selectbox("選擇投資標的", options=list(portfolio_data.keys()), key="portfolio")
    mean_return = portfolio_data[portfolio]["mean_return"]
    std_dev = portfolio_data[portfolio]["std_dev"]
    mean_return = st.number_input("年平均報酬率（%）", min_value=0.0, max_value=15.0, value=mean_return, key="mean_return")
    std_dev = st.number_input("年報酬率波動度（標準差%）", min_value=0.0, max_value=30.0, value=std_dev, key="std_dev")
    inflation = st.number_input("年通膨率（%）", min_value=0.0, max_value=10.0, value=2.0, key="inflation")
    simulations = st.number_input("模擬次數 (最多2000)", min_value=1, max_value=2000, value=1000, key="simulations")
    withdraw_strategy = st.selectbox("提領策略 (提領策略會影響退休所需金額)", options=list(strategy_data.keys()))
    target_success_rate = st.slider("目標成功率(%)", 50, 100, 95, key="target_success_rate") / 100

    base_annual_expense = monthly_expense * 12

    def monte_carlo_sim(initial_asset):
        success_count = 0
        assets_over_time = np.zeros((simulations, years_to_live))
        for sim in range(simulations):
            asset = initial_asset
            returns = np.random.normal(loc=mean_return/100, scale=std_dev/100, size=years_to_live)
            withdraw_rate=base_annual_expense/initial_asset
            annual_expense=base_annual_expense

            for year, r in enumerate(returns):
                real_return = (1 + r) / (1 + inflation/100) - 1
                last_asset=asset

                if strategy_data[withdraw_strategy]["value"] == "fix":
                    asset = asset * (1 + real_return) - annual_expense
                    annual_expense *= (1 + inflation/100)
                elif strategy_data[withdraw_strategy]["value"] == "GK":
                    asset = asset * (1 + real_return)
                    if asset > last_asset:
                        if year == 0:
                            annual_expense=annual_expense
                        else:
                            annual_expense *= (1 + inflation/100) 
                        #在市場上漲退休金變多時，如果導致當前提領率比初始提領率低過20%時，就必須把當前提領率上調10%，以免退休金太多花不完。
                        if ((annual_expense/asset)-withdraw_rate) < withdraw_rate*(-0.2):
                            annual_expense=annual_expense*1.1
                    else: 
                        #如果前一年退休金是虧損的，今年的提領金額就不隨通膨進行調整
                        #在市場下跌時退休金的總價值會降低，若導致當前提領率比初始提領率超出20%時，就必須把當前提領率下調10%，以免退休金油盡燈枯。
                        if ((annual_expense/asset)-withdraw_rate) > withdraw_rate*0.2:
                            annual_expense=annual_expense*0.9
                    asset=asset-annual_expense

                asset = max(asset, 0)
                assets_over_time[sim, year] = asset
                if asset <= 0:
                    assets_over_time[sim, year:] = 0
                    break
            if asset > 0:
                success_count += 1
        success_rate = success_count / simulations
        return success_rate, assets_over_time

    if st.button("開始模擬", key="simulate_retire"):
        low, high = 0.0, 1_000_000.0
        tolerance = 100
        result_asset = high
        with st.spinner("模擬中，請稍候..."):
            while high - low > tolerance:
                mid = (low + high) / 2
                rate, _ = monte_carlo_sim(mid)
                if rate >= target_success_rate:
                    result_asset = mid
                    high = mid
                else:
                    low = mid
            final_success, final_assets = monte_carlo_sim(result_asset)
        
        st.session_state["retire_result_asset"] = result_asset
        st.session_state["retire_final_assets"] = final_assets
        st.session_state["retire_years_to_live"] = years_to_live
        
    if "retire_result_asset" in st.session_state:
        st.success(f"要達到 {target_success_rate*100:.1f}% 成功率，初始資產至少要：**{st.session_state['retire_result_asset']:,.0f} 萬元**")
        percentiles = np.percentile(st.session_state["retire_final_assets"], [25, 50, 75], axis=0)
        years = list(range(1, st.session_state["retire_years_to_live"] + 1))
        df = pd.DataFrame({
            "25%": percentiles[0],
            "中位數": percentiles[1],
            "75%": percentiles[2]
        }, index=years)
        initial_row = pd.DataFrame({
            "25%": [st.session_state["retire_result_asset"]],
            "中位數": [st.session_state["retire_result_asset"]],
            "75%": [st.session_state["retire_result_asset"]]
        }, index=[0])
        df = pd.concat([initial_row, df])
        st.subheader("模擬資產走勢（含 25%、中位數、75%）")
        st.line_chart(df)

st.markdown("---")

# 定期定額達標時間估算
with st.expander("定期定額達標所需時間估算", expanded=True):
    asset_options = {
        "VT（全市場 ETF）": 0.08,
        "0050（台灣50）": 0.09,
        "SPY（S&P 500）": 0.105,
        "60/40 股債配": 0.065,
    }

    initial_capital = st.number_input("初始本金（萬元）", min_value=0, value=100, key="initial_capital")
    monthly_invest = st.number_input("每月定期投入金額（萬元）", min_value=0.0, value=2.0, key="monthly_invest")
    target_asset = st.number_input("目標資產（萬元）", min_value=1, value=1500, key="target_asset")
    selected_asset = st.selectbox("選擇投資標的", list(asset_options.keys()), key="selected_asset")
    annual_return = asset_options[selected_asset]
    st.markdown(f"📈 **{selected_asset} 長期年化報酬率：{annual_return * 100:.1f}%**")

    def calculate_years_to_goal(initial_asset, monthly_invest, annual_return, target):
        r = annual_return / 12
        months = 0
        asset = initial_asset
        history = [asset]
        while asset < target and months < 100 * 12:
            asset = asset * (1 + r) + monthly_invest
            history.append(asset)
            months += 1
        yearly_history = [history[i] for i in range(0, len(history), 12)]
        years = months / 12
        return years if asset >= target else None, yearly_history

    if st.button("開始計算達標時間", key="simulate_goal"):
        result_years, asset_growth = calculate_years_to_goal(initial_capital, monthly_invest, annual_return, target_asset)
        st.session_state["goal_result_years"] = result_years
        st.session_state["goal_asset_growth"] = asset_growth

    if "goal_result_years" in st.session_state and "goal_asset_growth" in st.session_state:
        if st.session_state["goal_result_years"] is None:
            st.error("在 100 年內無法達成目標資產，請調整參數。")
        else:
            st.success(f"預估約需 **{st.session_state['goal_result_years']:.1f} 年** 可達成目標資產。")
            years_to_plot = min(int(st.session_state["goal_result_years"]) + 1, len(st.session_state["goal_asset_growth"]))
            asset_growth = st.session_state["goal_asset_growth"][:years_to_plot]
            df_growth = pd.DataFrame({
                "年數": list(range(0, years_to_plot)),
                "資產總額": asset_growth
            })
            st.subheader("達成退休金前的資產累積走勢")
            st.line_chart(df_growth.set_index("年數"))
