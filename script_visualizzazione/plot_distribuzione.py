import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

# Data
categories = ['word order', 'simple clauses', 'morphology']
avg_coverage = [0.26, 0.36, 0.40]
std_coverage = [0.18, 0.27, 0.29]
perc_25 = [0.11, 0.03, 0.01]
perc_75 = [0.28, 0.44, 0.26]
n_langs = [3001, 2967, 2778]
n_params = [77, 75, 41]

# X range
x = np.linspace(0, 1, 1000)

# Plot
plt.figure(figsize=(10, 6))
colors = ['skyblue', 'salmon', 'lightgreen']

for i, (avg, std, p25, p75, label) in enumerate(zip(avg_coverage, std_coverage, perc_25, perc_75, categories)):
    y = norm.pdf(x, avg, std)
    # y = norm.pdf(x, avg, std) * n_langs[i]
    plt.plot(x, y, label=label, color=colors[i])

    # Shade between 25th and 75th percentiles
    x_fill = np.linspace(p25, p75, 500)
    y_fill = norm.pdf(x_fill, avg, std)
    # y_fill = norm.pdf(x_fill, avg, std) * n_langs[i]
    plt.fill_between(x_fill, y_fill, alpha=0.3, color=colors[i], label=f'{label} IQR')

plt.title('Estimated Coverage Distributions with IQR Shaded')
plt.xlabel('Coverage (proportion)')
plt.ylabel('Probability Density')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()

plt.savefig("prova.png")


# X range for coverage values (proportions between 0 and 1)
# x = np.linspace(0, 1, 1000)
x = np.linspace(0, max(n_params), 1000)
colors = ['skyblue', 'salmon', 'lightgreen']

# Plot setup
plt.figure(figsize=(12, 6))

for i, (avg, std, p25, p75, label) in enumerate(zip(avg_coverage, std_coverage, perc_25, perc_75, categories)):
    avg = avg * n_params[i]
    std = std * n_params[i]
    p25 = p25 * n_params[i]
    p75 = p75 * n_params[i]

    # Raw PDF
    pdf = norm.pdf(x, avg, std)

    # Area under curve in [0, 1]
    area = np.trapz(pdf, x)

    # Scale PDF to make area = number of languages
    scale_factor = n_langs[i] / area
    y = pdf * scale_factor

    # Plot scaled bell curve
    plt.plot(x, y, label=label, color=colors[i])

    # Shade IQR (25th–75th percentile)
    x_fill = np.linspace(p25, p75, 500)
    y_fill = norm.pdf(x_fill, avg, std) * scale_factor
    plt.fill_between(x_fill, y_fill, alpha=0.3, color=colors[i], label=f'{label} IQR')

    # Add text annotation above curve peak
    peak_x = avg
    peak_y = norm.pdf(peak_x, avg, std) * scale_factor
    # plt.text(peak_x, peak_y + max(n_langs)/40, f'n_langs={n_langs[i]}\nn_params={n_params[i]}',
    #          ha='center', fontsize=9)

# Final plot settings
plt.title('Coverage Distributions by Linguistic Category\n(Scaled by Number of Languages)')
plt.xlabel('Coverage (proportion)')
plt.ylabel('Estimated Number of Languages')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig("prova2.png")
