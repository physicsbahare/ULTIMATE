"""Metadata-only fixed sample; never opens a science archive or image."""
import csv, hashlib, json, math, random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path('/home/bahareh/ULTIMATE')
OUT=ROOT/'analysis_results/ml_feasibility_20261027/expansion'
DATA=ROOT/'data/TNG50_SKIRT_DR1_ml_expansion'
OLD=ROOT/'data/TNG50_SKIRT_DR1_extra'
SEED=20261027

def write_csv(path, rows):
    with path.open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    if (OUT/'partitions_frozen.json').exists():
        raise SystemExit('Frozen selection exists; refusing to redraw.')
    inventory=list(csv.DictReader((ROOT/'analysis_results/multigalaxy_morphology_20261027/galaxy_inventory.csv').open()))
    old_ids={int(r['subhalo_id']) for r in inventory}
    assert len(old_ids)==26
    fields=['subhalo_id','stellar_mass_Msun','gas_mass_Msun','dark_matter_mass_Msun','SFR_Msun_yr','stellar_half_mass_radius_kpc']
    rows=[]
    for line in (OLD/'baes24_tng50_skirt_atlas.txt').read_text().splitlines():
        if not line or line.startswith('#'):continue
        v=line.split();r=dict(zip(fields,[int(v[0])]+[float(x) for x in v[1:]]))
        r['log10_stellar_mass']=math.log10(r['stellar_mass_Msun'])
        r['sSFR_yr_inverse']=r['SFR_Msun_yr']/r['stellar_mass_Msun'];rows.append(r)
    assert len({r['subhalo_id'] for r in rows})==len(rows)==1154
    # Use previously documented mass/activity strata and their exact thresholds.
    prior=list(csv.DictReader((OLD/'eligible_catalogue.csv').open()))
    strata={int(r['subhalo_id']):(int(r['mass_stratum']),int(r['activity_stratum'])) for r in prior}
    excluded=set(old_ids)
    # Correctly parse only the ID suffix, never the '50' in TNG50.
    import re
    archives=[]
    for base in [ROOT/'TNG50_SKIRT/downloads',OLD]:
        for p in base.glob('*.tar.gz*'):
            m=re.fullmatch(r'TNG50_DR1_(\d+)\.tar\.gz(?:\.part)?',p.name)
            if m:excluded.add(int(m[1]));archives.append({'path':str(p),'subhalo_id':int(m[1]),'bytes':p.stat().st_size})
    rng=random.Random(SEED);groups={}
    for r in rows:
        if r['subhalo_id'] in excluded:continue
        s=strata[r['subhalo_id']];r.update(mass_stratum=s[0],activity_stratum=s[1]);groups.setdefault(s,[]).append(r)
    keys=sorted(groups);extra=set(rng.sample(keys,19));selected=[];stratum_records=[]
    for s in keys:
        pool=sorted(groups[s],key=lambda r:r['subhalo_id']);n=4 if s in extra else 3
        assert len(pool)>=n
        stratum_records.append(dict(mass_stratum=s[0],activity_stratum=s[1],eligible_count=len(pool),selected_count=n,selection_probability=n/len(pool)))
        for r in rng.sample(pool,n):
            r.update(stratum_eligible_count=len(pool),stratum_selected_count=n,selection_probability=n/len(pool));selected.append(r)
    assert len(selected)==94
    rng.shuffle(selected)
    for i,r in enumerate(selected):
        role='development' if i<60 else ('validation' if i<74 else 'final_test')
        role_n={'development':60,'validation':14,'final_test':20}[role]
        r.update(partition=role,provenance='new',partition_probability_given_selected=role_n/94,
                 joint_selection_partition_probability=r['selection_probability']*role_n/94,
                 gas_fraction_proxy=r['gas_mass_Msun']/(r['gas_mass_Msun']+r['stellar_mass_Msun']),
                 gas_surface_density_proxy_Msun_pc2=r['gas_mass_Msun']/(2*math.pi*(1000*r['stellar_half_mass_radius_kpc'])**2))
    # Only official metadata from old inventory enter the manifest; image-derived columns are excluded.
    by_id={r['subhalo_id']:r for r in rows};allrows=[]
    for sid in sorted(old_ids):
        r=by_id[sid].copy();s=strata.get(sid,('',''));r.update(mass_stratum=s[0],activity_stratum=s[1],stratum_eligible_count='',stratum_selected_count='',selection_probability='',partition='development',provenance='existing',partition_probability_given_selected=1.0,joint_selection_partition_probability='',gas_fraction_proxy=r['gas_mass_Msun']/(r['gas_mass_Msun']+r['stellar_mass_Msun']),gas_surface_density_proxy_Msun_pc2=r['gas_mass_Msun']/(2*math.pi*(1000*r['stellar_half_mass_radius_kpc'])**2));allrows.append(r)
    allrows+=selected
    assert Counter(r['partition'] for r in allrows)=={'development':86,'validation':14,'final_test':20}
    write_csv(OUT/'galaxy_partitions.csv',allrows);write_csv(OUT/'strata.csv',stratum_records)
    for role in ['development','validation','final_test']:
        write_csv(OUT/(role+'_galaxies.csv'),[r for r in allrows if r['partition']==role])
    freeze={'frozen_utc':datetime.now(timezone.utc).isoformat(),'seed':SEED,'image_access_before_freeze':'none for all 94 new galaxies','old26_policy':'All previously inspected galaxies are development; previous held_out labels are retired because image analysis already occurred.','counts':dict(Counter(r['partition'] for r in allrows)),'partitions':{role:[r['subhalo_id'] for r in allrows if r['partition']==role] for role in ['development','validation','final_test']},'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.csv')}}
    (OUT/'partitions_frozen.json').write_text(json.dumps(freeze,indent=2)+'\n')
    manifest={'release':'TNG50-SKIRT DR1, TNG50-1 snapshot99','catalogue_url':'https://www.tng-project.org/files/data/baes24_tng50_skirt_atlas.txt','catalogue_sha256':hashlib.sha256((OLD/'baes24_tng50_skirt_atlas.txt').read_bytes()).hexdigest(),'selection_seed':SEED,'selection_method':'Existing official eligible-catalogue 5 mass quantiles x zero-SFR + 4 positive-sSFR quartiles; 19 randomly chosen strata get 4 new galaxies, 6 get 3. SRS without replacement within each stratum. Random partition of selected94 into60/14/20. No image-dependent selection.','excluded_ids':sorted(excluded),'local_archive_inventory':archives,'selected':selected,'strata':stratum_records,'partition_freeze_sha256':hashlib.sha256((OUT/'partitions_frozen.json').read_bytes()).hexdigest(),'limitations':'No catalogue dust mass, morphology class or true inclination. Gas fraction and gas surface-density proxies are metadata-derived; they are neither dust measurements nor morphology labels. Fixed old26 inclusion is conditional and historical, not assigned a population inclusion probability.'}
    (DATA/'selection_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'counts':freeze['counts'],'new':len(selected),'eligible':sum(len(x) for x in groups.values()),'excluded':len(excluded),'freeze_sha256':manifest['partition_freeze_sha256']}))

if __name__=='__main__':main()
