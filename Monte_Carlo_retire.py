import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

# 資產類型           | 年報酬率平均值 | 年波動率（標準差
# 美國股票（S\&P 500）| 約 10%   | 約 **15%–20%** |
# 全球股票（VT）      | 約 8%–9% | 約 **13%–16%** |
# 60/40 平衡型（股債）| 約 6%–7% | 約 **8%–10%**  |
# 美國投資級債券      | 約 3%–4% | 約 **4%–6%**   |
# 現金／定存          | 約 1%–2% | 接近 **0%**     |

# 模擬參數
initial_assets = 1200000  #初始資金
withdraw_rate = 0.04  #每年提領率
inflation = 0.00  #每年通膨率
expected_return = 0.08 #預期每年報酬
return_std = 0.15  #報酬波動率
years = 7 #退休後預計活幾年
simulations = 10000  #模擬次數


# 儲存模擬結果
all_trajectories = []
ending_years = []
success_count = 0
final_assets = []
avg_withdrawals = []
yearly_withdrawals = np.zeros(years)  # 儲存每年總提領金額
yearly_counts = np.zeros(years)       # 實際有提領的模擬次數

for _ in range(simulations):
    assets = initial_assets
    withdrawal = initial_assets * withdraw_rate #提領金額
    trajectory = [initial_assets]
    witjectory = [withdrawal]
    total_withdrawn = 0
    withdraw_count = 0

    for year in range(years):
        total_withdrawn += withdrawal
        withdraw_count += 1
        last_assets=assets
        annual_return = np.random.normal(expected_return, return_std)
        real_return = (1 + annual_return) / (1 + inflation) - 1
        assets = assets * (1 + real_return)
        
        # GK 提領法則
        #通膨規則（Inflation Rule）
        #1️⃣每年是否調整提領金額，視通膨而定：
        #如果前一年退休金是虧損的，今年的提領金額就不隨通膨進行調整；反之，前一年退休金有賺錢，今年的提領金額就隨通膨調整，但上限是6%。
        #2️⃣ 保本規則（Capital Preservation Rule）
        #若資產跌太多、低於原本預期區間，就自動調降提領金額：
        #在市場下跌時退休金的總價值會降低，若導致當前提領率比初始提領率超出20%時，就必須把當前提領率下調10%，以免退休金油盡燈枯。
        #3️⃣ 繁榮規則（Prosperity Rule）
        #如果退休金資產大漲超標，則適度提高提領額度，多花一點享受人生：
        #本質上和保本規則相反。在市場上漲退休金變多時，如果導致當前提領率比初始提領率低過20%時，就必須把當前提領率上調10%，以免退休金太多花不完。
        
        if assets > last_assets:
            if year == 0:
                withdrawal=withdrawal
            else:
                withdrawal *= (1 + inflation) 
            #在市場上漲退休金變多時，如果導致當前提領率比初始提領率低過20%時，就必須把當前提領率上調10%，以免退休金太多花不完。
            if ((withdrawal/assets)-withdraw_rate) < withdraw_rate*(-0.2):
                withdrawal=withdrawal*1.1
        else: 
            #如果前一年退休金是虧損的，今年的提領金額就不隨通膨進行調整
            #在市場下跌時退休金的總價值會降低，若導致當前提領率比初始提領率超出20%時，就必須把當前提領率下調10%，以免退休金油盡燈枯。
            if ((withdrawal/assets)-withdraw_rate) > withdraw_rate*0.2:
                withdrawal=withdrawal*0.9
   
        # 記錄該年提領金額
        yearly_withdrawals[year] += withdrawal
        yearly_counts[year] += 1

        assets=assets-withdrawal
        witjectory.append(withdrawal)
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

# 期末資產
for traj in all_trajectories:
    # 找出這條模擬中的最後非負資產值
    last_value = next((v for v in reversed(traj) if v > 0), 0)
    final_assets.append(last_value)

max_asset = np.max(final_assets)
min_asset = np.min(final_assets)
avg_asset = np.mean(final_assets)
median_asset = np.median(final_assets)

#👇 所有模擬跑完後，計算每年平均提領：
average_withdrawals = yearly_withdrawals / yearly_counts
#for year in range(years):
#    print(f"第 {year+1} 年 平均提領:NT$ {average_withdrawals[year]:,.0f}")


# ✅ 成功率與平均年數
overall_avg = np.mean(avg_withdrawals)
print(f"💰 每年平均提領金額:NT$ {overall_avg:,.0f}")
success_rate = success_count / simulations * 100
avg_years = np.mean(ending_years)



#print(ending_years[-10:])
print(f"✅ 成功率：{success_rate:.1f}%")
print(f"📉 平均可撐年數：{avg_years:.1f} 年")
print(f"最大資產:NT$ {max_asset:,.0f}")
print(f"最小資產:NT$ {min_asset:,.0f}")
print(f"平均資產:NT$ {avg_asset:,.0f}")
print(f"中位資產:NT$ {median_asset:,.0f}")

# --- 📈 繪圖 ---

# 1. 多條資產走勢圖
plt.figure(figsize=(12, 6))
for traj in all_trajectories:
    plt.plot(traj, color='blue', alpha=0.6)

plt.title(f"Retire\n Sucees Rate={success_rate:.1f}%, Average={avg_years:.1f}years")
plt.xlabel("years")
plt.ylabel("Value")
plt.gca().yaxis.set_major_formatter(ScalarFormatter(useMathText=False))
plt.ticklabel_format(style='plain', axis='y')  # 確保不使用科學記號
plt.grid(True)
plt.axhline(0, color='red', linestyle='--', alpha=0.6)
plt.tight_layout()
#plt.show()


'''# 4. 可撐年數直方圖
plt.figure(figsize=(10, 5))
plt.hist(ending_years, bins=range(0, years+1, 2), color='orange', edgecolor='black')
plt.title("模擬中可撐年數分布")
plt.xlabel("可撐年數")
plt.ylabel("模擬次數")
plt.grid(True)
plt.tight_layout()
plt.show() '''
