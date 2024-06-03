# # Understand PACE L1C Angle of Linear Polarization (AoLP)
#
#
# **Authors:** Meng Gao (NASA, SSAI), Riley Blocker (NASA, SSAI), James Allen (NASA, MSU), Kirk Knobelspiesse (NASA)
#
# > **PREREQUISITES**
# >
# > This notebook has the following prerequisites:
# > (to be updated if there is any)
#
# ## Summary
#
# PACE has two Multi-Angle Polarimeters (MAPs): [SPEXOne](https://pace.oceansciences.org/spexone.htm) and [HARP2](https://pace.oceansciences.org/harp2.htm). These sensors offer unique data, which is useful for its own scientific purposes and also complements the data from OCI. Working with data from the MAPs requires you to understand both multi-angle data and some basic concepts about polarization. This notebook will walk you through some basic understanding and visualizations on the Stokes vector, particular on the angle of linear polarization. 
#
# ## Learning objectives
#
# At the end of this notebook you will know:
#
# * How to define Stokes vector
# * How to define Angle of Linear Polarization (AoLP)
# * How to compute AoLP for HARP2 and SPEXone
#
# <a name="toc"></a>
# ## Contents
#
# (to be updated)
#

# ### Definitions

# #### Reference frame

# A proper reference frame is needed to specify the vibration direction of the electric component of the light field. We first define the scattering plane formed by the incident light and scattered light. Relative to the scattering plane, we can define a vector axis paralell the plane ($\hat{l}$), and a vector axis perpendicular to the plane ($\hat{r}$), and $\hat{r} \times \hat{l}$ specify the direction of the light propagation. 
#
# ![reference_frame](https://oceancolor.gsfc.nasa.gov/fileshare/meng_gao/images/pace_l1c_reference_frame.png "reference frame")
#
# As shown in the plot, the light is propagated into the screen. The electric vibration direction is specified by the dashed line. The angle of linear polarization (AoLP) is related to the $\hat{l}$ axis.
#
# Reference: 
# - Hansen 1974: Figure 2 (page 531)
# - Kattawar 1989: Figure 1 (page 1454)
# - Liou 2002: Figure 6.13 (page 318)

# #### Stokes vector

# We can specify the radiance (I) at different vibration direction as
# ![radiance_direction](https://oceancolor.gsfc.nasa.gov/fileshare/meng_gao/images/pace_l1c_stokes_vector.png "radiance_direction")
#
# The stokes vector for linearly polarized light can be defined as:
#
# - $I = I_{0} + I_{90} = I_{45}+I_{135}$
# - $Q = I_{0} - I_{90} $
# - $U = I_{45} - I_{135} $

# #### How to derive the AoLP

# A general electric field can be write as 
#
# $E = E_l + i E_r$, 
#
# we take $w = <E^2> $ therefore 
#
# $w= < (E_l + i E_r)^2 > = <E^2_l - E^2_r> + 2 i < E_l E_r> = Q + i U $ or $w = |w| \exp (2  i \gamma)$ 
#
# where AoLP can be derived as
#
# $\gamma = \frac{1}{2} tan^{-1} (U/Q)$

# Usually tan^{-1} output is defined within [-pi/2, pi/2], therefore AoLP is only defined within [-pi/4, pi/4], in order to define AoLP over the whole [-pi/2, pi/2] range, we adopt the common convention (Hansen and Travis, 1974) to select the value in the interval 0 ≤ AoLP ≤ π for which cos(2AoLP) has the same sign as Q. (PACE L1C document)
# Reference:
# - PACE L1C document: 
# https://pace.oceansciences.org/docs/NASA_TM2024219027v12_Level1C.pdf
# - Hansen and Travis 1974: https://pubs.giss.nasa.gov/docs/1974/1974_Hansen_ha09500o.pdf
#
# For consistency with the Stokes vector definition, we convert everything into the range of [0, pi] or [0$^\circ$, 180$^\circ$].  We also use radian and degree interchangably. 

# ### Numerical test

import numpy as np
import matplotlib.pyplot as plt

# Check tan value, we can see within [0, pi], tan value can be the same for at least two difference angles, therefore, actan is also not unique.

phiv=np.linspace(0, np.pi, 100)
#plt.plot(phiv*180/np.pi,np.tan(phiv))
plt.plot(phiv*180/np.pi,np.tan(2*phiv),'.')
plt.xlabel(r"angle ($^\circ$)")
plt.ylabel("Tan")


# ### formula

# +
def aolp_fun2(q, u):
    """return aolp in degree, arctan2 return arctan(u/q) 
    aolp within [0, 180] """
    aolp = 1/2*np.arctan2 (u, q) 
    aolp=np.where(aolp<0, aolp+np.pi, aolp)
    aolp *= 180/np.pi
    return aolp

def get_sign(aolp):
    return np.sign(np.cos(2*aolp*np.pi/180))


# -

# #### Case studies

q1, u1 = 1, 0
aolp1 = aolp_fun2(q1, u1)
aolp1, get_sign(aolp1), q1

q1, u1 = -1, 0
aolp1 = aolp_fun2(q1, u1)
aolp1, get_sign(aolp1),q1

q1, u1 = 0, 1
aolp1 = aolp_fun2(q1, u1)
aolp1, get_sign(aolp1),q1

q1, u1 = 0, -1
aolp1 = aolp_fun2(q1, u1)
aolp1, get_sign(aolp1), q1

# ### matrix test and sign convention

xv=np.linspace(-1,1,100)
yv=np.linspace(-1,1,100)
qv, uv= np.meshgrid(xv, yv, indexing='ij')
aolpv=aolp_fun2(qv, uv)
signv=get_sign(aolpv)

plt.figure(figsize=(15,3))
plt.subplot(141)
plt.title('Q')
plt.imshow(qv, cmap='jet')
plt.colorbar()
plt.subplot(142)
plt.title('U')
plt.imshow(uv, cmap='jet')
plt.colorbar()
plt.subplot(143)
plt.title('AOLP')
plt.imshow(aolpv, cmap='jet')
plt.colorbar()
plt.subplot(144)
plt.title('Q sign')
plt.imshow(signv, cmap='jet')
plt.colorbar()

# We can see that the sign derived from cos(2*aolp) agree with Q, and therefore agree with the convention. 


