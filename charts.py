import numpy as np
import matplotlib.pyplot as plt
from common import STATE_SIZES, TIME_NAMES, FUNCTION_NAMES


def plot_relative_time(data, save_destination):
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
    # plt.show()

    plt.savefig(save_destination)


def plot_comparison_bar_chart(plot_data, save_destination):
    # data to plot
    n_groups = 8
    scilla_data, evm_data = plot_data

    # create plot
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.35
    opacity = 0.8

    rects1 = plt.bar(index, scilla_data, bar_width,
                     alpha=opacity,
                     color='#D7191C',
                     label='Scilla')

    rects2 = plt.bar(index + bar_width, evm_data, bar_width,
                     alpha=opacity,
                     color='#FDAE61',
                     label='EVM')

    plt.ylabel('Time (ms)')
    plt.title('Scilla/EVM execution times')
    ticks = ('ft-10', 'nft-10', 'auc-10', 'cfd-10',
             'ft-50', 'nft-50', 'auc-50', 'cfd-50')
    plt.xticks(index + bar_width/2, ticks)
    plt.legend()

    plt.tight_layout()

    plt.savefig(save_destination)

    # plt.show()


def plot_compare_sizes(plot_data, save_destination):
    # data to plot
    n_groups = 4
    scilla_data, evm_sol_data, evm_bytecode_data = plot_data

    # create plot
    fig, ax = plt.subplots()
    index = np.arange(n_groups)
    bar_width = 0.15
    opacity = 0.8

    rects1 = plt.bar(index, scilla_data, bar_width,
                     alpha=opacity,
                     color='#D7191C',
                     label='Scilla')

    rects2 = plt.bar(index + bar_width, evm_sol_data, bar_width,
                     alpha=opacity,
                     color='#FDAE61',
                     label='Solidity')

    rects3 = plt.bar(index + bar_width*2, evm_bytecode_data, bar_width,
                     alpha=opacity,
                     color='#ABDDA4',
                     label='EVM bytecode')

    plt.ylabel('Size (bytes)')
    plt.title('Code size comparison')
    ticks = ('ft', 'nft', 'auc', 'cfd')
    plt.xticks(index + bar_width, ticks)
    plt.legend()

    plt.tight_layout()
    # plt.show()
    plt.savefig(save_destination)


if __name__ == '__main__':
    plot_compare_sizes([[4871, 12302, 5010, 4122], [
                       6696, 6873, 4485, 1305], [4214, 5252, 2708, 1606]])
