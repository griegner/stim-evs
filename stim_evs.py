import numpy as np
from numpy import diff
from scipy.signal import find_peaks
import glob
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (10, 4)

def read_data(file):
    # load column 0
    ys = np.loadtxt(fname=file, usecols=0)
    xs = np.arange(len(ys))
    # data sampled at 1000Hz: convert to seconds
    xs = np.divide(xs, 1000)
    # remove first 10 seconds
    xs = xs[10000:]
    ys = ys[10000:]
    return xs, ys


def smooth(data, window):
    # moving average smoothing
    cs = np.cumsum(np.insert(data, 0, 0))
    return (cs[window:] - cs[:-window]) / window


def second_dydx(xs, ys, window=500):
    # first derivative
    dydx = diff(ys)/diff(xs)
    dydx = np.insert(dydx, 0, 0.)
    xs, dydx = smooth(xs, window), smooth(dydx, window)
    # second derivative
    dydx = diff(dydx)/diff(xs)
    dydx = np.insert(dydx, 0, 0.)
    xs, dydx = smooth(xs, window), smooth(dydx, window)
    return xs, dydx


def events(xs, ys):
    xs, dydx = second_dydx(xs, ys)
    # plt.plot(xs, dydx, 'k', lw=.5)
    peaks_pos, _ = find_peaks(dydx, height=5, distance=1000)
    peaks_neg, _ = find_peaks(-dydx, height=5, distance=1000)
    # adjust peaks visually
    ru = xs[peaks_pos[0]-100]
    stim = xs[peaks_neg[0]+100]
    rd = xs[peaks_neg[1]-150]
    n = xs[peaks_pos[1]+75]
    return ru, stim, rd, n


def find_nearest(array, *args):
    return [np.abs(array-arg).argmin() for arg in args]


def main():
    files = sorted(glob.glob('acq_data/*txt'))
    for file in files:
        print(file)
        open('acq_evs/' + file[-11:], 'w').close()  # clear file_out
        xs, ys = read_data(file)
        xs_raw, ys_raw = np.array_split(xs, 10), np.array_split(ys, 10)
        xs, ys = smooth(xs, window=250), smooth(ys, window=250)
        xs, ys = np.array_split(xs, 10), np.array_split(ys, 10)
        for i in range(len(xs)):
            ru, stim, rd, n = events(xs[i], ys[i])
            idx_list = find_nearest(xs[i], ru, stim, rd, n)
            # plot
            plt.plot(xs_raw[i], ys_raw[i], 'k', lw=.01)
            plt.plot(xs[i][idx_list], ys[i][idx_list], 'ro', ms=3)
            plt.plot(xs[i], ys[i], 'k', lw=.5)
            # add text
            heat = 'heat' + str(i + 1).zfill(2)
            plt.title(heat, size='medium', loc="left")
            plt.suptitle(file[-11:], size='medium')
            plt.xlabel('time (sec)')
            plt.ylabel('temp (°C)')
            # frame rate
            plt.pause(.1)
            plt.clf()
            # save stim events as txt file
            with open('acq_evs/' + file[-11:], 'a') as file_out:
                heat = 'heat' + str(i+1).zfill(2)
                print('%s %f %f %f %f' % (heat, ru, stim, rd, n), file=file_out)


main()
