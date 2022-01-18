#!/Users/zeidanlab/miniconda3/envs/neuroimg/bin/python

import argparse; from pathlib import Path
import numpy as np; import pandas as pd
import matplotlib.pyplot as plt; import seaborn as sns
from scipy import signal

def get_args():
    
    parser = argparse.ArgumentParser(description='input thermal stimulator recordings, outputs event timings for each heat plateau')
    parser.add_argument('path', type=Path, help='path to TCS temperature recording (csv file)')
    parser.add_argument('sub', type=str, help='subject ID (ex c000)')
    parser.add_argument('ses', type=int, help='scanning session (ex 1,2..)')
    parser.add_argument('task', type=str, help='manipulation-stimuli (ex pre48C)')
    parser.add_argument('--adjust_onsets', type=float, default=0, help='seconds to subtract from onset times')
    args = parser.parse_args()

    f_in = Path(args.path)
    assert f_in.is_file(), 'file does not exist'

    f_out = f'{f_in.parent}/sub-{args.sub}_ses-{args.ses}_task-{args.task}_events'
    return f_in, f_out+'.tsv', f_out+'.png', args.adjust_onsets

def get_data(csv, adjust_onsets):
    zones = [f'zone{i}' for i in range(5)]
    df = pd.read_csv(csv, names=['time (sec)', 'step', 'stim'] + zones, index_col=0)
    df = df.loc[df.stim == 'STIMULATE', zones]
    return df.set_index(df.index - df.index[0] - adjust_onsets)

def calc_deriv(df):
    mask = (df.max()-df.min()) > 10 # minimum Δ°C
    active = df[mask.index[mask]].mean(axis=1)
    deriv = active.diff(periods=5).diff(periods=5)

    return active, deriv

def calc_evs(active, deriv):

    ru_n, _ = signal.find_peaks(deriv, height=2)
    stim_rd, _ = signal.find_peaks(-deriv, height=2)

    # adjust
    ru = ru_n[::2] - 6
    rd = stim_rd[1::2] - 6
    assert ru.shape == rd.shape, 'error in calc_evs'

    index = np.concatenate([ru, rd])
    return active.iloc[index].sort_index()

def plot(df, active, deriv, evs, axs):

    active.plot(ax=axs[0], c='k', lw=.5)
    axs[0].plot(evs.index, evs.values, 'ro', ms=1)
    deriv.plot(ax=axs[1], c='k', lw=.5)

    # adjust plot
    for ax in axs: 
        sns.despine(ax=ax, bottom=True)
        ax.set_yticks([])
        
    axs[0].set_ylabel('°C')
    axs[0].axvline(x=0, color='r', linestyle=':', lw=.6)
    axs[1].set_ylabel('f″(x)')
    axs[1].set_xticks(df.index[::100])

def evs_to_bids(evs):
    return pd.DataFrame({
        'onset': evs.index[::2], 
        'duration': evs.index[1::2] - evs.index[::2]})



def main():
    f_in, f_out, png, adjust_onsets = get_args()
    df = get_data(f_in, adjust_onsets)
    active, deriv = calc_deriv(df)
    evs = calc_evs(active, deriv)

    fig, axs = plt.subplots(2, figsize=(30,2), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
    plot(df, active, deriv, evs, axs)

    evs = evs_to_bids(evs)
    evs.to_csv(f_out, sep='\t', index=False, float_format='%.3f')
    fig.savefig(png, dpi=300, facecolor='w')

if __name__ == '__main__': main()