# %% [markdown]
# # Distribution of vegetation in a landscape of heterogeneous predation risk

# %%
# importing libraries

import numpy as np
from matplotlib import pyplot as plt
import math
from itertools import permutations as perm
import time
from matplotlib import animation as animate
import ray
from numba import njit

# initialising ray cluster

ray.init(dashboard_port=8265)

# Notebook parameters

plt.rcParams['figure.figsize'] = [8, 8]
plt.rcParams['font.size'] = 30

# %% [markdown]
# ## Defining initialisation functions

# %%
# Defining resource matrix

def veg(N):

    # Starting with resoource available everywhere

    V = np.full((N, N), 1)

    return V

# Creating list of fish in the landscape

def fish_vec(n, N):

    # n = initial number of fish
    # N = size of the landscape

    # Iniital position at the center

    x = int(N/2)
    y = int(N/2)

    # Data for a single fish

    fish = np.array((x, y, 0))  # [(position), starvation time]

    fish_pop = np.full((n, 3), fish)

    return fish_pop

# Converting fish population to matrix

@njit(parallel = True)
def fish_mat(fish, N, T_max):

    # creating an empty matrix for fish

    cat = np.zeros((N, N, T_max))

    for t in range(T_max):

        # Extracting fish positioins

        fish_pop = fish[t]

        # Summing number of fish in each cell

        for index, value in np.ndenumerate(cat):

            for f in fish_pop:

                if index == (f[0], f[1], t):

                    cat[index] += 1

    return cat

# Function to caluclate risk as a function of distance

def risk_fun(dist, k=0.5, a=12.5):

    return (1/(1 + math.exp(-(dist-a)*k)))

    # return 1/(a + math.exp((25 - dist)*k))

# Function to calculate risk based on position

def risk(ix, iy, N=50, k=0.5, a=20):

    # Distance based change from the center

    center = N/2

    dist = ((center - ix)**2 + (center - iy)**2)**0.5

    alpha = risk_fun(dist, k=k, a=a)

    return alpha

# %% [markdown]
# ## Defining update functions

# %%
# Periodic boundaries

def pbound(pt, N):

    if pt >= N-1:

        return(abs(pt - N))

    elif pt < 0:

        return(abs(pt + N))

    else:

        return(pt)

# test


pbound(50, 50)


# spread and regeneration of vegetation

def veg_update(veg_mat, v=0.1):

    N = np.shape(veg_mat)  # getting shape of vegetation matrix

    for index, value in np.ndenumerate(veg_mat):

        if value == 0:

            adj = []  # empty list of adjascent cells

            # getting list of adjascent cells

            for dx in [-1, 0, 1]:

                for dy in [-1, 0, 1]:

                    x = index[0] + dx  # horizontal

                    y = index[1] + dy  # vertical

                    # Periodic boundaries

                    x = pbound(x, 50)
                    y = pbound(y, 50)

                    adj.append((x, y))

            # Spread of vegetation

            # Getting values from adjascent cells

            adj_veg = []

            for cell in adj:

                adj_veg.append(veg_mat[cell])

            # checking if neighbours are present

            if sum(adj_veg) > 0:

                # updating value

                veg_mat[index] = int(np.random.choice(
                    a=[0, 1], p=[1-v, v]))  # prob of reproducing

    return(veg_mat)



# updating fish positions

def fish_mov(fish_pop, N=50, k=0.5, a=20):

    index = 0

    for f in fish_pop:

        x = f[0]
        y = f[1]

        # Calculating risk

        xrisk = (risk(x+1, y, N, k=k, a=a) - risk(x-1, y, N, k=k, a=a))
        yrisk = (risk(x, y+1, N, k=k, a=a) - risk(x, y-1, N, k=k, a=a))

        # Calculating moves based on risk

        px = 0.5 - xrisk  # Risk of moving right vs left
        py = 0.5 - yrisk  # risk of moving up vs down

        # 2 - D risk - biased random walk

        dx = x + np.random.choice(a=[-1, 1], p=[(1-px), px])
        dy = y + np.random.choice(a=[-1, 1], p=[(1-py), py])

        # Periodic boundaries

        dx = pbound(dx, 50)

        dy = pbound(dy, 50)

        fish_pop[index,0] = dx
        fish_pop[index,1] = dy

        index += 1

    return fish_pop


# Fish reproduction

def fish_rep(fish_pop, r=0.01):

    for f in fish_pop:

        rep = np.random.choice(a=[0, 1], p=[1-r, r])  # P(reproduce)

        if rep == 1:

            f[2] = 0  # resetting starvation clock

            fish_pop = np.append(fish_pop, [f], axis=0)

    return fish_pop


# Fish starvation

def fish_starve(fish_pop):

    index = 0

    idx = []

    for f in fish_pop:

        # At t_S = 10, fish dies

        if f[2] == 10:

            idx.append(index)

        else:

            # Starvation clock increases with each time step

            fish_pop[index, 2] = fish_pop[index, 2] + 1

        index += 1

    # Killing fish

    fish_pop = np.delete(fish_pop, idx, axis=0)

    return fish_pop


# Fish feeding

def fish_feed(fish_pop, veg_mat, q=5):

    index = 0

    for f in fish_pop:

        # Check if vegetation is present

        if veg_mat[f[0], f[1]] == 1:

            # Fish eats the vegetations

            # Veg disappears

            veg_mat[f[0], f[1]] = 0

            # Fish starvation clock starts over

            fish_pop[index, 2] = fish_pop[index, 2] - q

        index += 1

    return veg_mat, fish_pop


# Simulation function

T_max = 500


@ray.remote(num_returns=2)
def fish_sim(n=20, N=50, T_max=500, v=0.1, k=0.5, a=20, r=0.01, q=5):
    """
    n = initial number of fish
    N = size of the matrix
    T_max = maximum time to simulate
    v = vegetation growth rate
    k = slope of risk function
    a = half saturation distance for risk function
    r = fish reproduction rate
    q = feed gain for fish
    """

    # Initialising the landscape

    fish_pop = fish_vec(n, N)  # fish population
    veg_mat = veg(N)  # resource matrix

    # Results

    veg_res = np.zeros((N, N, T_max+2))  # resource
    veg_res[:, :, 0] = veg_mat  # initial conditions

    fish_res = [fish_vec(20, 50) for t in range(T_max+2)]  # fish
    fish_res[0] = fish_pop  # initial conditions

    for t in range(T_max):

        # Updating resource values

        veg_mat = veg_update(veg_mat, v=v)

        # Fish feeding

        veg_mat, fish_pop = fish_feed(fish_pop, veg_mat, q=q)

        # Fish starvation and death

        fish_pop = fish_starve(fish_pop)

        # Fish reproduce

        fish_pop = fish_rep(fish_pop, r=r)

        # Fish movement

        fish_pop = fish_mov(fish_pop, N=N, k=k, a=a)

        # Logging fish abundance

        fish_res[t+1] = fish_pop

        # Logging resource

        veg_res[:, :, t+1] = veg_mat

    return fish_res, veg_res


# %%
# Extracting abundance from matrix

@njit(parallel = True)
def abn(mat, T_max=500):
    """ mat is 2-D simulation result across time (3-D array)"""

    res = [0]*T_max

    for t in range(T_max):

        res[t] = np.sum(mat[:, :, t])

    return res


# mean distance travelled by fish

@njit()
def movement(mat, N = 50, T_max = 500):
    
    c = N/2 #center

    mean_dist = [0]*(T_max)

    var_dist = [0]*(T_max)

    for t in range(T_max):

        abn = np.sum(mat[:,:,t])

        dist = np.zeros(int(abn))

        ind = 0

        for index, value in np.ndenumerate(mat[:,:,t]):

            if value > 0: # checking for presence of fish 

                # distance of each element from center

                for _ in range(int(value)):

                    dist[ind] = ((c - index[0])**2 + (c - index[1])**2)**0.5

                    ind += 1

            mean_dist[t] = np.mean(dist)
            var_dist[t] = np.var(dist)
    
    return mean_dist, var_dist


# %%
# Animating fish movement in the landscape

def lilly(slice):

    plt.clf()
    plt.imshow(fish_res[:, :, slice])
    plt.colorbar()
    plt.title(f"At time = {slice}")
    plt.clim(0, 5)


#anim = animate.FuncAnimation(plt.figure(), lilly, range(T_max), interval=100)

#anim.save("sim1.gif")
