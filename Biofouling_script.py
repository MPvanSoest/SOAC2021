# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 10:24:22 2021

@author: marle
"""

import numpy as np
import matplotlib.pyplot as plt

# constants
g = 9.81 # [m/s^2]


# model settings
dt = 60
nr_days = 30
len_t = int(nr_days*24*3600/dt)
t = np.arange(0,len_t*dt, dt)
drag = True

D = 999 # [m], depth of grid
dz = 1 # [m]
z = np.arange(-D, 1, dz)
z = np.flip(z)

# parameters
nu = 0.00109 # [N s/m^2], viscosity
rho_bf = 1388 # [kg/m^3], algae density
rho_pl = 950 # [kg/m^3], plastic density
rho_fo = 50 # [kg/m^3], plastic foam density

m_A = 0.39/(3600*24) # [/s], mortality rate
R_20 = 0.1/(3600*24) # [/s], respiration rate
Q_10 = 2 # [-], temperature coeff respiration

V_A = 2*10**(-16) # [m^3], volume per algae

# particle shapes
theta_p = np.zeros(4)
d_s = np.zeros(4)
d_n = np.zeros(4)
length_ratio = np.zeros(4)
A_p = np.zeros(4)
C_d = np.zeros(4)
axis_ratio = np.zeros(4)
K = np.zeros(4)

# sphere
R_s = 0.001 # [m], radius of particle
theta_p[0] = 4*np.pi*R_s**2 # [m^2], surface of particle
V_pl = 4/3*np.pi*R_s**3 # [m^3], plastic particle volume

A_p[0] = np.pi*R_s**2
C_d[0] = 0.47

d_s[0] = 2*R_s
d_n[0] = 2*R_s
length_ratio[0] = (2*R_s)**2/(np.pi*R_s**2)
axis_ratio[0] = 1
K[0] = 0.357 + 0.684*(d_s[0]/d_n[0]) + 0.00154*length_ratio[0] + 0.0104*axis_ratio[0]

# cilinder
R_c = (V_pl/(np.pi*20))**(1/3) # [m], radius
L_c = 20*R_c # [m], length of cilinder
theta_p[1] = 2*np.pi*R_c*L_c + 2*np.pi*R_c**2

A_p[1] = np.pi*R_c**2
C_d[1] = 0.82

d_s[1] = np.sqrt(2*(R_c*L_c+R_c**2))
d_n[1] = 2*R_c
length_ratio[1] = L_c**2/(np.pi*R_c**2)
axis_ratio[1] = 1
K[1] = 0.357 + 0.684*(d_s[1]/d_n[1]) + 0.00154*length_ratio[1] + 0.0104*axis_ratio[1]

# film (square)
D_fi = (V_pl/100)**(1/3)
L_fi = 10*D_fi
theta_p[2] = 2*L_fi**2 + 4*L_fi*D_fi

A_p[2] = L_fi**2
C_d[2] = 1.28

d_s[2] = 2*np.sqrt(1/(2*np.pi)*(L_fi**2+2*L_fi*D_fi))
d_n[2] = 2*np.sqrt(L_fi**2/np.pi)
length_ratio[2] = D_fi**2/(L_fi**2)
axis_ratio[2] = 1
K[2] = 0.357 + 0.684*(d_s[2]/d_n[2]) + 0.00154*length_ratio[2] + 0.0104*axis_ratio[2]

# foam (sphere)
R_fo = R_s
theta_p[3] = theta_p[0]

A_p[3] = np.pi*R_s**2
C_d[3] = 0.47

d_s[3] = d_s[0]
d_n[3] = d_n[0]
length_ratio[3] = length_ratio[0]
axis_ratio[3] = axis_ratio[0]
K[3] = K[0]

K = K * d_n/(2*R_s)

# Temperature profile
T_surf = 25     # Water temperature at the surface [degrees Celcius], for the North Pacific
T_bot  = 1.5    # Water temperature at the sea bottom [degrees Celcius], for the North Pacific
z_c    = -300   # Depth of the thermocline [m], for the North Pacific
p      =  2     # Parameter defining the steepness of the thermocline, for the North Pacific

T = T_surf + (T_bot - T_surf)*(z**p)/(z**p + z_c**p)

# Light profile
epsilon = 0.2
I_0 = 1.2e8 /(24*3600) # [mu E /m^2/s], light intensity at surface without day/night

I_fluc = I_0 * np.sin(2*np.pi*(t-6*(3600))/(3600*24))

I_fluc = np.where(I_fluc < 0, 0, I_fluc)

I = np.matmul(I_fluc.reshape((len(I_fluc),1)),np.exp(epsilon * z).reshape((1,len(z))))

# Density profile
a1 = 9.999e2
a2 = 2.034e-2
a3 = -6.162e-3
a4 = 2.261e-5
a5 = -4.657e-8

b1 = 8.020E2
b2 = -2.001
b3 = 1.677E-2
b4 = 2.261E-5
b5 = -4.657E-5 

# North Pacific
c1 = 9.998E-17 
c2 = 1.054E-12 
c3 = 3.997E-9 
c4 = 6.541E-6
c5 = 4.195E-3
c6 = 3.517E+1

# South Pacific
# c1 = -1.270E-17 
# c2 = -6.377E-14 
# c3 = 1.266E-10
# c4 = 1.082E-6
# c5 = 1.545E-3
# c6 = 3.410E+1

S = (c1*z**5 + c2*z**4 + c3*z**3 + c4*z**2 + c5*z + c6)/1000
rho_sw = (a1 + a2*T + a3*T**2 + a4*T**3 + a5*T**4) + (b1*S + b2*S*T + b3*S*T**2 + b4*S*T**3 + b5*S**2*T**2)

# Algae growth
T_min  = 0.2                        # Minimum temperatuer for algae growth [degrees Celcius]
T_max  = 33.3                       # Maximum temperature for algae growth [degrees Celcius]
T_opt  = 26.7                 
mu_max = 1.85/(3600*24)             # Maximum growth rate algae [per second]
I_opt  = 1.75392*10**13/(3600*24)   # Optimal light intensity algae growth [micro Einstein per m2 per second]
alpha  = 0.12/(3600*24)             # Initial slope [per second]

mu_opt = mu_max * I / (I + (mu_max/alpha) * ((I/I_opt)-1)**2)
phi = ((T-T_max)*(T-T_min)**2)/((T_opt-T_min)*((T_opt-T_min)*(T-T_opt)-(T_opt-T_max)*(T_opt+T_min-2*T)))

mu = mu_opt*phi

# mu[T.index(T < T_min or T > T_max)] = 0

indexmin = np.argwhere(T < T_min)
indexmax = np.argwhere(T > T_max)
mu[indexmin] = 0
mu[indexmax] = 0

#%%

# define matrices
w = np.zeros((len_t,len(theta_p)))
z_p = np.zeros((len_t,len(theta_p)))
rho_p = np.zeros((len_t,len(theta_p)))
A = np.zeros((len_t,len(theta_p)))
V_bf = np.zeros((len_t,len(theta_p)))
V_p = np.zeros((len_t,len(theta_p)))

# initial conditions
V_bf[0,:] = V_pl/10
A[0,:] = V_bf[0,:]/(V_A*theta_p[:])
V_p[0,:] = V_bf[0,:] + V_pl
w[0,:] = 0
z_p[0,:] = 0
rho_p[0,:] = (V_bf[0,:]*rho_bf + V_pl*rho_pl)/(V_p[0,:])
rho_p[0,3] = (V_bf[0,3]*rho_bf + V_pl*rho_fo)/(V_p[0,3]) # foam 

# integrate
for j in range(len(theta_p)):
    for i in range(len_t-1):
        index_p = abs(z - z_p[i,j]).argmin()
        
        dAdt = mu[int(t[i]/dt),index_p]*A[i,j] - m_A * A[i,j] - Q_10**((T[index_p]-20)/10) * R_20 * A[i,j]
        A[i+1,j] = A[i,j] + dAdt*dt
        
        V_bf[i+1,j] = V_A*A[i+1,j]*theta_p[j]
        V_p[i+1,j] = V_bf[i+1,j] + V_pl
        
        if j==3: #foam
            rho_p[i+1,j] = (V_bf[i+1,j]*rho_bf + V_pl*rho_fo)/(V_p[i+1,j])        
        else:
            rho_p[i+1,j] = (V_bf[i+1,j]*rho_bf + V_pl*rho_pl)/(V_p[i+1,j])
        
        R_p = (V_p[i+1,j]*(3/4)/np.pi)**(1/3) # equivalent sphere radius
        
        # w[i+1,j] = -np.sign(rho_p[i+1,j]-rho_sw[index_p])*np.sqrt(abs(V_p[i+1,j]*(rho_p[i+1,j]-rho_sw[index_p])*g/(0.5*rho_sw[index_p]*C_d[j]*A_p[j])))
        if drag == True:
           w[i+1,j] = -(2/9)*(rho_p[i+1,j]-rho_sw[index_p])/(nu*K[j])*g*R_p**2 # terminal velocity (Fg, Fb, Fd)
        else:
            w[i+1,j] = -(2/9)*(rho_p[i+1,j]-rho_sw[index_p])/(nu)*g*R_p**2 # terminal velocity (Fg, Fb, Fd)
        
        z_p[i+1,j] = z_p[i,j] + w[i+1,j]*dt
        
        if z_p[i+1,j] >= 0: # particle is at surface
            z_p[i+1,j] = 0
            w[i+1,j] = 0

#%% Plots

## Surface light fluctuation
plt.figure(figsize=(8,6))
plt.plot(t/(3600*24), I_fluc)
plt.xlim([25,30])
plt.ylabel('Light intensity [$\mu E /(m^{2}s)$]')
plt.xlabel('time [days]')
plt.title('Light intensity cycle at the surface (z=0)')
plt.savefig("surfacelight.png")
plt.show()

# Seawater temperature
plt.figure(figsize=(8,6))
plt.plot(T, z)
plt.xlabel('temperature [$\degree$ C]')
plt.ylabel('depth [m]')
plt.title('Temperature profile of the North-Pacific ocean')
plt.savefig("temp_NP.png")
plt.show()

# Seawater salinity
plt.figure(figsize=(8,6))
plt.plot(S*1000, z)
plt.xlabel('salinity [g/kg]')
plt.ylabel('depth [m]')
plt.title('Salinity profile of the North-Pacific ocean')
plt.savefig("salinity_NP.png")
plt.show()
  		
# Seawater density
plt.figure(figsize=(8,6))
plt.plot(rho_sw, z)
plt.xlabel('seawater density [kg/m^3]')
plt.ylabel('depth [m]')
plt.title('Density profile of the North-Pacific ocean')
plt.savefig("density_NP.png")
plt.show()

#%%
## Particle depth
plt.figure(figsize=(8,6))
plt.plot(t/(3600*24), z_p[:,0], label='sphere')
plt.xlim([25,30])
plt.xlabel('time (days)')
plt.ylabel('depth [m]')
plt.legend()
plt.title('Plastic particle oscillation, shape-dependant drag = '+ str(drag))
plt.savefig("part_dep.png")
plt.show()

plt.figure(figsize=(8,6))
plt.plot(t/(3600*24), z_p[:,1], label='cylinder')
plt.xlim([25,30])
plt.xlabel('time (days)')
plt.ylabel('depth [m]')
plt.legend()
plt.title('Plastic particle oscillation, shape-dependant drag = '+ str(drag)) #', R = '+ str(R) + ' m')
plt.savefig("part_dep.png")
plt.show()

plt.figure(figsize=(8,6))
plt.plot(t/(3600*24), z_p[:,2], label='film')
plt.xlim([25,30])
plt.xlabel('time (days)')
plt.ylabel('depth [m]')
plt.legend()
plt.title('Plastic particle oscillation, shape-dependant drag = '+ str(drag)) #', R = '+ str(R) + ' m')
plt.savefig("part_dep.png")
plt.show()

plt.figure(figsize=(8,6))
plt.plot(t/(3600*24), z_p[:,3], label='foam')
plt.xlim([25,30])
plt.xlabel('time (days)')
plt.ylabel('depth [m]')
plt.legend()
plt.title('Plastic particle oscillation, shape-dependant drag = '+ str(drag)) #', R = '+ str(R) + ' m')
plt.savefig("part_dep.png")
plt.show()

#%%
## Particle depth
plt.figure(figsize=(8,6))
plt.plot(t/(3600*24), z_p[:,0], label='sphere')
plt.plot(t/(3600*24), z_p[:,1], label='cylinder')
plt.plot(t/(3600*24), z_p[:,2], label='film')
plt.plot(t/(3600*24), z_p[:,3], label='foam')
plt.xlim([25,30])
plt.xlabel('time (days)')
plt.ylabel('depth [m]')
plt.legend()
plt.title('Plastic particle oscillation, shape-dependant drag = '+ str(drag)) #', R = '+ str(R) + ' m')
plt.savefig("part_dep.png")
plt.show()
#%%

## Particle density
plt.figure(figsize=(8,6))
plt.plot(t/(3600*24), rho_p[:,0], label='sphere')
plt.plot(t/(3600*24), rho_p[:,1], label='cylinder')
plt.plot(t/(3600*24), rho_p[:,2], label='film')
plt.plot(t/(3600*24), rho_p[:,3], label='foam')
plt.xlim([25,30])
plt.ylim([950,np.max(rho_p)+10])
plt.xlabel('time (days)')
plt.ylabel('density [$kg/m^{3}]$')
plt.legend()
plt.title('Plastic particle density during oscillation')
plt.savefig("part_dens.png")
plt.show()

## Particle velocity
plt.figure(figsize=(8,6))
plt.plot(t/(3600*24), w[:,0], label='sphere')
plt.plot(t/(3600*24), w[:,1], label='cylinder')
plt.plot(t/(3600*24), w[:,2], label='film')
plt.plot(t/(3600*24), w[:,3], label='foam')
plt.xlim([25,30])
plt.xlabel('time (days)')
plt.ylabel('velocity [m/s]')
plt.legend()
plt.title('Plastic particle velocity during oscillation')
plt.savefig("part_vel.png")
plt.show()

