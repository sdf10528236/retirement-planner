import numpy as np
import matplotlib.pyplot as plt

def simulate_investment(monthly_investment, annual_return_mean, annual_return_std, target_amount, initial_principal=0, years_limit=50, simulations=10000):
    months_limit = years_limit * 12  # 將年限轉換為月數
    monthly_return_mean = (1 + annual_return_mean) ** (1/12) - 1  # 將年化報酬率轉換為月化報酬率
    monthly_return_std = annual_return_std / np.sqrt(12)  # 將年化波動率轉換為月化波動率

    success_count = 0
    total_years_to_goal = []

    # 開始進行模擬
    for _ in range(simulations):
        total_amount = initial_principal  # 起始金額包含初始本金
        total_amount_history = []  # 記錄每月的總資產成長

        for month in range(1, months_limit + 1):
            # 每月投入金額
            total_amount += monthly_investment
            # 模擬這一個月的投資報酬率
            monthly_return = np.random.normal(monthly_return_mean, monthly_return_std)

            # 計算資產成長
            total_amount *= (1 + monthly_return)
            # 記錄每月的總資產
            total_amount_history.append(total_amount)
            # 檢查是否達到目標金額
            if total_amount >= target_amount:
                total_years_to_goal.append(month / 12)  # 記錄達成目標的時間（以年為單位）
                success_count += 1
                break

    
    # 計算結果
    success_rate = success_count / simulations
    average_years_to_goal = np.mean(total_years_to_goal) if total_years_to_goal else None

    return average_years_to_goal, success_rate

def retirement_simulation(
    target_amount,            # 初始資金
    withdraw_rate,       # 每年提領率
    inflation,           # 每年通膨率
    annual_return_mean,     # 預期每年報酬
    annual_return_std,          # 報酬波動率
    years,                # 退休後預計活幾年
    simulations         # 模擬次數
):
    # 儲存模擬結果
    all_trajectories = []
    ending_years = []
    success_count = 0
    final_assets = []
    avg_withdrawals = []
    yearly_withdrawals = np.zeros(years)  # 儲存每年總提領金額
    yearly_counts = np.zeros(years)       # 實際有提領的模擬次數

    for _ in range(simulations):
        assets = target_amount
        withdrawal = target_amount * withdraw_rate  # 初始提領金額
        trajectory = [target_amount]
        total_withdrawn = 0
        withdraw_count = 0
        for year in range(years):
            total_withdrawn += withdrawal
            withdraw_count += 1
            last_assets = assets
            annual_return = np.random.normal(annual_return_mean, annual_return_std)
            real_return = (1 + annual_return) / (1 + inflation) - 1
            assets = assets * (1 + real_return)
            
            # GK 提領法則
            if assets > last_assets:
                if year > 0:
                    withdrawal *= (1 + inflation)
                # 繁榮規則：資產大漲，提領額上調 10%
                if ((withdrawal / assets) - withdraw_rate) < withdraw_rate * (-0.2):
                    withdrawal *= 1.1
            else:
                # 如果資產虧損，提領金額不隨通膨調整
                # 保本規則：資產下跌，提領額下調 10%
                if ((withdrawal / assets) - withdraw_rate) > withdraw_rate * 0.2:
                    withdrawal *= 0.9

            # 記錄該年提領金額
            yearly_withdrawals[year] += withdrawal
            yearly_counts[year] += 1

            # 扣除提領金額
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
        # 期末資產統計
        for traj in all_trajectories:
            last_value = next((v for v in reversed(traj) if v > 0), 0)
            final_assets.append(last_value)

    max_asset = np.max(final_assets)
    min_asset = np.min(final_assets)
    avg_asset = np.mean(final_assets)
    median_asset = np.median(final_assets)

    # 平均每年提領金額
    average_withdrawals = yearly_withdrawals / yearly_counts

    # 成功率與平均年數
    overall_avg = np.mean(avg_withdrawals)
    success_rate = success_count / simulations * 100
    avg_years = np.mean(ending_years)

     # 結果輸出
    results = {
        "success_rate": success_rate,
        "avg_years": avg_years,
        "max_asset": max_asset,
        "min_asset": min_asset,
        "avg_asset": avg_asset,
        "median_asset": median_asset,
        "average_withdrawals": average_withdrawals,
        "overall_avg_withdrawal": overall_avg
    }
    return results

##### 參數修改地方 ##############################
#退休前參數
monthly_investment = 150000  # 每月投入金額
annual_return_mean = 0.08  # 年化平均報酬率（8%）
annual_return_std = 0.16  # 年化報酬波動率（16%）
target_amount = 46000000  # 目標金額（4000萬）
initial_principal = 4000000  # 初始本金（500萬）
years_limit = 50  # 最多模擬50年
simulations = 3000  # 模擬次數
 
#退休後參數
inflation=0.02 # 每年通膨
withdraw_rate=0.026 #提領率
years=200          # 退休後預計活幾年
##################################################

# 執行模擬
average_years, success_rate = simulate_investment(monthly_investment, annual_return_mean, annual_return_std, target_amount, initial_principal, years_limit, simulations)
results =retirement_simulation(target_amount,withdraw_rate,inflation,annual_return_mean,annual_return_std,years,simulations)

# 輸出結果
print(f"您所投入的標的,年化報酬率為{annual_return_mean*100:.0f}%,年化報酬波動率為{annual_return_std*100:.0f}%,模擬{simulations}次")
print("\n退休前:")
print(f"目前本金:{initial_principal/10000:.0f}萬,每月投入:{monthly_investment/10000:.0f}萬,目標金額:{target_amount/10000:.0f}萬,")
if average_years:
    print(f"平均達成目標金額需要的時間：{average_years:.2f} 年")
else:
    print("未能在模擬的時間範圍內達成目標。")
   
print(f"✅成功率：{success_rate:.2%}\n")
 
print("--------------------------------------------------------")
print("\n退休後:")
print(f"退休金:{target_amount/10000:.0f}萬,每年提領率:{withdraw_rate*100:.1f}%,退休後預計活:{years}年,")
average_withdrawals = results["average_withdrawals"]

print(f"✅ 成功率：{results['success_rate']:.1f}%")
print(f"📉 平均可撐年數：{results['avg_years']:.1f} 年")
#print(f"最大資產: NT$ {results['max_asset']:,.0f}")
#print(f"最小資產: NT$ {results['min_asset']:,.0f}")
print(f"平均遺產: NT$ {results['avg_asset']:,.0f}")
print(f"遺產中位數: NT$ {results['median_asset']:,.0f}")
print(f"💰 每年平均提領金額: NT$ {results['overall_avg_withdrawal']:,.0f}")

for year in range(years):
    if year%10 == 0:
        print(f"退休後第 {year+1} 年，平均每年可提領: NT$ {average_withdrawals[year]:,.0f}")