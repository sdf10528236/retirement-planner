import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import math

st.set_page_config(page_title="退休規劃", layout="centered")

st.title("GK 動態提領策略（Guyton-Klinger Dynamic Withdrawal）")

st.markdown("""
GK 動態提領是一種退休金提領策略，根據市場表現和通膨，每年調整提領金額，讓退休金既安全又能維持生活品質。  
此策略由財務規劃師 **Jonathan Guyton** 與 **William Klinger** 於 2006 年提出。  
""")

# 🎬 影片放在論文連結上方
st.markdown("## 🎬 清流君GK動態提領影片")
st.video("https://www.youtube.com/watch?v=nNzokVsPyQY&t=887s")

st.markdown("## 📄 論文連結")
st.markdown("""
- [Decision Rules and Maximum Initial Withdrawal Rates (PDF)](https://www.financialplanningassociation.org/sites/default/files/2021-10/MAR06%20JFP%20Guyton%20PDF.pdf)
""")


st.markdown("## 📊 GK 三大法則與詳細範例")

# 通膨規則
with st.expander("1️⃣ 通膨規則（Inflation Rule）"):
    st.write("""
    **原則：** 每年是否調整提領金額，依通膨狀況決定：
    - 去年退休金有賺錢 → 提領金額隨通膨調整，但上限 6%  
    - 去年退休金虧損 → 提領金額不隨通膨調整

    **詳細範例：**
    1. 去年退休金總資產：10,000,000 元  
    2. 去年投資賺錢，通膨率：3%  
    3. 假設前一年提領金額為 400,000
    4. 計算今年提領金額：  
       今年提領 = 400,000 × (1 + 3%) = 412,000 元  
    5. 如果去年投資虧損，則今年提領 = 400,000 元（不調整）
    """)

# 保本規則
with st.expander("2️⃣ 保本規則（Capital Preservation Rule）"):
    st.write("""
    **原則：** 在市場下跌時退休金的總價值會降低，若導致當前提領率比初始提領率超出20%時，就必須把當前提領率下調10%，以免退休金油盡燈枯。

    **詳細範例：**
    - 初始資產：10,000,000 元  
    - 初始提領率：4% → 每年提領 400,000 元
    - 假設市場下跌，資產剩下 7,000,000 元  
      - 新提領率 = 400,000 ÷ 7,000,000 ≈ 5.71%  
      - 超過初始提領率 4% 的 20% → 4% × 1.2 = 4.8%  
      - 5.71% > 4.8%，需下調提領額度 10%  
      - 調整後提領金額 = 400,000 × (1 - 10%) = 360,000 元
    - 結果：資產安全，避免提領過高耗盡退休金
    """)

# 繁榮規則
with st.expander("3️⃣ 繁榮規則（Prosperity Rule）"):
    st.write("""
    **原則：** 在市場上漲退休金變多時，如果導致當前提領率比初始提領率低過20%時，就必須把當前提領率上調10%，以免退休金太多花不完。

    **詳細範例：**
    - 初始資產：10,000,000 元  
    - 初始提領率：4% → 每年提領 400,000 元
    - 通膨率：3%
    - 假設市場上漲，資產增加到 13,000,000 元  
      - 通膨調整提領額：400,000 × (1 + 3%) = 412,000 元
      - 新提領率 = 412,000 ÷ 13,00,000 ≈ 3.17%  
      - 低於初始提領率 4% 的 20% → 4% × 0.8 = 3.2%  
      - 3.17% < 3.2%，需上調提領額度 10%  
      - 調整後提領金額 = 412,000 × (1 + 10%) = 453,200 元
    - 結果：退休金花得更多，享受人生，同時資產仍安全
    """)




# 在 GK 法則內容之後
st.markdown("## 🧮 退休試算工具")
st.markdown("以下三個表單可用來試算不同退休情境。")
st.markdown("---")

st.title("我要多少錢才能退休?")



# 投資標的資料
portfolio_data = {
    "VT (全市場 ETF)": {"mean_return": 8.05, "std_dev": 15.76},
    "0050 (台灣50)": {"mean_return": 8.5, "std_dev": 15.5},
    "60/40 股債配": {"mean_return": 6.0, "std_dev": 8.5},
    "0056 (高股息)": {"mean_return": 7.5, "std_dev": 12.5},
}

#提領策略
strategy_data = {
    "GK動態提領": {"value": "GK"},
    "每年固定提領": {"value": "fix"},
}

retire_need=1200

# 退休後模擬輸入
with st.expander("退休後資產需求模擬", expanded=True):
    monthly_expense = st.number_input("退休後預計每月花費（萬元）", min_value=0, value=4, key="monthly_expense")
    years_to_live = st.number_input("退休後預期存活年數", min_value=1, value=35, key="years_to_live")
    portfolio = st.selectbox("選擇投資標的", options=list(portfolio_data.keys()), key="portfolio")
    mean_return = portfolio_data[portfolio]["mean_return"]
    std_dev = portfolio_data[portfolio]["std_dev"]
    # VT 說明
    st.info(
        """
        VT 是什麼?
        **VT (Vanguard Total World Stock ETF)**  
        - 全球股票 ETF，投資超過 9,000 家公司，涵蓋約 50 個國家。  
        - 以市值加權方式投資大型、中型及小型公司（市值型 ETF）。  
        - 高度分散風險，適合長期退休投資。  
        - 慢活夫妻介紹影片:(https://www.youtube.com/watch?v=_vcMqpM24OM)
        - 官方資訊請參考：[Vanguard VT ETF 官方網站](https://investor.vanguard.com/etf/profile/VT)
        """
    )
    # 鎖死數值
    st.number_input("年平均報酬率（%）", min_value=0.0, max_value=15.0, value=mean_return, key="mean_return", disabled=True)
    st.number_input("年報酬率波動度（標準差%）", min_value=0.0, max_value=30.0, value=std_dev, key="std_dev", disabled=True)
    inflation = st.number_input("年通膨率（%）", min_value=0.0, max_value=10.0, value=3.0, key="inflation")
    simulations = 10000 #模擬次數
    withdraw_strategy = st.selectbox("提領策略 (提領策略會影響退休所需金額)", options=list(strategy_data.keys()))
    target_success_rate = st.slider("目標成功率(%)", 80, 100, 95, key="target_success_rate") / 100

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
                real_return = (1 + r)  - 1
                last_asset=asset

                if strategy_data[withdraw_strategy]["value"] == "fix":
                    asset = asset * (1 + real_return) - annual_expense
                    annual_expense *= (1 + inflation/100)
                elif strategy_data[withdraw_strategy]["value"] == "GK":
                    asset = asset * (1 + real_return)
                    if asset > last_asset:
                        if year != 0:
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
        tolerance = 5
        result_asset = high
        with st.spinner("模擬中，請稍候..."):
            while high - low > tolerance:
                mid = (low + high) / 2
                rate, _ = monte_carlo_sim(mid)
                if rate > target_success_rate:
                    result_asset = mid
                    high = mid
                else:
                    low = mid
            final_success, final_assets = monte_carlo_sim(result_asset)
        #print(final_assets)
        st.session_state["retire_result_asset"] = result_asset
        st.session_state["retire_final_assets"] = final_assets
        st.session_state["retire_years_to_live"] = years_to_live
        
    if "retire_result_asset" in st.session_state:
        st.success(f"要達到 {target_success_rate*100:.1f}% 成功率，初始資產至少要：**{st.session_state['retire_result_asset']:,.0f} 萬元**")
        retire_need=int(math.ceil(st.session_state['retire_result_asset'])) #給定期定額達標時間估算，提領模擬預估表單用
        #percentiles = np.percentile(st.session_state["retire_final_assets"], [25, 50, 75], axis=0)
        years = list(range(1, st.session_state["retire_years_to_live"] + 1))
        # 取出最終資產
        final_assets = st.session_state["retire_final_assets"][:, -1]

        # ====== 找出 25%、50%、75% 的完整走勢 ======
        percentiles = [25,50,75]
        paths = {}

        for p in percentiles:
            target_value = np.percentile(final_assets, p)  # 取最終資產的分位數
            closest_idx = np.argmin(np.abs(final_assets - target_value))  # 找最接近的模擬路徑
            paths[f"{p}%"] = st.session_state["retire_final_assets"][closest_idx]

        # 建立 DataFrame
        df = pd.DataFrame(paths, index=years)

        # Streamlit 顯示
        st.subheader("GK 動態提領模擬 - 資產走勢分布 (25%, 中位數, 75%)")
        st.line_chart(df)

        


###### 定期定額達標時間估算
st.markdown("---")
st.title("我要多久才能退休?")

with st.expander("我要多久才能退休? 定期定額達標所需時間估算", expanded=True):
    asset_options = {
        "VT（全市場 ETF）": 0.0805,
        "0050（台灣50）": 0.09,
        "SPY（S&P 500）": 0.105,
        "60/40 股債配": 0.065,
    }

    initial_capital = st.number_input("現在能投入的本金?（萬元）", min_value=0, value=100, key="initial_capital")
    monthly_invest = st.number_input("每月可以定期再投入多少錢?（萬元）", min_value=0.0, value=2.0, key="monthly_invest")
    target_asset = st.number_input("我預計要多少錢可以退休?（萬元）", min_value=1, value=retire_need, key="target_asset")
    selected_asset = st.selectbox("選擇投資標的", list(asset_options.keys()), key="selected_asset")
    annual_return = asset_options[selected_asset]
    st.markdown(f"📈 **{selected_asset} 長期年化報酬率：{annual_return * 100:.2f}%**")

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
            st.success(f"預估約需 **{st.session_state['goal_result_years']:.1f} 年** 可達成退休目標。")
            years_to_plot = min(int(st.session_state["goal_result_years"]) + 1, len(st.session_state["goal_asset_growth"]))
            asset_growth = st.session_state["goal_asset_growth"][:years_to_plot]
            df_growth = pd.DataFrame({
                "年數": list(range(0, years_to_plot)),
                "資產總額": asset_growth
            })
            st.subheader("達成退休金前的資產累積走勢")
            st.line_chart(df_growth.set_index("年數"))


#### 提領模擬預估

st.title("我退休後錢會不會花完?")
# ================================
# 📌 提領模擬預估
# ================================
with st.expander("提領模擬預估 (蒙地卡羅)", expanded=True):
    initial_assets = st.number_input("假設你已經退休了，可以投資的資額有多少?（萬元）", min_value=100, value=retire_need, step=100)

    # ✅ 改成輸入「每月提領多少萬」
    monthly_withdraw = st.number_input("退休後預計每月賣股票提領的金額（萬元）", min_value=0.5, value=4.0, step=0.5)
    annual_withdraw = monthly_withdraw * 12   # 轉成年提領金額
    #
    portfolio2 = st.selectbox("選擇投資標的", options=list(portfolio_data.keys()), key="portfolio2")
    mean_return2 = portfolio_data[portfolio2]["mean_return"]
    std_dev2 = portfolio_data[portfolio2]["std_dev"]
    # 鎖死數值顯示
    expected_return = st.number_input("年平均報酬率（%）", value=mean_return2, disabled=True, key="mean_return2")/100
    return_std = st.number_input("年報酬率波動度（標準差%）", value=std_dev2, disabled=True, key="std_dev2")/100
    #
    inflation = st.number_input("預估年通膨率 (%)", min_value=0.0, value=3.0) / 100
    years = st.number_input("預估退休後可以活幾年", min_value=1, max_value=100, value=35)
    simulations = 10000 #模擬次數
    withdraw_strategy = st.selectbox("提領策略", options=list(strategy_data.keys()))

    if st.button("開始模擬", key="withdraw_sim"):
        all_trajectories = []
        withdraw_trajectories = []
        ending_years = []
        success_count = 0
        final_assets = []
        avg_withdrawals = []
        total_withdrawn_list = []
        for _ in range(simulations):
            assets = initial_assets
            withdrawal = annual_withdraw 
            trajectory = [initial_assets]
            withdrawal_path = [withdrawal]
            total_withdrawn = 0
            withdraw_count = 0
            base_withdraw_rate = withdrawal / initial_assets  # 用來比較 GK 動態提領

            for year in range(years):
                withdraw_count += 1
                total_withdrawn += withdrawal

                # 投資報酬
                annual_return = np.random.normal(expected_return, return_std)
                assets = assets * (1 + annual_return)

                if strategy_data[withdraw_strategy]["value"] == "fix":
                    withdrawal *= (1 + inflation)
                elif strategy_data[withdraw_strategy]["value"] == "GK":
                    if assets > trajectory[-1]:  # 上漲
                        if year != 0:
                            withdrawal *= (1 + inflation)
                            if ((withdrawal / assets) - base_withdraw_rate) < base_withdraw_rate * (-0.2):
                                withdrawal *= 1.1
                    else:  # 市場下跌
                        if ((withdrawal / assets) - base_withdraw_rate) > base_withdraw_rate * 0.2:
                            withdrawal *= 0.9

                assets -= withdrawal
                trajectory.append(max(assets, 0))
                withdrawal_path.append(withdrawal)

                if assets <= 0:
                    ending_years.append(year + 1)
                    break
            else:
                ending_years.append(years)
                success_count += 1

            all_trajectories.append(trajectory)
            withdraw_trajectories.append(withdrawal_path)
            if withdraw_count > 0:
                avg_withdrawals.append(total_withdrawn / withdraw_count)

            final_assets.append(max(trajectory[-1], 0))
            total_withdrawn_list.append(total_withdrawn)
        success_rate = success_count / simulations * 100
        median_asset = np.median(final_assets)

        total_withdrawn_25 = np.percentile(total_withdrawn_list, 25)
        total_withdrawn_50 = np.percentile(total_withdrawn_list, 50)
        total_withdrawn_75 = np.percentile(total_withdrawn_list, 75)

        st.success(f"✅ 成功率：{success_rate:.1f}%")
        st.write(f"💰 每年平均提領金額：約 {np.mean(avg_withdrawals):,.0f} 萬元")
        st.write(f"🏦 中位期末資產：約 {median_asset:,.0f} 萬元")

        # 📊 找出 25%、50%、75% 的完整曲線
        percentiles = [25,50,75]
        paths_assets = {}
        paths_withdrawals = {}
        for p in percentiles:
            target_val = np.percentile(final_assets, p)
            idx = np.argmin(np.abs(np.array(final_assets) - target_val))
            paths_assets[f"{p}% 資產"] = all_trajectories[idx]
            paths_withdrawals[f"{p}% 提領"] = withdraw_trajectories[idx]

        years_range = list(range(len(max(all_trajectories, key=len))))

        # 📈 資產走勢圖
        df_assets = pd.DataFrame(paths_assets, index=years_range)
        st.subheader("📈 資產走勢情境 (25%, 中位數, 75%)")
        st.line_chart(df_assets)

        # 💰 提領走勢圖
        df_withdrawals = pd.DataFrame(paths_withdrawals, index=years_range)
        st.subheader("💰 提領走勢情境 (25%, 中位數, 75%)")
        st.line_chart(df_withdrawals)

        st.markdown("### 📊 退休期間「累計提領總金額」")

        st.write(f"🔴 25% 悲觀情境：約 **{total_withdrawn_25:,.0f} 萬元**")
        st.write(f"🟡 50% 中位數情境：約 **{total_withdrawn_50:,.0f} 萬元**")
        st.write(f"🟢 75% 樂觀情境：約 **{total_withdrawn_75:,.0f} 萬元**")
