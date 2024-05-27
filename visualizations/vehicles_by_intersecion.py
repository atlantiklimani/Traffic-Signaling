import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('D:\\Desktop\\data.csv', delimiter=';')

grouped = df.groupby('Intersection place')['Total vehicles'].sum().sort_values()

fig, ax = plt.subplots(figsize=(10, 8))
grouped.plot(kind='barh', ax=ax, color='blue')
ax.set_xlabel('Total Vehicles')
ax.set_ylabel('Intersection')
ax.set_title('Total Vehicles by Intersection')

for i, v in enumerate(grouped):
    ax.text(v + 3, i, str(v), color='blue', va='center')

plt.tight_layout()
plt.show()
