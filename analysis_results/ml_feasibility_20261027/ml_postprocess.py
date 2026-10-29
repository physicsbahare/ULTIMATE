"""Paired galaxy-level ablations, diagnostics, and publication-sized figures."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ml_benchmark import OUT, TARGETS, bootstrap

NAMES = {'A_g':'Integrated g attenuation [mag]', 'A_Ks':'Integrated Ks attenuation [mag]',
         'A_g_p50_1kpc':'Median g attenuation, 1 kpc [mag]', 'dR50_g':'Dust ΔR50, g [kpc]',
         'dR50_Ks':'Dust ΔR50, Ks [kpc]', 'dC_g':'Dust ΔC, g', 'dC_Ks':'Dust ΔC, Ks'}
COLORS = {'median':'#777777', 'photometric_ridge':'#bc6500', 'morphology_ridge':'#637c23',
          'ridge':'#0072b2', 'forest':'#aa4488'}


def paired_tables(galaxy):
    all_rows = []
    for (condition, mode, target), group in galaxy.groupby(['condition','mode','target']):
        index = group.pivot(index='subhalo_id', columns=['bandset','model'], values='MAE')
        for model in ['ridge','forest']:
            for comparison, baseline in [('extra_NIR', ('g_only', model)),
                                         ('versus_median', ('g_J_Ks','median')),
                                         ('versus_photometric', ('g_J_Ks','photometric_ridge'))]:
                differences = index[baseline]-index['g_J_Ks',model]
                low, high = bootstrap(differences)
                all_rows.append(dict(condition=condition, mode=mode, target=target, model=model,
                    comparison=comparison, mean_gain=differences.mean(), CI_low=low, CI_high=high,
                    n_improved=int((differences > 1e-10).sum()), n_galaxies=len(differences)))
    pd.DataFrame(all_rows).to_csv(OUT/'paired_model_comparisons.csv', index=False)
    correction = []
    for values, group in galaxy[galaxy.target.str.startswith('d')].groupby(['condition','mode','bandset','model','target']):
        low, high = bootstrap(group.correction_gain)
        correction.append(dict(zip(['condition','mode','bandset','model','target'],values),
            uncorrected_MAE=group.uncorrected_clear_MAE.mean(), corrected_MAE=group.corrected_clear_MAE.mean(),
            mean_gain=group.correction_gain.mean(), CI_low=low, CI_high=high,
            n_improved=int((group.correction_gain>1e-10).sum()), n_galaxies=len(group)))
    pd.DataFrame(correction).to_csv(OUT/'correction_summary.csv', index=False)


def figures():
    plt.rcParams.update({'font.size':10, 'axes.spines.top':False, 'axes.spines.right':False,
                         'savefig.bbox':'tight', 'figure.dpi':140})
    destination=OUT/'figures'; destination.mkdir(exist_ok=True)
    def save(fig, name):
        fig.savefig(destination/(name+'.png'), dpi=180)
        fig.savefig(destination/(name+'.pdf'))
        plt.close(fig)
    summary=pd.read_csv(OUT/'heldout_summary.csv')
    galaxy=pd.read_csv(OUT/'galaxy_heldout_errors.csv')
    selected=summary[(summary.condition=='original_noise') & (summary['mode']=='glao') & (summary.bandset=='g_J_Ks')]
    models=['median','photometric_ridge','morphology_ridge','ridge','forest']
    labels=['Constant','Photometry','Morphology','Full ridge','Forest']
    fig,axes=plt.subplots(2,4,figsize=(15,7),constrained_layout=True)
    for ax,target in zip(axes.flat,TARGETS):
        part=selected[selected.target==target].set_index('model').loc[models]
        x=np.arange(len(models));err=np.vstack([part.MAE-part.MAE_CI_low,part.MAE_CI_high-part.MAE])
        ax.bar(x,part.MAE,color=[COLORS[m] for m in models],yerr=err,capsize=2)
        ax.set_xticks(x,labels,rotation=40,ha='right');ax.set_title(NAMES[target]);ax.set_ylabel('Held-out galaxy MAE');ax.set_ylim(bottom=0)
    axes.flat[-1].axis('off')
    fig.suptitle('Exploratory grouped CV: 22 galaxies, g/J/Ks, GLAO proxy\n95% galaxy resampling intervals; unresolved physical-label systematics excluded',fontsize=13)
    save(fig,'01_grouped_ML_errors')
    gains=pd.read_csv(OUT/'GLAO_ML_gain_summary.csv')
    fig,axes=plt.subplots(1,3,figsize=(14,5),constrained_layout=True)
    for ax,condition in zip(axes,['original_noise','equal_noise','noiseless']):
        for offset,model in [(-.12,'ridge'),(.12,'forest')]:
            s=gains[(gains.condition==condition)&(gains.bandset=='g_J_Ks')&(gains.model==model)].set_index('target').loc[TARGETS]
            # Relative gains put heterogeneous targets on a common, defined scale.
            norm=s.seeing_MAE.to_numpy();value=s.mean_gain.to_numpy()/norm
            ax.errorbar(value,np.arange(7)+offset,xerr=np.vstack([(s.mean_gain-s.CI_low)/norm,(s.CI_high-s.mean_gain)/norm]),fmt='o' if model=='ridge' else 's',color=COLORS[model],label=model,capsize=2)
        ax.axvline(0,color='#555555',lw=1);ax.set_yticks(np.arange(7),TARGETS);ax.set_xlabel('Error reduction / seeing MAE');ax.set_title(condition.replace('_',' '));ax.legend()
    fig.suptitle('GLAO benefit is metric and model dependent; intervals resample 22 galaxies\nPositive favors GLAO. g-only controls have exactly zero gain.',fontsize=13)
    save(fig,'02_GLAO_ML_ablation')
    # Extra bands versus PSF, exact values retained in supporting tables.
    comparisons=pd.read_csv(OUT/'paired_model_comparisons.csv')
    fig,axes=plt.subplots(1,3,figsize=(13,4),constrained_layout=True)
    for ax,target in zip(axes,['A_g','dR50_Ks','dC_Ks']):
        s=summary[(summary.condition=='original_noise')&(summary.model=='ridge')&(summary.target==target)]
        chosen=[('g_only','seeing'),('g_J_Ks','seeing'),('g_J_Ks','glao')]
        values=[s[(s.bandset==bands)&(s['mode']==mode)].iloc[0].MAE for bands,mode in chosen]
        ax.bar(np.arange(3),values,color=['#777777','#bc6500','#0072b2'])
        ax.set_xticks(np.arange(3),['g only','g/J/Ks\nseeing','g/J/Ks\nGLAO']);ax.set_title(NAMES[target]);ax.set_ylabel('Held-out galaxy MAE');ax.set_ylim(bottom=0)
    fig.suptitle('Extra NIR bands and improved resolution are separate comparisons\nFixed 1 h per band: g-only uses less total observing time',fontsize=13)
    save(fig,'03_extra_bands_vs_resolution')
    fig,axes=plt.subplots(2,2,figsize=(10,8),constrained_layout=True)
    use=galaxy[(galaxy.condition=='original_noise')&(galaxy['mode']=='glao')&(galaxy.bandset=='g_J_Ks')&(galaxy.model=='ridge')]
    for ax,target in zip(axes.flat,['A_g','A_g_p50_1kpc','dR50_Ks','dC_g']):
        s=use[use.target==target]
        ax.scatter(s.truth_mean,s.truth_mean+s.bias,c='#0072b2',label='held-out galaxy mean')
        outlier=s[s.subhalo_id==294866]
        ax.scatter(outlier.truth_mean,outlier.truth_mean+outlier.bias,marker='s',facecolors='none',edgecolors='#bc6500',s=80,label='294866')
        lo=min(s.truth_mean.min(),(s.truth_mean+s.bias).min());hi=max(s.truth_mean.max(),(s.truth_mean+s.bias).max())
        ax.plot([lo,hi],[lo,hi],'--',c='#555555');ax.set_xlabel('Operational DR1 truth');ax.set_ylabel('Held-out prediction');ax.set_title(NAMES[target]);ax.legend(fontsize=8)
    fig.suptitle('Ridge predictions: galaxy means conceal some orientation errors\nFull view/draw errors and source-control challenge remain tabulated',fontsize=13)
    save(fig,'04_heldout_predictions')
    fig,axes=plt.subplots(1,2,figsize=(13,4.5),constrained_layout=True)
    for model in ['median','photometric_ridge','ridge','forest']:
        s=selected[selected.model==model].set_index('target').loc[TARGETS]
        axes[0].plot(np.arange(7),s.simultaneous_galaxy_coverage,'o-',color=COLORS[model],label=model)
    axes[0].axhline(.8,ls='--',c='#555555');axes[0].set_xticks(np.arange(7),TARGETS,rotation=45,ha='right');axes[0].set_ylim(0,1.03);axes[0].set_ylabel('Entire-galaxy empirical coverage');axes[0].legend(fontsize=8)
    ood=pd.read_csv(OUT/'OOD_summary.csv');target='dR50_Ks'
    for j,model in enumerate(['median','ridge','forest']):
        values=[selected[(selected.model==model)&(selected.target==target)].iloc[0].MAE]
        values += [ood[(ood.model==model)&(ood.target==target)&(ood.challenge==c)].iloc[0].MAE for c in ['high_mass_quartile','zero_projected_dust_controls']]
        axes[1].bar(np.arange(3)+j*.23,values,width=.22,color=COLORS[model],label=model)
    axes[1].set_xticks(np.arange(3)+.23,['Grouped CV\n22 galaxies','High mass OOD\n6 galaxies','Source controls\n4 galaxies']);axes[1].set_ylabel('Ks dust ΔR50 MAE [kpc]');axes[1].legend(fontsize=8)
    fig.suptitle('Uncertainty diagnostics and deliberately shifted tests\nNominal 80% intervals from only five calibration galaxies per fold',fontsize=13)
    save(fig,'05_uncertainty_and_OOD')
    correction=pd.read_csv(OUT/'correction_summary.csv')
    fig,axes=plt.subplots(1,4,figsize=(14,4),constrained_layout=True)
    for ax,target in zip(axes,['dR50_g','dR50_Ks','dC_g','dC_Ks']):
        part=correction[(correction.condition=='original_noise')&(correction['mode']=='glao')&(correction.bandset=='g_J_Ks')&(correction.target==target)].set_index('model')
        values=[part.loc['ridge','uncorrected_MAE'],part.loc['median','corrected_MAE'],part.loc['photometric_ridge','corrected_MAE'],part.loc['ridge','corrected_MAE'],part.loc['forest','corrected_MAE']]
        ax.bar(np.arange(5),values,color=['#333333',COLORS['median'],COLORS['photometric_ridge'],COLORS['ridge'],COLORS['forest']]);ax.set_xticks(np.arange(5),['Raw','Constant','Photometry','Ridge','Forest'],rotation=45,ha='right');ax.set_title(NAMES[target]);ax.set_ylabel('Error vs native clear morphology');ax.set_ylim(bottom=0)
    fig.suptitle('Dust-bias subtraction can help, but simple correction baselines also help\nPSF and noise error remain; no dust-free image reconstruction is claimed',fontsize=13)
    save(fig,'06_morphology_correction')


def run():
    paired_tables(pd.read_csv(OUT/'galaxy_heldout_errors.csv'))
    figures()
    print('Paired ablations and six PNG/PDF figures written.')


if __name__=='__main__':
    run()
