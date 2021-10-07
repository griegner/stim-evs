#!/Users/zeidanlab/miniconda3/envs/neuroimg/bin/python

import argparse; from pathlib import Path
import numpy as np; import pandas as pd
import matplotlib.pyplot as plt; import seaborn as sns
from scipy import signal

def get_args():
    
    parser = argparse.ArgumentParser(description='input thermal stimulator recordings, outputs event timings for each heat plateau')
    parser.add_argument('path', type=Path, help='path to QST.lab temperature recording (csv file)')
    args = parser.parse_args()

    f_in = Path(args.path)
    assert f_in.is_file(), 'file does not exist'
    f_out = f'{f_in.parent}/{f_in.stem}_events'

    return f_in, f_out+'.csv', f_out+'.png'

def get_data(csv):
    return pd.read_csv(csv, usecols=[0,3,4,5,6,7], names=['time (sec)'] + [f'zone{i}' for i in range(5)], index_col=0)

def calc_events(df):
    mask = (df.max()-df.min()) > 10 # minimum Δ°C
    active = df[mask.index[mask]].mean(axis=1)
    deriv = active.diff().diff()

    ru_n, _ = signal.find_peaks(deriv, height=1)
    stim_rd, _ = signal.find_peaks(-deriv, height=1)

    # adjust
    ru = ru_n[::2] - 2
    stim = stim_rd[::2]
    rd = stim_rd[1::2] - 2
    n = ru_n[1::2]

    index = np.concatenate([ru, stim, rd, n])
    evs = active.iloc[index].sort_index()
    return active, deriv, evs

def plot(df, active, deriv, evs, axs):

    active.plot(ax=axs[0], c='k', lw=.5)
    axs[0].plot(evs.index, evs.values, 'ro', ms=2)
    deriv.plot(ax=axs[1], c='k', lw=.5)

    # adjust plot
    for ax in axs: 
        sns.despine(ax=ax, bottom=True)
        ax.set_yticks([])
        
    axs[0].set_ylabel('°C')
    axs[1].set_ylabel('f″(x)')
    axs[1].set_xticks(df.index[::100])


def main():
    f_in, f_out, png = get_args()
    df = get_data(f_in)
    active, deriv, evs = calc_events(df)

    fig, axs = plt.subplots(2, figsize=(30,2), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
    plot(df, active, deriv, evs, axs)

    evs.to_csv(f_out, columns=[])
    fig.savefig(png, dpi=300, facecolor='w')

if __name__ == '__main__': main()