import unittest
import numpy as np
import physical_model as p
class Tests(unittest.TestCase):
 def test_positive_and_nested(self):
  m=p.ForwardModel('seeing');q=m.initial();f,j=m.predict(q,False,True);self.assertTrue((f>0).all())
  qv=np.r_[q,np.zeros(m.nspatial-1)];np.testing.assert_allclose(f,m.predict(qv,True),rtol=1e-12)
 def test_forward_adjoint(self):
  m=p.ForwardModel('seeing');image=np.ones((7,400,400));rate,_=p.e.render(image,.3,m.g)
  mu=np.array([np.einsum('ayx,yx->a',w,r) for w,r in zip(m.g['weights'],rate)])
  unit=np.einsum('ban,n->ba',m.response,np.ones(m.ncell));np.testing.assert_allclose(unit,mu,rtol=3e-8,atol=1e-9)
 def test_derivative(self):
  m=p.ForwardModel('seeing');q=np.r_[m.initial(),np.zeros(m.nspatial-1)];f,j=m.predict(q,True,True)
  for i in [0,m.ngray//2,m.ngray,m.ngray+1,len(q)-2]:
   a=q.copy();b=q.copy();a[i]+=1e-5;b[i]-=1e-5;fd=(m.predict(a,True)-m.predict(b,True))/2e-5
   np.testing.assert_allclose(j[:,i],fd,rtol=3e-5,atol=3e-6)
 def test_training_regions(self):
  t=np.load(p.O/'stellar_training.npz');self.assertTrue((t['xy'][:,0]<-4).all());self.assertTrue((t['templates']>0).all())
 def test_structured_operator(self):
  m=p.ForwardModel('seeing');rng=np.random.default_rng(1714);cells=rng.uniform(.01,1,(7,40,40));image=cells.repeat(10,axis=1).repeat(10,axis=2)
  rate,_=p.e.render(image,.3,m.g);direct=np.array([np.einsum('ayx,yx->a',w,r) for w,r in zip(m.g['weights'],rate)])
  indirect=np.einsum('ban,bn->ba',m.response,cells.reshape(7,-1));np.testing.assert_allclose(direct,indirect,rtol=1e-9,atol=1e-8)
 def test_absolute_information(self):
  m=p.ForwardModel('seeing');q=m.initial();a=m.predict(q,False).reshape(7,15);q[-1]+=1;b=m.predict(q,False).reshape(7,15)
  np.testing.assert_allclose(a/a.mean(axis=1)[:,None],b/b.mean(axis=1)[:,None],atol=1e-14);self.assertGreater(np.linalg.norm(a-b)/np.linalg.norm(a),.1)
if __name__=='__main__':unittest.main()
