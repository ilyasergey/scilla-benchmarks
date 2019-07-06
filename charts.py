import numpy as np
import matplotlib.pyplot as plt
from common import STATE_SIZES, TIME_NAMES, FUNCTION_NAMES


def plot_comparison_bar_chart(data):
    # data to plot
    n_groups = 4
    n_comparison = 3
    data1 = (90, 55, 40, 65)

    # create plot
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.15
    opacity = 1

    colors = ['#D7191C', '#FDAE61', '#ABDDA4', '#2B83BA']
    bars = []

    for comparison_index in range(n_comparison):
        distance = bar_width * comparison_index

        for color_index in range(len(colors)):
            inner_data = data[comparison_index][color_index]
            color = colors[color_index]
            kwargs = {
                'alpha': opacity,
                'color': color,
            }

            if color_index > 0:
                bottom = np.array(data[comparison_index][0])
                for i in range(1, color_index):
                    bottom += np.array(data[comparison_index][i])
                bottom = bottom.tolist()
                kwargs['bottom'] = bottom

            bar = plt.bar(index + distance, inner_data, bar_width,
                          **kwargs)
            bars.append(bar)

    plt.ylabel('Time (ms)')
    plt.title('Relative time breakdown')
    plt.xticks(index + bar_width, FUNCTION_NAMES)
    plt.legend((bars[0][0], bars[1][0], bars[2][0], bars[3][0]),
               TIME_NAMES)

    plt.tight_layout()
    plt.show()


def plot_stacked_bar_chart():
    N = 5
    menMeans = (20, 35, 30, 35, 27)
    womenMeans = (25, 32, 34, 20, 25)
    ind = np.arange(N)    # the x locations for the groups
    width = 0.35       # the width of the bars: can also be len(x) sequence

    p1 = plt.bar(ind, menMeans, width)
    p2 = plt.bar(ind, womenMeans, width,
                 bottom=menMeans)

    plt.ylabel('Scores')
    plt.title('Scores by group and gender')
    plt.xticks(ind, ('G1', 'G2', 'G3', 'G4', 'G5'))
    plt.yticks(np.arange(0, 81, 10))
    plt.legend((p1[0], p2[0]), ('Men', 'Women'))

    plt.show()


if __name__ == '__main__':
    plot_stacked_bar_chart()
