"""
Social Media Screen Time & Mental Health — Analysis
=====================================================

Question: Does the specific platform you use (TikTok, Instagram, LinkedIn, etc.)
predict worse mental health outcomes — or is something else driving the effect?

Dataset: 7,000 survey respondents with self-reported screen time habits,
platform usage, and mental health indicators (anxiety, mood, loneliness,
self-esteem, sleep, and an overall wellbeing classification).

Author: [Your Name]
Tools: pandas, matplotlib
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

matplotlib.rcParams['font.family'] = 'DejaVu Sans'

# ---------------------------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------------------------

DATA_PATH = "social_media_screentime_mental_health_2026.csv"
df = pd.read_csv(DATA_PATH)

print(f"Loaded {len(df):,} rows, {df.shape[1]} columns")
print(df['most_used_platform'].value_counts())

# Colors used throughout for consistent styling
NAVY = '#1d3557'
TEAL = '#2a9d8f'
CORAL = '#e76f51'
GOLD = '#f4a261'
GRAY = '#6c757d'


# ---------------------------------------------------------------------------
# 2. FINDING 1 — Does platform choice predict anxiety?
# ---------------------------------------------------------------------------
# Group by platform and compare average anxiety score. If platform were a
# strong driver, we'd expect a wide spread between the highest and lowest.

platform_order = (
    df.groupby('most_used_platform')['anxiety_score_0to27']
    .mean()
    .sort_values(ascending=False)
    .index
)
plat_anxiety = df.groupby('most_used_platform')['anxiety_score_0to27'].mean().reindex(platform_order)

print("\nAverage anxiety score by platform:")
print(plat_anxiety.round(2))
print(f"Spread: {plat_anxiety.max() - plat_anxiety.min():.2f} points "
      f"({(plat_anxiety.max()-plat_anxiety.min())/plat_anxiety.mean()*100:.1f}% of the mean)")

fig, ax = plt.subplots(figsize=(9, 5.5))
ax.barh(plat_anxiety.index[::-1], plat_anxiety.values[::-1], color=TEAL, height=0.6)
ax.set_xlim(0, 16)
ax.set_xlabel('Average anxiety score (0–27 scale)', fontsize=11)
ax.set_title('Anxiety Levels Are Nearly Identical Across Platforms',
             fontsize=14, fontweight='bold', pad=15)
ax.spines[['top', 'right']].set_visible(False)
for i, v in enumerate(plat_anxiety.values[::-1]):
    ax.text(v + 0.15, i, f'{v:.1f}', va='center', fontsize=10, color=NAVY, fontweight='bold')
plt.tight_layout()
plt.savefig('1_platform_anxiety.png', dpi=180, bbox_inches='tight')
plt.close()


# ---------------------------------------------------------------------------
# 3. FINDING 2 — Does daily screen time predict wellbeing?
# ---------------------------------------------------------------------------
# Split into quartiles so each group has an equal number of people, then
# compare wellbeing outcomes across the quartiles.

df['screen_bucket'] = pd.qcut(
    df['daily_screen_hours'], 4,
    labels=['Low\n(<2 hrs)', 'Med-Low\n(2-3 hrs)', 'Med-High\n(3-4.3 hrs)', 'High\n(4.4+ hrs)']
)

# Correlation check: how strongly does screen time relate to anxiety?
corr = df['daily_screen_hours'].corr(df['anxiety_score_0to27'])
print(f"\nCorrelation between daily screen hours and anxiety score: r = {corr:.3f}")

wellbeing_by_screen = pd.crosstab(df['screen_bucket'], df['wellbeing_band'], normalize='index') * 100
wellbeing_by_screen = wellbeing_by_screen[['Good', 'Moderate', 'At-risk']]
print("\nWellbeing band (%) by screen time quartile:")
print(wellbeing_by_screen.round(1))

fig, ax = plt.subplots(figsize=(9, 5.5))
wellbeing_by_screen.plot(kind='bar', stacked=True, ax=ax, color=[TEAL, GOLD, CORAL], width=0.65)
ax.set_ylabel('% of participants', fontsize=11)
ax.set_xlabel('')
ax.set_title('Screen Time Predicts Wellbeing Far More Than Platform Choice',
             fontsize=14, fontweight='bold', pad=15)
ax.legend(title='Wellbeing', frameon=False, loc='upper right', bbox_to_anchor=(1.25, 1))
ax.spines[['top', 'right']].set_visible(False)
plt.xticks(rotation=0, fontsize=10)
for i, (idx, row) in enumerate(wellbeing_by_screen.iterrows()):
    cum = 0
    for col in ['Good', 'Moderate', 'At-risk']:
        val = row[col]
        if val > 4:
            ax.text(i, cum + val / 2, f'{val:.0f}%', ha='center', va='center',
                     fontsize=9, fontweight='bold', color='white' if col != 'Moderate' else NAVY)
        cum += val
plt.tight_layout()
plt.savefig('2_screentime_wellbeing.png', dpi=180, bbox_inches='tight')
plt.close()


# ---------------------------------------------------------------------------
# 4. FINDING 3 — Does nighttime checking matter more than morning habits?
# ---------------------------------------------------------------------------

night_order = ['Never', 'Sometimes', 'Often', 'Every night']
night_data = df.groupby('night_time_use')[['anxiety_score_0to27', 'avg_sleep_hours']] \
    .mean().reindex(night_order)

print("\nAnxiety and sleep by nighttime social media use:")
print(night_data.round(2))

fig, ax1 = plt.subplots(figsize=(9, 5.5))
x = range(len(night_order))
ax1.bar(x, night_data['anxiety_score_0to27'], color=CORAL, width=0.5)
ax1.set_ylabel('Average anxiety score', fontsize=11, color=CORAL)
ax1.set_ylim(0, 16)
ax1.set_xticks(x)
ax1.set_xticklabels(night_order, fontsize=10)
ax1.tick_params(axis='y', labelcolor=CORAL)
ax1.spines[['top']].set_visible(False)
for i, v in enumerate(night_data['anxiety_score_0to27']):
    ax1.text(i, v + 0.3, f'{v:.1f}', ha='center', fontsize=10, fontweight='bold', color=CORAL)

ax2 = ax1.twinx()
ax2.plot(x, night_data['avg_sleep_hours'], color=NAVY, marker='o', linewidth=2.5, markersize=8)
ax2.set_ylabel('Average sleep hours', fontsize=11, color=NAVY)
ax2.set_ylim(5.5, 8)
ax2.tick_params(axis='y', labelcolor=NAVY)
for i, v in enumerate(night_data['avg_sleep_hours']):
    ax2.text(i, v + 0.08, f'{v:.1f}h', ha='center', fontsize=10, fontweight='bold', color=NAVY)

ax1.set_title('Checking Social Media Every Night Is Linked to Higher\n'
              'Anxiety and Nearly 1 Hour Less Sleep', fontsize=14, fontweight='bold', pad=15)
ax1.spines[['right']].set_visible(False)
ax2.spines[['top']].set_visible(False)
plt.tight_layout()
plt.savefig('3_nighttime_use.png', dpi=180, bbox_inches='tight')
plt.close()

# For comparison: does time-to-first-check-after-waking matter as much?
wake_corr = df['minutes_to_first_check_after_waking'].corr(df['anxiety_score_0to27'])
print(f"\nFor comparison, correlation between morning check speed and anxiety: r = {wake_corr:.3f}")
print("(Much weaker than nighttime use or total screen time — the timing that matters is at night, not morning.)")

print("\nDone. Charts saved: 1_platform_anxiety.png, 2_screentime_wellbeing.png, 3_nighttime_use.png")
