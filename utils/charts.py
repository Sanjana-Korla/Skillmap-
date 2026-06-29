import numpy as np 
import matplotlib.pyplot as plt 

def generate_comparison_chart(labels, user_values, market_values, title="Your Skills vs. Market Benchmark"): 
    if not labels: 
        return None 
    plt.style.use('dark_background') 
    x = np.arange(len(labels)) 
    width = 0.35 
    fig, ax = plt.subplots(figsize=(7, 3.5)) 
    
    # Side-by-side bar representations 
    rects1 = ax.bar(x - width/2, user_values, width, label='Your Level', color='#4CAF50') 
    rects2 = ax.bar(x + width/2, market_values, width, label='Market Target', color='#00E5FF', alpha=0.7) 
    ax.set_title(title, fontsize=12, fontweight='bold', pad=15) 
    ax.set_xticks(x) 
    ax.set_xticklabels(labels, rotation=15, ha='right', fontsize=9) 
    ax.set_ylabel('Proficiency Level (0-4)', fontsize=9) 
    ax.set_yticks([0, 1, 2, 3, 4]) 
    ax.set_yticklabels(['None', 'Beginner', 'Intermediate', 'Expert', 'Master'], fontsize=8) 
    ax.spines['top'].set_visible(False) 
    ax.spines['right'].set_visible(False) 
    ax.spines['left'].set_color('#333333') 
    ax.spines['bottom'].set_color('#333333') 
    ax.legend(loc='upper right', fontsize=8) 
    
    # Adjust spacing so rotated labels are not cut off at the bottom
    fig.subplots_adjust(bottom=0.25)
    
    plt.tight_layout() 
    return fig 

def generate_market_demand_chart(skills, scores): 
    if not skills: 
        return None 
    plt.style.use('dark_background') 
    fig, ax = plt.subplots(figsize=(6, 2.5)) 
    percentage_scores = [s * 100 for s in scores] 
    sorted_pairs = sorted(zip(skills, percentage_scores), key=lambda x: x[1]) 
    sorted_skills = [p[0] for p in sorted_pairs] 
    sorted_scores = [p[1] for p in sorted_pairs] 
    bars = ax.barh(sorted_skills, sorted_scores, color='#00E5FF', height=0.4) 
    ax.spines['top'].set_visible(False) 
    ax.spines['right'].set_visible(False) 
    ax.spines['bottom'].set_visible(False) 
    ax.spines['left'].set_color('#444444') 
    ax.xaxis.grid(True, linestyle='--', alpha=0.15, color='#666666') 
    ax.set_xlabel("Market Frequency (Percentage %)", color='#cccccc', fontsize=8) 
    ax.tick_params(axis='both', which='major', labelsize=8) 
    for bar in bars: 
        width = bar.get_width() 
        ax.text(width + 1.5, bar.get_y() + bar.get_height()/2, f'{int(width)}%', 
                va='center', ha='left', color='#ffffff', fontweight='bold', fontsize=8) 
    plt.tight_layout() 
    return fig