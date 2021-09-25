import matplotlib.pyplot as plt

from statplot.data_getters import DirTreeIsoJson

skydeath = "a937646bf11544c38dbf9ae4a65669a0"

store = DirTreeIsoJson("/home/amund/tmp")

files = store.find_files(skydeath)

data = {time: store.get_data(file) for time, file in files.items()}
bw_stats = {
    time: player.stats.bedwars for time, player in data.items() if player is not None
}

dates = []
fkdr_list = []
fks_list = []
fds_list = []


def div(dividend, divisor):
    if dividend == 0:
        return 0
    elif divisor == 0:
        return float("inf")
    else:
        return dividend / divisor


for date, bedwars in bw_stats.items():
    dates.append(date)
    fks_list.append(bedwars.final_kills)
    fds_list.append(bedwars.final_deaths)
    fkdr_list.append(div(bedwars.final_kills, bedwars.final_deaths))

plt.plot_date(dates, fkdr_list)
plt.plot_date(dates, fks_list)
plt.plot_date(dates, fds_list)
plt.show()
