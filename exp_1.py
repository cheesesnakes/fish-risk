# importing set up script

exec(open('setup.py').read())

# Testing stability as a function of input rate and reproduction rate in the absence of predation

# %%
# varying distance and exponent of risk function

# Defining simulation parameters

T_max = 1000  # time for the simulation
N = 50  # length of side for N x N matrix
n = 20  # initial number of fish

v = list(np.arange(0.01, 0.1, 0.01))
r = list(np.arange(0.01, 0.1, 0.01))

iter = 1

# Results matrices

sim_fish_0 = [0]*len(r)*len(v)*iter  # np.zeros((len(k), len(a)))
sim_veg_0 = [0]*len(r)*len(v)*iter  # np.zeros((len(k), len(a)))

x = 0  # ray sync

for i in range(len(v)):

    for j in range(len(r)):

        for rep in range(iter):

            sim_fish_0[x], sim_veg_0[x] = fish_sim.remote(N=N, T_max=T_max, a=100, v = v[i], r = r[j])

            x += 1

# Retrieving ray futures

fish_res_0 = ray.get(sim_fish_0)
veg_res_0 = ray.get(sim_veg_0)


# %%
# Extracting metrics
v = list(np.arange(0.01, 0.1, 0.01))
r = list(np.arange(0.01, 0.1, 0.01))

fish_abn_0 = np.zeros((len(r), len(v), iter, T_max))
veg_abn_0 = np.zeros((len(r), len(v), iter, T_max))

x = 0

for i in range(len(v)):

    for j in range(len(r)):

        for z in range(iter):
            
            fish_mat_0 = fish_mat(fish_res_0[x], N, T_max)
            
            # abundance

            fish_abn_0[i, j, z] = abn(fish_mat_0, T_max) #fish

            veg_abn_0[i, j, z] = abn(veg_res_0[x], T_max) #resource

            
            x += 1


# %%
plt.imshow(fish_abn_0[:,:,:,T_max-1], extent=[0.01, 0.09, 0.09, 0.01])
plt.xlabel('Fish reproductive rate (r)')
plt.ylabel('Resource input rate (v)')
plt.colorbar()

plt.savefig('fig6_1.png')


# %%
plt.imshow(veg_abn_0[:,:,:,T_max-1], extent=[0.01, 0.09, 0.09, 0.01])
plt.xlabel('Fish reproductive rate (r)')
plt.ylabel('Resource input rate (v)')
plt.colorbar()

plt.savefig('fig6_2.png')
