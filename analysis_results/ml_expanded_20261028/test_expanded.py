"""Scientific gates: paired operators, no target leakage, grouped partitions."""
import unittest
import inspect
import numpy as np
import pandas as pd
from expanded_features import O,PREV,SOURCE,TARGETS,geometry,aperture_policy,labels_for,old
from expanded_models import columns,model


class ScientificGates(unittest.TestCase):
    def test_uniform_screen_and_negative_ratios(self):
        axis=(np.arange(800)+.5-400)*.1;y,x=np.meshgrid(axis,axis,indexing='ij')
        image=np.exp(-(x*x+y*y)/8)
        clear=np.array([image,.8*image,.6*image]);dusty=clear*.5
        radius,_=aperture_policy(dusty)
        values=labels_for(clear,dusty,radius)
        self.assertAlmostEqual(values['A_g'],-2.5*np.log10(.5),places=10)
        self.assertAlmostEqual(values['A_g_IQR_1kpc'],0.,places=10)
        for target in ['dR50_g','dR50_Ks','dC_g','dC_Ks']:self.assertAlmostEqual(values[target],0.,places=10)
        self.assertLess(labels_for(clear,clear*1.1,radius)['A_g'],0)
        self.assertEqual(list(inspect.signature(aperture_policy).parameters),['dusty'])

    def test_large_render_reproduces_old_central_field(self):
        with np.load(O/'data_audit/cache/294866/O1.npz') as a:
            images=np.array([a['dusty_'+b] for b in SOURCE],dtype=float)
        large_g=geometry('glao');large,loss=old.p.render(images,large_g)
        small_g=old.p.make_geometry(.1,'glao');small,_=old.p.render(images[:,200:600,200:600],small_g)
        start=(large.shape[-1]-small.shape[-1])//2
        center=large[:,start:start+small.shape[-1],start:start+small.shape[-1]]
        np.testing.assert_allclose(center,small,atol=1e-9,rtol=1e-10)
        self.assertLess(loss,1e-5)

    def test_predictor_columns_exclude_truth_and_metadata(self):
        forbidden=['clear','dust_mass','stellar_mass','subhalo','SFR','truth','prediction','target','partition']
        for scenario in ['optical','seeing_NIR','GLAO_NIR']:
            for family in ['median','screen','phot_ridge','summary_ridge','spatial_ridge','spatial_forest','spatial_boost']:
                base,cells=columns(scenario,family)
                self.assertTrue(all(not any(token in name for token in forbidden) for name in base+cells))
                self.assertFalse(set(base+cells)&set(TARGETS))

    def test_test_truth_does_not_change_predictions(self):
        inputs=[];labels=[]
        for sid in [294866,571633,578834]:
            inputs.append(pd.read_csv(O/'derived'/str(sid)/'features.csv.gz'))
            labels.append(pd.read_csv(O/'derived'/str(sid)/'labels.csv'))
        features=pd.concat(inputs);targets=pd.concat(labels)
        features=features[(features.aperture=='adaptive')&(features.condition=='nominal')&(features['mode']=='glao')]
        data=features.merge(targets,on=['subhalo_id','view','partition','aperture'],validate='many_to_one')
        train=data[data.subhalo_id!=578834];test=data[data.subhalo_id==578834]
        fitted=model(dict(family='spatial_ridge',value=10),'GLAO_NIR');fitted.fit(train,train[TARGETS])
        pred=fitted.predict(test)
        changed=test.copy();changed[TARGETS]+=1000
        np.testing.assert_array_equal(pred,fitted.predict(changed))


if __name__=='__main__':unittest.main()
