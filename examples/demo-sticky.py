from __future__ import division

import numpy as np
from matplotlib import pyplot as plt
plt.ion()

import pyhsmm
from pyhsmm.util.text import progprint_xrange

import autoregressive.models as m
import autoregressive.distributions as d

###################
#  generate data  #
###################

a = d.AR_MNIW(nu_0=10,S_0=np.eye(2),M_0=np.zeros((2,4)),Kinv_0=np.eye(4))
a.A = np.hstack((-np.eye(2),2*np.eye(2)))

b = d.AR_MNIW(nu_0=10,S_0=np.eye(2),M_0=np.zeros((2,4)),Kinv_0=np.eye(4))
b.A = np.array([[np.cos(np.pi/6),-np.sin(np.pi/6)],[np.sin(np.pi/6),np.cos(np.pi/6)]]).dot(np.hstack((-np.eye(2),np.eye(2)))) + np.hstack((np.zeros((2,2)),np.eye(2)))

c = d.AR_MNIW(nu_0=10,S_0=np.eye(2),M_0=np.zeros((2,4)),Kinv_0=np.eye(4))
c.A = np.array([[np.cos(-np.pi/6),-np.sin(-np.pi/6)],[np.sin(-np.pi/6),np.cos(-np.pi/6)]]).dot(np.hstack((-np.eye(2),np.eye(2)))) + np.hstack((np.zeros((2,2)),np.eye(2)))


data = np.array([0,2]).repeat(2).reshape((2,2))
distns = [a,b,c]
for i in range(9):
    data = np.concatenate((data,distns[i % len(distns)].rvs(prefix=data[-2:],length=30)))

plt.figure()
plt.plot(data[:,0],data[:,1],'bx-')

##################
#  create model  #
##################


Nmax = 20
model = m.ARWeakLimitStickyHDPHMM(
        nlags=2,
        kappa=100.,
        alpha=4.,gamma=4.,init_state_concentration=10.,
        obs_distns=[d.AR_MNIW(nu_0=3,S_0=np.eye(2),M_0=np.zeros((2,4)),Kinv_0=np.eye(4)) for state in range(Nmax)],
        )

model.add_data(data,trunc=50)

###############
#  inference  #
###############

for itr in progprint_xrange(100):
    model.resample_model()

plt.figure()
model.plot()

plt.figure()
colors = ['b','r','y','k','g']
stateseq = model.states_list[0].stateseq
for i,s in enumerate(np.unique(stateseq)):
    plt.plot(data[s==stateseq,0],data[s==stateseq,1],colors[i % len(colors)] + 'o')

print model.heldout_viterbi(data)
print model.heldout_state_marginals(data)
