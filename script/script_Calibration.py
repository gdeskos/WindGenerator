import sys
sys.path.append('../')
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

import matplotlib.pyplot as plt
from pylab import *
import pickle
from math import log

from torch.nn import parameter

from source.Calibration import CalibrationProblem
from source.DataGenerator import OnePointSpectraDataGenerator

####################################
### Configuration
####################################

config = {
    'type_EddyLifetime' :   'tauNet',  ### 'const', TwoThird', 'Mann', 'tauNet'
    'type_PowerSpectra' :   'RDT', ### 'RDT', 'zetaNet', 'C3Net', 'Corrector'
    'nlayers'           :   2,
    'hidden_layer_size' :   10,
    # 'nModes'            :   5, ### number of modes in the rational function in tauNet ### deprecated
    'learn_nu'          :   False, ### NOTE: Experiment 1: False, Experiment 2: True
    'plt_tau'           :   True,
    'tol'               :   1.e-3, ### not important
    'lr'                :   1,     ### learning rate
    'penalty'           :   1.e-1,
    'regularization'    :   1.e-1,
    'nepochs'           :   200,
    'curves'            :   [0,1,2,3],
    'data_type'         :   'IEC_KSEC', ### 'Kaimal', 'SimiuScanlan', 'SimiuYeo', 'iso'
    'Vhub'              :   10, # m/s
    'zhub'              :   150, #m
    'sigma1'            :   1.834,
    'Lambda1'           :   42,
    'domain'            :   np.logspace(-1, 2, 20), ### NOTE: Experiment 1: np.logspace(-1, 2, 20), Experiment 2: np.logspace(-2, 2, 40)
    'noisy_data'        :   0*3.e-1, ### level of the data noise  ### NOTE: Experiment 1: zero, Experiment 2: non-zero
    'output_folder'     :   '/Users/gdeskos/WindGenerator/data/'
}
pb = CalibrationProblem(**config)


####################################
### Initialize Parameters
####################################

#Calculating turbulence parameters according to IEC standards
# we assume a hub height z=150m corresponding to the IEA 15MW wind turbine hub height
zhub=150; # Hub height in meters
Vhub=10.; # Average Hub height velocity in m/s
Iref = 0.14
sigma1=Iref*(0.75*Vhub+5.6)
Lambda1=42; # Longitudinal turbulence scale parameter at hub height

print(sigma1, Lambda1)

#Mann model parameters
Gamma = 3.9
sigma = 0.55*sigma1
L=0.8*Lambda1;

parameters = pb.parameters
parameters[:3] = [log(L), log(Gamma), log(sigma)]
pb.parameters = parameters[:len(pb.parameters)]
pb.print_parameters()

####################################
### Initialize Data
####################################

k1_data_pts = config['domain'] #np.logspace(-1, 2, 20)
DataPoints  = [ (k1, 1) for k1 in k1_data_pts ]
Data = OnePointSpectraDataGenerator(DataPoints=DataPoints, **config).Data

### Data perturbation
data_noise_magnitude = config['noisy_data']
if data_noise_magnitude:
    Data[1][:] *= np.exp(np.random.normal(loc=0, scale=data_noise_magnitude, size=Data[1].shape))

DataValues = Data[1]

####################################
### Just plot
####################################

kF = pb.eval(k1_data_pts)

for i in range(3):
    plt.plot(k1_data_pts, kF[i], 'o-', label=r'$F_{0:d}$ model'.format(i+1))
for i in range(3):
    plt.plot(k1_data_pts, DataValues[:,i,i], '--')#, label=r'$F_{0:d}$ data'.format(i+1))
plt.plot(k1_data_pts, -kF[3], 'o-', label=r'-$F_{13}$ model')
plt.plot(k1_data_pts, -DataValues[:,0,2], '--', label=r'$-F_{13}$ data')
plt.xscale('log')
plt.yscale('log')
plt.xlabel(r'$k_1$')
plt.ylabel(r'$k_1 F(k_1)/u_\ast^2$')
plt.legend()
plt.grid(which='both')
plt.show()

####################################
### Calibrate
####################################
#opt_params = pb.calibrate(Data=Data, **config)#, OptimizerClass=torch.optim.RMSprop)

####################################
### Export
####################################
#if 'opt_params' not in locals():
#    opt_params = pb.parameters
#filename = config['output_folder'] + config['type_EddyLifetime'] + '_' + config['data_type'] + '.pkl'
#with open(filename, 'wb') as file:
#    pickle.dump([config, opt_params, Data, pb.loss_history_total, pb.loss_history_epochs], file)
