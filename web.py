import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

import pandas as pd

# --- 模擬投資累積 ---
def simulate_investment(monthly_investment, annual_return_mean, annual_return_std, target_amount, initial_principal=0, years_limit=50, simulations=10000):
    months_limit = years_limit * 12
    monthly_return_mean = (1 + annual_return_mean) ** (1/12) - 1
    monthly_return_std = annual_return_std / np.sqrt(12)
    success_count = 0
    total_years_to_goal = []

    for _ in range(simulations):
        total_amount = initial_principal
        for month in range(1, months_limit + 1):
            total_amount += monthly_investment
            monthly_return = np.random.normal(monthly_return_mean, monthly_return_std)
            total_amount *= (1 + monthly_return)
            if total_amount >= target_amount:
                total_years_to_goal.append(month / 12)
                success_count += 1
                break

    success_rate = success_count / simulations
    average_years_to_goal = np.mean(total_years_to_goal) if total_years_to_goal else None
    return average_years_to_goal, success_rate

# --- 模擬退休提領 ---
def retirement_simulation(target_amount, withdraw_rate, inflation, annual_return_mean, annual_return_std, years, simulations):
    all_trajectories = []
    ending_years = []
    success_count = 0
    final_assets = []
    avg_withdrawals = []
    yearly_withdrawals = np.zeros(years)
    yearly_counts = np.zeros(years)

    for _ in range(simulations):
        assets = target_amount
        withdrawal = target_amount * withdraw_rate
        trajectory = [target_amount]
        total_withdrawn = 0
        withdraw_count = 0
        for year in range(years):
            total_withdrawn += withdrawal
            withdraw_count += 1
            last_assets = assets
            annual_return = np.random.normal(annual_return_mean, annual_return_std)
            real_return = (1 + annual_return) / (1 + inflation) - 1
            assets *= (1 + real_return)

            if assets > last_assets:
                if year > 0:
                    withdrawal *= (1 + inflation)
                if ((withdrawal / assets) - withdraw_rate) < withdraw_rate * (-0.2):
                    withdrawal *= 1.1
            else:
                if ((withdrawal / assets) - withdraw_rate) > withdraw_rate * 0.2:
                    withdrawal *= 0.9

            yearly_withdrawals[year] += withdrawal
            yearly_counts[year] += 1

            assets -= withdrawal
            trajectory.append(assets)

            if assets <= 0:
                ending_years.append(year + 1)
                break
        else:
            ending_years.append(years)
            success_count += 1

        all_trajectories.append(trajectory)
        if withdraw_count > 0:
            avg_withdrawals.append(total_withdrawn / withdraw_count)
        last_value = next((v for v in reversed(trajectory) if v > 0), 0)
        final_assets.append(last_value)

    max_asset = np.max(final_assets)
    min_asset = np.min(final_assets)
    avg_asset = np.mean(final_assets)
    median_asset = np.median(final_assets)
    average_withdrawals = yearly_withdrawals / yearly_counts
    overall_avg = np.mean(avg_withdrawals)
    success_rate = success_count / simulations * 100
    avg_years = np.mean(ending_years)

    return {
        "success_rate": success_rate,
        "avg_years": avg_years,
        "max_asset": max_asset,
        "min_asset": min_asset,
        "avg_asset": avg_asset,
        "median_asset": median_asset,
        "average_withdrawals": average_withdrawals,
        "overall_avg_withdrawal": overall_avg
    }

# --- Streamlit 介面 ---
st.title("💰 退休金模擬器 (蒙地卡羅)")

st.header("退休前模擬設定")
monthly_investment = st.slider("每月投入金額 (萬元)", 0, 50, 10) * 10000
initial_principal = st.slider("目前本金 (萬元)", 0, 2000, 400) * 10000
target_amount = st.slider("目標退休金 (萬元)", 1000, 8000, 4000) * 10000
years_limit = st.slider("最多模擬幾年", 10, 60, 50)
annual_return_mean = st.slider("年化報酬率 %", 0, 15, 8) / 100
annual_return_std = st.slider("報酬波動率 %", 0, 30, 16) / 100
simulations = st.slider("模擬次數", 500, 10000, 1000)

st.header("退休後模擬設定")
withdraw_rate = st.slider("每年提領率 %", 1, 10, 3) / 100
inflation = st.slider("每年通膨率 %", 0, 5, 2) / 100
years = st.slider("退休後年數", 10, 100, 80)

# 建立一個空的 line chart
chart = st.line_chart()



if st.button("開始模擬"):
    avg_years, invest_success = simulate_investment(
        monthly_investment, annual_return_mean, annual_return_std,
        target_amount, initial_principal, years_limit, simulations
    )

    results = retirement_simulation(
        target_amount, withdraw_rate, inflation,
        annual_return_mean, annual_return_std,
        years, simulations
    )

    st.subheader("退休前結果")
    if avg_years:
        st.write(f"🎯 達成目標所需平均年數：{avg_years:.2f} 年")
    else:
        st.warning("未在模擬期間內達成退休金目標")
    st.write(f"✅ 達成成功率：{invest_success:.2%}")

    st.subheader("退休後結果")
    st.write(f"✅ 成功率：{results['success_rate']:.1f}%")
    st.write(f"📉 平均可撐年數：{results['avg_years']:.1f}")
    st.write(f"💰 每年平均提領金額：NT$ {results['overall_avg_withdrawal']:,.0f}")
    st.write(f"📦 平均遺產：NT$ {results['avg_asset']:,.0f}（中位數：{results['median_asset']:,.0f}）")

    st.markdown("### 📅 每10年平均提領：")
    for year in range(0, years, 10):
        st.write(f"第 {year+1} 年：NT$ {results['average_withdrawals'][year]:,.0f}")

    fig, ax = plt.subplots()
    ax.hist(results["average_withdrawals"], bins=30, color='skyblue', edgecolor='black')
    ax.set_title("模擬中每年平均提領分布")
    st.pyplot(fig)


