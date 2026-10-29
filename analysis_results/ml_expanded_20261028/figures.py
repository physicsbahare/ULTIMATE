"""Publication figure rendering from frozen predictions and measured tables."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from expanded_features import O
from summarize import recommended

plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.bbox':'tight','figure.dpi':140,'font.family':'DejaVu Sans'})
COLORS={'optical':'#666666','seeing_NIR':'#0072B2','GLAO_NIR':'#D55E00'}
LABELS={'A_g':r'$A_{g,\mathrm{eff}}$ [mag]','dR50_Ks':r'$\Delta R_{50,Ks}$ [kpc]','dC_Ks':r'$\Delta C_{Ks}$','A_g_p50_1kpc':'Median 1-kpc effective g attenuation [mag]','A_g_IQR_1kpc':'IQR 1-kpc effective g attenuation [mag]'}
F=O/'figures';F.mkdir(exist_ok=True)
def save(fig,name):
    for suffix in ['png','pdf']:fig.savefig(F/(name+'.'+suffix))
    plt.close(fig)

def run():
    final=(O/'FINAL_EVALUATION_COMPLETED.json').exists()
    evaluation='final_test' if final else 'validation'
    pred=pd.read_csv(O/('final_predictions.csv.gz' if final else 'validation_and_control_predictions.csv.gz'))
    pred=recommended(pred[(pred.aperture=='adaptive')&~pred.zero_projected_dust&(pred.evaluation==evaluation)])
    fig,axs=plt.subplots(1,3,figsize=(12,3.6))
    for ax,target in zip(axs,['A_g','dR50_Ks','dC_Ks']):
        for scenario in ['seeing_NIR','GLAO_NIR']:
            p=pred[(pred.target==target)&(pred.scenario==scenario)].groupby(['subhalo_id','view'])[['truth','prediction']].mean()
            ax.scatter(p.truth,p.prediction,s=14,alpha=.5,color=COLORS[scenario],label=scenario.replace('_',' '))
        limits=ax.get_xlim();low=min(limits[0],ax.get_ylim()[0]);high=max(limits[1],ax.get_ylim()[1]);ax.plot([low,high],[low,high],c='k',lw=.8,ls='--')
        ax.set(xlabel='Atlas target: '+LABELS[target],ylabel='Prediction',title=target)
    axs[0].legend(fontsize=8);fig.suptitle(evaluation+': recommended models; each point = galaxy orientation, four draws averaged\nOperational product contrasts; no calibrated physical dust truth',fontsize=10);fig.tight_layout();save(fig,'prediction_vs_atlas_target')
    m=pd.read_csv(O/'performance_summary.csv');m=m[(m.evaluation==evaluation)&(m.aperture=='adaptive')]
    fig,axs=plt.subplots(1,3,figsize=(12,3.6))
    for ax,target in zip(axs,['A_g','dR50_Ks','dC_Ks']):
        recfamily=pd.read_csv(O/'recommended_settings.csv').set_index('target').loc[target,'family']
        families=list(dict.fromkeys(['median','phot_ridge',recfamily]))
        for j,scenario in enumerate(COLORS):
            p=m[(m.target==target)&(m.scenario==scenario)].set_index('family').loc[families]
            ax.bar(np.arange(len(families))+(j-1)*.25,p.MAE,width=.24,color=COLORS[scenario],label=scenario.replace('_',' '))
        ax.set_xticks(np.arange(len(families)),[s.replace('_','\n') for s in families],fontsize=8);ax.set_ylabel('Equal-galaxy MAE');ax.set_title(LABELS[target])
    axs[0].legend(fontsize=7);fig.suptitle('Frozen model comparison: '+evaluation+' (Ks-defined adaptive aperture)');fig.tight_layout();save(fig,'model_and_observing_strategy_comparison')
    gains=pd.read_csv(O/'recommended_gains.csv');p=gains[(gains.evaluation==evaluation)&(gains.aperture=='adaptive')&(gains.comparison=='seeing_minus_GLAO_MAE')]
    fig,axs=plt.subplots(1,3,figsize=(11,3))
    for ax,target in zip(axs,['A_g','dR50_Ks','dC_Ks']):
        r=p[p.target==target].iloc[0];ax.errorbar([r.gain],[0],xerr=[[max(0,r.gain-r.low)],[max(0,r.high-r.gain)]],fmt='o',color=COLORS['GLAO_NIR'],capsize=5);ax.axvline(0,c='k',ls='--',lw=.8);ax.set_yticks([]);ax.set(xlabel='Seeing MAE − GLAO MAE',title=LABELS[target])
    fig.suptitle('Paired galaxy-bootstrap 95% intervals; positive = GLAO advantage');fig.tight_layout();save(fig,'paired_GLAO_gains')
    lc=pd.read_csv(O/'learning_curves.csv');fig,axs=plt.subplots(1,3,figsize=(11,3.3))
    for ax,target in zip(axs,['A_g','dR50_Ks','dC_Ks']):
        for scenario in ['seeing_NIR','GLAO_NIR']:
            p=lc[(lc.target==target)&(lc.scenario==scenario)].groupby('n_training_galaxies').MAE.agg(['mean','min','max'])
            ax.plot(p.index,p['mean'],marker='o',c=COLORS[scenario],label=scenario.replace('_',' '));ax.fill_between(p.index,p['min'],p['max'],color=COLORS[scenario],alpha=.15)
        ax.set(xlabel='Independent development galaxies',ylabel='Validation MAE',title=LABELS[target])
    axs[0].legend(fontsize=8);fig.suptitle('Learning curves: 13 validation galaxies; shaded three subset seeds, not a population CI');fig.tight_layout();save(fig,'learning_curves')
    tables=[pd.read_csv(O/'target_table.csv')]
    if final:tables.append(pd.read_csv(O/'final_target_table.csv'))
    t=pd.concat(tables);t=t[~t.zero_projected_dust];a=t[t.aperture=='adaptive'];b=t[t.aperture=='fixed12'];paired=a.merge(b,on=['subhalo_id','view'],suffixes=('_adaptive','_fixed12'))
    fig,axs=plt.subplots(1,3,figsize=(11,3.2))
    for ax,target in zip(axs,['A_g','dR50_Ks','dC_Ks']):
        ax.scatter(paired[target+'_fixed12'],paired[target+'_adaptive'],s=10,c='#009E73',alpha=.35);lo=min(ax.get_xlim()[0],ax.get_ylim()[0]);hi=max(ax.get_xlim()[1],ax.get_ylim()[1]);ax.plot([lo,hi],[lo,hi],'k--',lw=.8);ax.set(xlabel='Fixed R=12 kpc',ylabel='Adaptive aperture',title=LABELS[target])
    fig.suptitle('Targets depend on aperture: every available non-null orientation');fig.tight_layout();save(fig,'aperture_target_sensitivity')
    # Residual-property diagnostics preserve per-galaxy/orientation sampling.
    fig,axs=plt.subplots(1,3,figsize=(11,3.2),layout='constrained')
    for ax,target in zip(axs,['A_g','dR50_Ks','dC_Ks']):
        p=pred[(pred.target==target)&(pred.scenario=='GLAO_NIR')].groupby(['subhalo_id','view']).agg(error=('error','mean'),mass=('log_stellar_mass','first'),q=('observed_Ks_q','mean'))
        points=ax.scatter(p.mass,p.error,c=p.q,cmap='viridis',vmin=0,vmax=1,s=20,alpha=.75);ax.axhline(0,c='k',ls='--',lw=.8);ax.set(xlabel=r'Atlas $\log_{10}(M_*/M_\odot)$',ylabel='Prediction − atlas target',title=LABELS[target])
    fig.colorbar(points,ax=axs,label='Observed Ks axis ratio',fraction=.025,pad=.02);fig.suptitle('Exploratory residual diagnostics; physical metadata are scoring-only');save(fig,'residuals_and_galaxy_properties')
    fig,axs=plt.subplots(2,2,figsize=(9,7))
    for col,target in enumerate(['A_g_p50_1kpc','A_g_IQR_1kpc']):
        ax=axs[0,col]
        for scenario in ['seeing_NIR','GLAO_NIR']:
            q=pred[(pred.target==target)&(pred.scenario==scenario)].groupby(['subhalo_id','view'])[['truth','prediction']].mean()
            ax.scatter(q.truth,q.prediction,c=COLORS[scenario],s=14,alpha=.5,label=scenario.replace('_',' '))
        lo=min(ax.get_xlim()[0],ax.get_ylim()[0]);hi=max(ax.get_xlim()[1],ax.get_ylim()[1]);ax.plot([lo,hi],[lo,hi],'k--',lw=.8);ax.set(xlabel='Atlas target [mag]',ylabel='Prediction [mag]',title=LABELS[target],xlim=(lo,hi),ylim=(lo,hi))
        ax=axs[1,col];family=pd.read_csv(O/'recommended_settings.csv').set_index('target').loc[target,'family'];families=['median','phot_ridge',family]
        for j,scenario in enumerate(['seeing_NIR','GLAO_NIR']):
            q=m[(m.target==target)&(m.scenario==scenario)].set_index('family').loc[families]
            ax.bar(np.arange(3)+(j-.5)*.3,q.MAE,width=.28,color=COLORS[scenario])
        ax.set_xticks(np.arange(3),[x.replace('_','\n') for x in families],fontsize=8);ax.set_ylabel('Equal-galaxy MAE [mag]')
    axs[0,0].legend(fontsize=7);fig.suptitle('Spatial summary targets, not pixel maps or 3D geometry; '+evaluation+'\nOperational attenuation after 1-kpc smoothing; source calibration unresolved',fontsize=10);fig.tight_layout();save(fig,'spatial_attenuation_statistics')
    print('Wrote seven publication figures in PNG and PDF.')

if __name__=='__main__':run()
