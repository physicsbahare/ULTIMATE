"""Descriptive examples selected by lowest/median/highest final Ks-C error, no tuning."""
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from expanded_features import O,SOURCE,geometry,old
from summarize import recommended

def run():
    assert (O/'FINAL_EVALUATION_COMPLETED.json').exists()
    p=recommended(pd.read_csv(O/'final_predictions.csv.gz'))
    ranks=p[(p.aperture=='adaptive')&(p.scenario=='GLAO_NIR')&(p.target=='dC_Ks')&~p.zero_projected_dust].groupby('subhalo_id').abs_error.mean().sort_values()
    ids=[int(ranks.index[i]) for i in [0,len(ranks)//2,len(ranks)-1]]
    pd.DataFrame(dict(subhalo_id=ids,selection=['lowest','median','highest'],criterion='Final GLAO recommended dC_Ks equal-galaxy MAE')).to_csv(O/'representative_image_selection.csv',index=False)
    fig,axs=plt.subplots(3,6,figsize=(15,8.5),sharex=True,sharey=True)
    t=pd.read_csv(O/'final_target_table.csv')
    for row,sid in enumerate(ids):
        with np.load(O/'data_audit/cache'/str(sid)/'O1.npz') as a:
            dusty=np.array([a['dusty_'+b] for b in SOURCE],float);clear=np.array([a['clear_'+b] for b in SOURCE],float)
        radius=t[(t.subhalo_id==sid)&(t.view=='O1')&(t.aperture=='adaptive')].radius_kpc.iloc[0]
        c=gaussian_filter(clear[0],10/2.354820045);d=gaussian_filter(dusty[0],10/2.354820045)
        attenuation=np.where((c>c.max()*1e-4)&(d>0),-2.5*np.log10(np.maximum(d,1e-30)/np.maximum(c,1e-30)),np.nan)
        modes={}
        for mode in ['seeing','glao']:
            g=geometry(mode);rate,_=old.p.render(dusty,g)
            modes[mode]=rate[2]/old.p.INST[2]['flat_e_s_per_jy']/(g['pixel']/206265.)**2/1e6
        images=[clear[0],dusty[0],attenuation,dusty[2],modes['seeing'],modes['glao']]
        extent=[-40,40,-40,40];g=geometry('seeing');observedextent=[g['x'].min()-.5*g['pixel']*g['scale'],g['x'].max()+.5*g['pixel']*g['scale'],g['y'].min()-.5*g['pixel']*g['scale'],g['y'].max()+.5*g['pixel']*g['scale']]
        norms={}
        for band,j in [('g',0),('Ks',2)]:
            v=dusty[j][dusty[j]>0];norms[band]=np.log10(np.quantile(v,.3)),np.log10(np.quantile(v,.999))
        for col,(ax,im) in enumerate(zip(axs[row],images)):
            if col==2:
                plotted=ax.imshow(im,origin='lower',extent=extent,cmap='RdBu_r',vmin=-.3,vmax=1.);fig.colorbar(plotted,ax=ax,shrink=.65,label='mag')
            else:
                band='g' if col<2 else 'Ks';vmin,vmax=norms[band]
                ax.imshow(np.log10(np.maximum(im,1e-15)),origin='lower',extent=extent if col<4 else observedextent,cmap='magma',vmin=vmin,vmax=vmax)
                if col in [0,3]:ax.text(.025,.98,f'log10 I [MJy/sr]\n{vmin:.1f} to {vmax:.1f}',transform=ax.transAxes,va='top',color='white',fontsize=6,bbox=dict(facecolor='black',alpha=.5,pad=1))
            ax.add_patch(Circle((0,0),radius,fill=False,color='white' if col!=2 else 'k',lw=.6,ls='--'))
            ax.set(xlim=(-30,30),ylim=(-30,30))
            if row==0:ax.set_title(['Native clear g','Native dusty g','1-kpc effective g contrast','Native dusty Ks','Seeing Ks, noiseless','GLAO Ks, noiseless'][col],fontsize=8)
            if row==2:ax.set_xlabel('kpc')
        axs[row,0].set_ylabel(str(sid)+' / O1\n'+['lowest','median','highest'][row]+' dC error\nkpc')
    fig.suptitle('Final examples selected by predeclared error ranks; O1 shown for each galaxy\nPer-row/band shared log surface-brightness scale; actual LSST g / 2MASS Ks, fixed-rest-band experiment',fontsize=10)
    fig.tight_layout();(O/'figures').mkdir(exist_ok=True)
    for suffix in ['pdf','png']:fig.savefig(O/'figures'/('representative_success_and_failure_images.'+suffix),bbox_inches='tight',dpi=160)
    plt.close(fig)

if __name__=='__main__':run()
