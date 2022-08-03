## stim_evs
> script to create timing files for fMRI analysis: input thermal stimulator recordings (QST.lab), outputs event timings for each 'heat' plateau

[scipy function: find_peaks](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html) 

finds local maxima/minima of the second derivative temperature trace  
`*_events.tsv` outputs follow the [BIDs specification](https://bids-specification.readthedocs.io/en/stable/) for task events

![](ex-fig.png)

**to run**: `$ python stim-evs.py --help`
