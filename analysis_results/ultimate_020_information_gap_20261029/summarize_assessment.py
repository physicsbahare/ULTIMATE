"""Summarize only new saved outputs; does not simulate or fit anything."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent
SEED=20261029

def ci(v):
    v=np.asarray(v,float);r=np.random.default_rng(SEED)
    boot=v[r.integers(0,len(v),(5000,len(v)))].mean(axis=1)
    return np.quantile(boot,[.025,.975])

def main():
    # Preserve execution bytes; clarify source sampling versus integration grid.
    original=O/'operator_checks_execution_original.csv'
    if not original.exists():
        (O/'psf_definition_and_operator_checks.csv').rename(original)
    op=pd.read_csv(original).rename(columns={'native_pixel_arcsec':'convolution_pixel_arcsec'})
    op['source_native_pixel_arcsec']=json.loads((O/'provenance.json').read_text())['native_pixel_arcsec']
    op.to_csv(O/'psf_definition_and_operator_checks.csv',index=False)
    m=pd.read_csv(O/'morphology_resolution_results.csv');m=m[~m.source_control]
    rows=[];gains=[]
    for (family,metric),p in m.groupby(['family','metric']):
        for estimand in ['morphology','pair_transfer']:
            v=p.groupby(['subhalo_id','condition'])[estimand+'_abs_error'].mean().unstack()
            gain=v.w039-v.w020;lo,hi=ci(gain)
            rows.append(dict(family=family,metric=metric,estimand=estimand,n_galaxies=len(v),MAE_w039=v.w039.mean(),MAE_w020=v.w020.mean(),gain=gain.mean(),gain_lo=lo,gain_hi=hi,n_improved=int((gain>0).sum()),n_worse=int((gain<0).sum())))
            for sid in v.index:gains.append(dict(family=family,metric=metric,estimand=estimand,subhalo_id=sid,gain=gain[sid]))
    summary=pd.DataFrame(rows);summary.to_csv(O/'morphology_summary.csv',index=False)
    pd.DataFrame(gains).to_csv(O/'galaxy_morphology_gains.csv',index=False)
    score=pd.read_csv(O/'ml_information_gain_results.csv');specific=score[score.evaluation=='resolution_specific']
    display=specific[specific.test_condition=='w020'][['family','target','model','photometric_MAE','MAE','incremental_MAE','paired_width_gain','paired_width_gain_lo','paired_width_gain_hi','change_in_incremental_gain','change_in_incremental_gain_lo','change_in_incremental_gain_hi']]
    print('MORPHOLOGY\n'+summary.to_string(index=False))
    print('MATCHED ML\n'+display.to_string(index=False))
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':250,'pdf.fonttype':42})
    colors={'gaussian':'#245b91','moffat':'#bb681f'}
    fig,axs=plt.subplots(1,2,figsize=(10.5,4.7))
    gs=pd.DataFrame(gains)
    for ax,metric,unit in zip(axs,['R50','C'],['kpc','dimensionless']):
        for j,family in enumerate(['gaussian','moffat']):
            v=gs[(gs.family==family)&(gs.metric==metric)&(gs.estimand=='morphology')].gain.to_numpy()
            jitter=np.linspace(-.11,.11,len(v));ax.scatter(j+jitter,v,s=22,alpha=.55,c=colors[family],marker='o' if j==0 else 's')
            r=summary[(summary.family==family)&(summary.metric==metric)&(summary.estimand=='morphology')].iloc[0]
            ax.errorbar(j,r.gain,yerr=[[r.gain-r.gain_lo],[r.gain_hi-r.gain]],color='#222222',capsize=5,fmt='D',ms=6)
        ax.axhline(0,color='#666666',lw=1);ax.set(xticks=[0,1],xticklabels=['Gaussian','Moffat β=3.02'],ylabel=f'MAE(0.390) − MAE(0.200) [{unit}]',title='Ks '+('half-light radius' if metric=='R50' else 'concentration'))
    fig.suptitle('Direct dusty-morphology transfer at two assumed Ks FWHM values',fontsize=13)
    fig.text(.5,.015,'13 development galaxies; dots average 5 correlated views; diamonds: mean and galaxy-bootstrap 95% interval.\nNo added noise; fixed rest bands at z=0.1; 0.1″ detector pixels. Positive values favor 0.200″.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.10,1,.94])
    dest=O/'figures';dest.mkdir(exist_ok=True)
    for ext in ['png','pdf']:fig.savefig(dest/('morphology_width_gain.'+ext))
    plt.close(fig)
    fig,axs=plt.subplots(2,2,figsize=(11.5,7.3))
    labels={'A_g':'Integrated A_g [mag]','A_Ks':'Integrated A_Ks [mag]','dR50_Ks':'Paired ΔR50_Ks [kpc]','dC_Ks':'Paired ΔC_Ks [dimensionless]'}
    for ax,target in zip(axs.flat,['A_g','A_Ks','dR50_Ks','dC_Ks']):
        for j,family in enumerate(['gaussian','moffat']):
            for k,model in enumerate(['phot_ridge','summary_ridge','spatial_ridge']):
                r=display[(display.family==family)&(display.target==target)&(display.model==model)].iloc[0]
                y=k+(-.13 if j==0 else .13)
                ax.errorbar(r.paired_width_gain,y,xerr=[[r.paired_width_gain-r.paired_width_gain_lo],[r.paired_width_gain_hi-r.paired_width_gain]],fmt='o' if j==0 else 's',color=colors[family],capsize=3,label=family.capitalize() if k==0 else None)
        ax.axvline(0,color='#666666',lw=1);ax.set(yticks=[0,1,2],yticklabels=['Photometric ridge','Summary ridge','Spatial ridge'],title=labels[target],xlabel='Held-out MAE(0.390) − MAE(0.200)');ax.invert_yaxis()
    axs[0,0].legend(frameon=False,fontsize=9)
    fig.suptitle('Resolution-specific ridge fitting: conditional predictive gains',fontsize=13)
    fig.text(.5,.012,'13 development galaxies in 5 matched galaxy folds; fixed α=10; no added noise.\n95% galaxy-bootstrap intervals exclude retraining and instrument/source uncertainty; positive favors 0.200″.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.075,1,.95])
    for ext in ['png','pdf']:fig.savefig(dest/('ml_width_gain.'+ext))
    plt.close(fig)

if __name__=='__main__':main()
