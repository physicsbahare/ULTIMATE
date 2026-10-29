"""Paired labels and observable image features; final partition is blocked by default."""
from pathlib import Path
import sys,json,time
import numpy as np
import pandas as pd
from scipy import ndimage as ndi

O=Path(__file__).resolve().parent
PREV=O.parent/'multigalaxy_morphology_20261027'
PART=O.parent/'ml_feasibility_20261027/expansion/galaxy_partitions.csv'
_path=sys.path.copy();sys.path.insert(0,str(PREV))
import observe as old
from morphology import Geometry,measure
sys.path[:]=_path
BANDS=['g','J','Ks'];SOURCE=['LSST_g','2MASS_J','2MASS_Ks']
TARGETS=['A_g','A_Ks','A_g_p50_1kpc','A_g_IQR_1kpc','dR50_Ks','dC_Ks','dR50_g','dC_g']


def geometry(mode,pixel=.1):
    g=old.p.make_geometry(.1,mode)
    native=.1/g['scale'];nout=2*int(np.ceil(48/g['scale']/pixel))
    outedges=(np.arange(nout+1)-nout/2)*pixel
    size=2*int(np.ceil(35/g['scale']/pixel));start=(nout-size)//2
    xy=(np.arange(size)+.5-size/2)*pixel*g['scale'];y,x=np.meshgrid(xy,xy,indexing='ij')
    g.update(pixel=pixel,native=native,edges=(np.arange(961)-480)*native,
        outedges=outedges,nout=nout,sl=slice(start,start+size),shape=(size,size),x=x,y=y,r=np.hypot(x,y),roi=np.hypot(x,y)<30)
    return g


def aperture_policy(dusty):
    # Same observable deep Ks seeing reference determines BOTH paired apertures.
    sigma=old.p.INST[2]['seeing_fwhm_arcsec']*geometry('seeing')['scale']/.1/2.354820045
    seeing=ndi.gaussian_filter(dusty[2],sigma,mode='constant',truncate=5)
    outer=Geometry(800,.1,35)
    r80=measure(seeing,outer)['R80'];raw=1.5*r80
    radius=float(np.clip(raw,8.,30.))
    fraction=float(seeing[outer.r<radius].sum()/seeing[outer.mask].sum())
    return radius,dict(reference_Ks_R80_R35_kpc=r80,adaptive_unclipped_radius_kpc=raw,
                       adaptive_radius_capped=bool(raw>30),adaptive_minimum_applied=bool(raw<8),
                       reference_fraction_of_R35=fraction,reference_aperture_limited=bool(fraction<.9))


def labels_for(clear,dusty,radius):
    g=Geometry(800,.1,radius);result={}
    for j,band in [(0,'g'),(2,'Ks')]:
        c,d=measure(clear[j],g),measure(dusty[j],g)
        result['A_'+band]=-2.5*np.log10(d['flux']/c['flux'])
        for metric in ['R50','C']:
            result['d'+metric+'_'+band]=d[metric]-c[metric]
            result['clear_'+metric+'_'+band]=c[metric]
            result['dusty_'+metric+'_'+band]=d[metric]
    c=ndi.gaussian_filter(clear[0],1/.1/2.354820045,mode='constant',truncate=5)
    d=ndi.gaussian_filter(dusty[0],1/.1/2.354820045,mode='constant',truncate=5)
    valid=g.mask&(c>c.max()*1e-4)&(d>0)&np.isfinite(c)&np.isfinite(d)
    effective=-2.5*np.log10(d[valid]/c[valid]);p25,p50,p75=np.quantile(effective,[.25,.5,.75])
    result.update(A_g_p50_1kpc=p50,A_g_IQR_1kpc=p75-p25,valid_attenuation_pixels=int(valid.sum()),
                  negative_Aeff_fraction=float(np.mean(effective<0)))
    return result


class FeaturePlan:
    def __init__(self,g,radius):
        self.g=g;self.radius=radius
        self.m=Geometry(g['shape'][0],g['pixel']*g['scale'],radius)
        self.regions=[(g['r']<radius*f) for f in [.1,.25,.5,.75]]
        self.theta=np.arctan2(g['y'],g['x'])
        # Circular 8x8 cells in observed sky coordinates; no truth alignment/inclination.
        self.bin_x=np.clip(np.floor((g['x']/radius+1)*4),0,7).astype(int)
        self.bin_y=np.clip(np.floor((g['y']/radius+1)*4),0,7).astype(int)
        self.cell=self.bin_y[self.m.mask]*8+self.bin_x[self.m.mask]
    def __call__(self,images):
        result={};logs={}
        for j,band in enumerate(BANDS):
            im=images[j];measured=measure(im,self.m);flux=measured['flux']
            for key in ['R50','C','A','q']:result[band+'_'+key]=measured[key]
            jy=flux/old.p.INST[j]['flat_e_s_per_jy']
            logs[band]=np.log10(jy) if jy>0 else np.nan
            result[band+'_logJy']=logs[band]
            for k,region in enumerate(self.regions):
                result[f'{band}_radial{k}']=float(im[region].sum()/flux) if flux>0 else np.nan
            inner=im[self.regions[1]].sum()/old.p.INST[j]['flat_e_s_per_jy']
            outer=jy-inner
            result[band+'_inner_logJy']=np.log10(inner) if inner>0 else np.nan
            result[band+'_outer_logJy']=np.log10(outer) if outer>0 else np.nan
            theta=self.theta[self.m.mask];values=im[self.m.mask]
            for harmonic in [1,2,4]:
                result[f'{band}_harmonic{harmonic}']=float(abs(np.sum(values*np.exp(1j*harmonic*theta)))/flux) if flux>0 else np.nan
            if band in ['g','Ks']:
                cells=np.bincount(self.cell,weights=values,minlength=64)/flux if flux>0 else np.full(64,np.nan)
                for k,value in enumerate(cells):result[f'cell_{band}_{k:02d}']=float(value)
                for size in [.5,1.,2.]:
                    residual=im-ndi.gaussian_filter(im,size/(self.g['pixel']*self.g['scale'])/2.354820045,mode='constant',truncate=5)
                    result[f'{band}_texture_{size}']=float(np.sqrt(np.mean(residual[self.m.mask]**2))/(flux/self.m.mask.sum())) if flux>0 else np.nan
        for a,b in [('g','J'),('J','Ks')]:
            result['color_'+a+'_'+b]=-2.5*(logs[a]-logs[b])
            result['gradient_'+a+'_'+b]=-2.5*(result[a+'_inner_logJy']-result[b+'_inner_logJy']-result[a+'_outer_logJy']+result[b+'_outer_logJy'])
        return result


def process(sid,partition,final=False):
    if partition=='final_test':
        assert final and (O/'FINAL_PROTOCOL_FROZEN.json').exists(),'Final scientific access is sealed'
    cache=O/'data_audit/cache'/str(sid)
    dest=O/'derived'/str(sid);dest.mkdir(parents=True,exist_ok=True)
    if (dest/'complete.json').exists():return
    assert (cache/'complete.json').exists()
    meta=pd.read_csv(PART).set_index('subhalo_id').loc[sid]
    physical=pd.read_csv(cache/'physical.csv')
    # The data-audit product uses full projected fields only for quality/scoring metadata.
    dust=physical[physical['product']=='dustmass'] if 'product' in physical else physical
    fieldcol='field_mass_Msun'
    dustmass=float(dust[fieldcol].mean())
    labels=[];features=[];transfer=[];policy=[]
    geometries={mode:geometry(mode) for mode in ['seeing','glao']}
    for view in [f'O{i}' for i in range(1,6)]:
        with np.load(cache/(view+'.npz')) as arrays:
            clear=np.array([arrays['clear_'+b] for b in SOURCE],dtype=float)
            dusty=np.array([arrays['dusty_'+b] for b in SOURCE],dtype=float)
        adaptive,flags=aperture_policy(dusty)
        policy.append(dict(subhalo_id=sid,view=view,radius_kpc=adaptive,**flags))
        plans={}
        for aperture,radius in [('fixed12',12.),('adaptive',adaptive)]:
            values=labels_for(clear,dusty,radius)
            assert np.isfinite([values[t] for t in TARGETS]).all()
            labels.append(dict(subhalo_id=sid,view=view,partition=partition,aperture=aperture,
                radius_kpc=radius,zero_projected_dust=bool(dustmass<=0),dust_mass_field_Msun=dustmass,
                stellar_mass_Msun=meta.stellar_mass_Msun,SFR_Msun_yr=meta.SFR_Msun_yr,
                log_stellar_mass=meta.log10_stellar_mass,**flags,**values))
            for mode,g in geometries.items():plans[aperture,mode]=FeaturePlan(g,radius)
        rates={};variance={}
        for mode,g in geometries.items():
            rates[mode],loss=old.p.render(dusty,g);variance[mode]=old.p.variance(rates[mode],1.)
            transfer.append(dict(subhalo_id=sid,view=view,mode=mode,padded_flux_loss=loss))
            assert loss<1e-5
        shared=np.maximum(variance['seeing'],variance['glao'])
        rng=np.random.default_rng(20261028+int(sid)*101+int(view[1:])*1000003)
        for draw in range(4):
            epsilon=rng.normal(size=rates['seeing'].shape)
            for condition in ['nominal','equal_noise','noiseless']:
                for mode in ['seeing','glao']:
                    noise=variance[mode] if condition=='nominal' else shared
                    image=rates[mode] if condition=='noiseless' else rates[mode]+np.sqrt(noise)*epsilon
                    for aperture in ['fixed12','adaptive']:
                        features.append(dict(subhalo_id=sid,view=view,draw=draw,partition=partition,
                            aperture=aperture,condition=condition,mode=mode,**plans[aperture,mode](image)))
        print('Derived',sid,view,flush=True)
    pd.DataFrame(labels).to_csv(dest/'labels.csv',index=False)
    pd.DataFrame(features).to_csv(dest/'features.csv.gz',index=False)
    pd.DataFrame(policy).to_csv(dest/'apertures.csv',index=False)
    pd.DataFrame(transfer).to_csv(dest/'transfer.csv',index=False)
    (dest/'complete.json').write_text(json.dumps(dict(subhalo_id=int(sid),partition=partition,views=5,draws=4,complete=True)))


def assemble(final=False):
    meta=pd.read_csv(PART)
    permitted=meta if final else meta[meta.partition!='final_test']
    complete=[O/'derived'/str(sid) for sid in permitted.subhalo_id if (O/'derived'/str(sid)/'complete.json').exists()]
    if not complete:return
    for filename,target in [('labels.csv','target_table.csv'),('features.csv.gz','feature_table.csv.gz'),('apertures.csv','aperture_policies.csv'),('transfer.csv','render_validation.csv')]:
        pd.concat([pd.read_csv(p/filename) for p in complete],ignore_index=True).to_csv(O/target,index=False)


def run(watch=False,final=False):
    meta=pd.read_csv(PART)
    permitted=meta if final else meta[meta.partition!='final_test']
    while True:
        count=0
        for row in permitted.itertuples():
            if (O/'data_audit/cache'/str(row.subhalo_id)/'complete.json').exists():
                process(row.subhalo_id,row.partition,final=final);count+=1
        assemble(final)
        print('Available derived galaxies',count,'/',len(permitted),flush=True)
        if count==len(permitted) or not watch:break
        time.sleep(15)


if __name__=='__main__':run('--watch' in sys.argv,'--final' in sys.argv)
