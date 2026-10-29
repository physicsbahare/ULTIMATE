"""Fixed-origin circular-aperture morphology; no truth images in measurement API."""
import numpy as np
class Geometry:
 def __init__(self,n,pixel,radius,cx=0.,cy=0.):
  axis=(np.arange(n)+.5-n/2)*pixel
  self.y,self.x=np.meshgrid(axis-cy,axis-cx,indexing='ij')
  self.r=np.hypot(self.x,self.y);self.mask=self.r<radius
  self.order=np.argsort(self.r[self.mask]);self.sorted_r=self.r[self.mask][self.order]
  self.xx=self.x[self.mask];self.yy=self.y[self.mask]
  self.shift=(int(round(2*cy/pixel)),int(round(2*cx/pixel)))
  assert abs(2*cx/pixel-self.shift[1])<1e-8 and abs(2*cy/pixel-self.shift[0])<1e-8

def measure(image,g,variance=None):
 f=np.asarray(image)[g.mask].astype(float);total=f.sum()
 out={k:np.nan for k in ['R20','R50','R80','C','A','q']};out['flux']=float(total)
 if total<=0 or not np.isfinite(f).all():return out
 cum=np.cumsum(f[g.order]);radii=[]
 for frac in [.2,.5,.8]:
  hit=np.flatnonzero(cum>=frac*total);radii.append(g.sorted_r[hit[0]] if len(hit) else np.nan)
 out.update(dict(zip(['R20','R50','R80'],radii)))
 if radii[0]>0:out['C']=5*np.log10(radii[2]/radii[0])
 rot=np.roll(image[::-1,::-1],g.shift,axis=(0,1));resid=np.abs(image-rot)
 if variance is not None:
  vr=np.roll(variance[::-1,::-1],g.shift,axis=(0,1));resid=resid-np.sqrt(2/np.pi)*np.sqrt(variance+vr)
 out['A']=float(resid[g.mask].sum()/total)
 m=np.array([[np.dot(f,g.xx**2),np.dot(f,g.xx*g.yy)],[np.dot(f,g.xx*g.yy),np.dot(f,g.yy**2)]])/total
 ev=np.linalg.eigvalsh(m)
 if np.all(ev>0):out['q']=float(np.sqrt(ev[0]/ev[1]))
 return out
