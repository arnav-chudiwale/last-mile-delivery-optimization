# Quick sanity checks — run in a REPL or add to your script
import numpy as np, pandas as pd

df = pd.read_csv('data/delivery_locations.csv')
lats = np.concatenate(([40.7128], df['latitude'].values))
longs = np.concatenate(([-74.0060], df['longitude'].values))

print("Lat range:", lats.min(), lats.max())
print("Long range:", longs.min(), longs.max())

dm = np.load('data/distance_matrix.npy')
i, j = np.unravel_index(np.argmax(dm), dm.shape)
print("Farthest pair:", (i, j), "distance_km:", dm[i, j])
print("Coords:", (lats[i], longs[i]), (lats[j], longs[j]))

print("Distance percentiles (non-zero):", np.percentile(dm[dm>0], [25, 50, 75, 90, 99]))