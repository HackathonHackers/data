from __future__ import division #now division always returns a floating point number

import numpy as np
import pandas as pd
from scipy import stats


tts = '''your copy of the csv here'''
min_pval = 0.05;
#split_on = 'Did You Accept the Offer?'
#split_on = 'Degree Level'
split_on = 'Position Type'
if __name__ == '__main__':
    bals = pd.read_csv(tts)
    # Visualizing difference in total compensation by gender
    #bals['total'] = [float(str(r).translate(None, ',$')) for r in bals['Total First Year Annualized Renumeration(including Signon & Relocation)']]

    # Visualizing differences in whether someone negotiated or not by gender
    bals['total'] = [True if r == 'Yes' else False for r in bals['Did You Negotiate the Offer?']]
    #bals = bals[bals['Position Type'] == 'Full Time']
    types = bals[split_on].unique()

    for t in types:
        slice = bals[bals[split_on] == t]
        if len(slice) <= 1:
            continue;
        print 'Splitting on ' + str(t)
        grouped = slice.groupby('Sex')
        g = grouped['total'].agg({'mean': 'mean', 'std': 'std', 'count': 'count'})
        g = g[g['count'] > 1]
        ttest = pd.DataFrame(index= g.index, columns = g.index)
        df = pd.DataFrame(index= g.index, columns = g.index)
        pv = pd.DataFrame(index= g.index, columns = g.index)
        yn = pd.DataFrame(index= g.index, columns = g.index)

        for i, r in g.iterrows():
            sn1 = r['std']*r['std']/r['count'];
            for j, k in g.iterrows():
                sn2 = k['std']*k['std']/k['count']
                ttest.ix[i,j] = abs(r['mean'] - k['mean'])/np.sqrt(sn1+ sn2)
                df.ix[i,j] = (sn1 + sn2)*(sn1 + sn2)/(sn1*sn1/(r['count'] - 1) + sn2*sn2/(k['count']-1))
                pv.ix[i,j] = stats.t.sf(np.abs(ttest.ix[i,j]), df.ix[i,j])*2
                if pv.ix[i,j] < min_pval:
                    yn.ix[i,j] = True
                else:
                    yn.ix[i,j] = False

        print df
        print ttest
        print pv
        print yn
        print g



