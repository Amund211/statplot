from statplot.data_getters import DirTreeIsoJson

skydeath = "a937646bf11544c38dbf9ae4a65669a0"

store = DirTreeIsoJson("/home/amund/tmp")

files = store.find_files(skydeath)

data = {time: store.get_data(file) for time, file in files.items()}

import matplotlib.pyplot as plt

from asyncpixel.models import Player

dates = []
fkdrs = []
fks = []
fds = []

for date in data:
    if data[date] is None:
        continue
    dates.append(date)
    fkdrs.append(data[date].stats.bedwars.final_kills_per_kills)
    fks.append(data[date].stats.bedwars.final_kills)
    fds.append(data[date].stats.bedwars.final_deaths)

plt.plot_date(dates, fkdrs)
plt.plot_date(dates, fks)
plt.plot_date(dates, fds)
plt.show()
