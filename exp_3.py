# %% 
# importing set up script

exec(open('setup.py').read())

# Varying input rate with and without predation pressure

# %%
# varying distance and exponent of risk function

# Defining simulation parameters

T_max = 1000  # time for the simulation
N = 50  # length of side for N x N matrix
n = 20  # initial number of fish

k = [1, 0.5, 0.25, 0.125]  # exponent

a = 20 # half saturation distance

v = np.arange(0.1, 1, 0.1) # vegetation input rate

iter = 10

# Results matrices

sim_fish_2 = [0]*len(k)*len(v)*iter  # np.zeros((len(k), len(a)))
sim_veg_2 = [0]*len(k)*len(v)*iter  # np.zeros((len(k), len(a)))

x = 0  # ray sync

for i in range(len(k)):

    for j in range(len(v)):

        for rep in range(iter):

            sim_fish_2[x], sim_veg_2[x] = fish_sim.remote(N=N, T_max=T_max, k=k[i], v=v[j], a = a)

            x += 1

# Retrieving ray futures

fish_res_2 = ray.get(sim_fish_2)
veg_res_2 = ray.get(sim_veg_2)


# %%
# Extracting metrics

fish_abn_2 = np.zeros((len(k), len(a), iter, T_max))
veg_abn_2 = np.zeros((len(k), len(a), iter, T_max))
mean_dist_2 = np.zeros((len(k), len(a), iter, T_max))
var_dist_2 = np.zeros((len(k), len(a), iter, T_max))

x = 0

for i in range(len(k)):

    for j in range(len(a)):

        for r in range(iter):
            
            fish_mat_2 = fish_mat(fish_res_2[x], N, T_max)

            # abundance

            fish_abn_2[i, j, r] = abn(fish_mat_2, T_max) #fish

            veg_abn_2[i, j, r] = abn(veg_res_2[x], T_max) #resource

            # movement

            mean_dist_2[i, j, r], var_dist_2[i, j, r] = movement(fish_mat_2, T_max = T_max)

            x += 1


# %%
k = [1, 0.5, 0.25, 0.125]  # exponent

v = np.arange(0.1, 1, 0.1) # vegetation input rate

plt.rcParams['font.size'] = '15'

fig, axis = plt.subplots(1,2, figsize = (16,8))
veg_eq_2 = np.zeros((len(k), len(v)))
veg_var_2 = np.zeros((len(k), len(v)))

for i in range(len(k)):

    for j in range(len(v)):

        veg_eq_2[i, j] = np.mean(veg_abn_2[i, j, :, (T_max-100):(T_max-1)])
        veg_var_2[i, j] = np.var(veg_abn_2[i, j, :, (T_max-100):(T_max-1)])

    axis[0].scatter(v, veg_eq_2[i, :], label=k[i])
    axis[0].plot(v, veg_eq_2[i, :])

    axis[1].scatter(v, veg_var_2[i, :], label=k[i])
    axis[1].plot(v, veg_var_2[i, :])

axis[0].set_xlabel('Vegetation input rate (v)')
axis[0].set_ylabel('Vegetation abundance')
#plt.errorbar(a, veg_eq[i,:], label = k[i], yerr = veg_var[i,:], fmt='o')
axis[1].set_xlabel('Vegetation input rate (v)')
axis[1].set_ylabel('Variance')
axis[1].legend(title = 'Risk Gradient (k)')

plt.savefig('fig2.png')


# %%
fish_eq_2 = np.zeros((len(k), len(v)))
fish_var_2 = np.zeros((len(k), len(v)))

for i in range(len(k)):

    for j in range(len(v)):

        fish_eq_2[i, j] = np.mean(fish_abn_2[i, j, :, (T_max-100):(T_max-1)])
        fish_var_2[i, j] = np.var(fish_abn_2[i, j, :, (T_max-100):(T_max-1)])

    plt.scatter(v, fish_eq_2[i, :], label=k[i])
    plt.plot(v, fish_eq_2[i, :])
    plt.legend()

# %% [markdown]
# ## Experiment 3
# 
# Varying predation gradient

# %%
# varying distance and exponent of risk function

# Defining simulation parameters

T_max = 1000  # time for the simulation
N = 50  # length of side for N x N matrix
n = 20  # initial number of fish

k = 0.5  # exponent

a = list(range(0, 100, 20)) # half saturation distance

v = np.arange(0.1, 1, 0.1) # vegetation input rate

iter = 10

# Results matrices

sim_fish_3 = [0]*len(k)*len(a)*iter  # np.zeros((len(k), len(a)))
sim_veg_3 = [0]*len(k)*len(a)*iter  # np.zeros((len(k), len(a)))

x = 0  # ray sync

for i in range(len(a)):

    for j in range(len(v)):

        for rep in range(iter):

            sim_fish_3[x], sim_veg_3[x] = fish_sim.remote(N=N, T_max=T_max, k=k, a=a[i], v = v[j])

            x += 1

# Retrieving ray futures

fish_res_3 = ray.get(sim_fish_3)
veg_res_3 = ray.get(sim_veg_3)


# %%
# Extracting metrics

fish_abn_3 = np.zeros((len(k), len(a), iter, T_max))
veg_abn_3 = np.zeros((len(k), len(a), iter, T_max))
mean_dist_3 = np.zeros((len(k), len(a), iter, T_max))
var_dist_3 = np.zeros((len(k), len(a), iter, T_max))

x = 0

for i in range(len(k)):

    for j in range(len(a)):

        for r in range(iter):
            
            fish_mat_3 = fish_mat(fish_res_3[x], N, T_max)

            # abundance

            fish_abn_3[i, j, r] = abn(fish_mat_3, T_max) #fish

            veg_abn_3[i, j, r] = abn(veg_res_3[x], T_max) #resource

            # movement

            mean_dist_3[i, j, r], var_dist_3[i, j, r] = movement(fish_mat_3, T_max = T_max)

            x += 1


# %%
a = list(range(0, 100, 20)) # half saturation distance

v = np.arange(0.1, 1, 0.1) # vegetation input rate

plt.rcParams['font.size'] = '15'

fig, axis = plt.subplots(1,2, figsize = (16,8))

veg_eq_3 = np.zeros((len(a), len(v)))
veg_var_3 = np.zeros((len(a), len(v)))

for i in range(len(a)):

    for j in range(len(v)):

        veg_eq_3[i, j] = np.mean(veg_abn_3[i, j, :, (T_max-100):(T_max-1)])
        veg_var_3[i, j] = np.var(veg_abn_3[i, j, :, (T_max-100):(T_max-1)])

    axis[0].scatter(v, veg_eq_3[i, :], label=a[i])
    axis[0].plot(v, veg_eq_3[i, :])

    axis[1].scatter(v, veg_var_3[i, :], label=a[i])
    axis[1].plot(v, veg_var_3[i, :])

axis[0].set_xlabel('Vegetation input rate (v)')
axis[0].set_ylabel('Vegetation abundance')
#plt.errorbar(a, veg_eq[i,:], label = k[i], yerr = veg_var[i,:], fmt='o')
axis[1].set_xlabel('Vegetation input rate (v)')
axis[1].set_ylabel('Variance')
axis[1].legend(title = 'Risk intensity (a)')

plt.savefig('fig3.png')


# %%
fish_eq_3 = np.zeros((len(a), len(v)))
fish_var_3 = np.zeros((len(a), len(v)))

for i in range(len(a)):

    for j in range(len(v)):

        fish_eq_3[i, j] = np.mean(fish_abn_3[i, j, :, (T_max-100):(T_max-1)])
        fish_var_3[i, j] = np.var(fish_abn_3[i, j, :, (T_max-100):(T_max-1)])

    plt.scatter(v, fish_eq_3[i, :], label=a[i])
    plt.plot(v, fish_eq_3[i, :])
    plt.legend()