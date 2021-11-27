# importing set up script

exec(open('setup.py').read())

# Varying risk gradient, vegetations input and fish reproductive rate

# %%
# varying risk

N = 50
center = N/2

ix = N/2
iy = list(range(N))

d = [0]*N

r = [0]*N

k = [1, 0.5, 0.25, 0.125]  # exponent

a = [0, 12.5, 25, 50]  # half saturation distance

fig, axis = plt.subplots(1, 4, figsize=(32, 8))

plt.rcParams['font.size'] = '15'

m = 0; n = 0

for x in range(len(k)):

    for j in range(len(a)):

        for i in range(N):

            d[i] = ((center - ix)**2 + (center - iy[i])**2)**0.5

            r[i] = risk_fun(d[i], a=a[j], k=k[x])

        axis[j].plot(d, r, label = k[x])
        axis[j].set_ylabel('Predation Risk')
        axis[j].set_xlabel('Distance from cover')
        axis[j].set_title('a = %a' % (a[j]))

plt.legend(title = 'Risk gradient')
plt.savefig('fig4.png')


# %%
# varying distance and exponent of risk function

# Defining simulation parameters

T_max = 1000  # time for the simulation
N = 50  # length of side for N x N matrix
n = 20  # initial number of fish

k = [1, 0.5, 0.25, 0.125]  # exponent

a = list(range(0, N, 5))  # half saturation distance

iter = 10

# Results matrices

sim_fish = [0]*len(k)*len(a)*iter  # np.zeros((len(k), len(a)))
sim_veg = [0]*len(k)*len(a)*iter  # np.zeros((len(k), len(a)))

x = 0  # ray sync

for i in range(len(k)):

    for j in range(len(a)):

        for rep in range(iter):

            sim_fish[x], sim_veg[x] = fish_sim.remote(N=N, T_max=T_max, k=k[i], a=a[j])

            x += 1

# Retrieving ray futures

fish_res = ray.get(sim_fish)
veg_res = ray.get(sim_veg)


# %%
# Extracting metrics

fish_abn = np.zeros((len(k), len(a), iter, T_max))
veg_abn = np.zeros((len(k), len(a), iter, T_max))
mean_dist = np.zeros((len(k), len(a), iter, T_max))
var_dist = np.zeros((len(k), len(a), iter, T_max))

x = 0

for i in range(len(k)):

    for j in range(len(a)):

        for r in range(iter):
            
            fish_mat = fish_mat(fish_res[x], N, T_max)

            # abundance

            fish_abn[i, j, r] = abn(fish_mat, T_max) #fish

            veg_abn[i, j, r] = abn(veg_res[x], T_max) #resource

            # movement

            mean_dist[i, j, r], var_dist[i, j, r] = movement(fish_mat, T_max = T_max)

            x += 1


# %%
fig, axis = plt.subplots(4, 4, figsize=(16, 16))

plt.rcParams['font.size'] = '10'

a_sub = list(range(0, 20, 5))

for i in range(len(k)):

    for j in range(len(a_sub)):

        axis[i, j].plot(range(T_max), veg_abn[i, j, iter-1, :])
        axis[i, j].set_title('a = %a; k = %a' % (a_sub[j], k[i]))
        axis[i, j].set_ylim([np.min(veg_abn)-100, np.max(veg_abn)+100])


# %%
fig, axis = plt.subplots(4, 4, figsize=(16, 16))

plt.rcParams['font.size'] = '10'

a_sub = list(range(0, 20, 5))

for i in range(len(k)):

    for j in range(len(a_sub)):

        axis[i, j].plot(range(T_max), fish_abn[i, j, iter-1, :])
        axis[i, j].set_title('a = %a; k = %a' % (a_sub[j], k[i]))
        axis[i, j].set_ylim([np.min(fish_abn)-10, np.max(fish_abn)+10])


# %%
k = [1, 0.5, 0.25, 0.125]  # exponent

a = list(range(0, 100, 5))  # half saturation distance

plt.rcParams['font.size'] = '15'

veg_eq = np.zeros((len(k), len(a)))
veg_var = np.zeros((len(k), len(a)))

fig, axis = plt.subplots(1, 2, figsize = (16,8))

for i in range(len(k)):

    for j in range(len(a)):

        veg_eq[i, j] = np.mean(veg_abn[i, j, :, (T_max-100):(T_max-1)])
        veg_var[i, j] = np.var(veg_abn[i, j, :, (T_max-100):(T_max-1)])

    axis[0].scatter(a, veg_eq[i, :], label=k[i])
    axis[0].plot(a, veg_eq[i, :])

    axis[1].scatter(a, veg_var[i, :], label=k[i])
    axis[1].plot(a, veg_var[i, :])



axis[0].set_xlabel('Risk intensity (a)')
axis[0].set_ylabel('Vegetation abundance')
#plt.errorbar(a, veg_eq[i,:], label = k[i], yerr = veg_var[i,:], fmt='o')
axis[1].set_xlabel('Risk intensity (a)')
axis[1].set_ylabel('Variance')
axis[1].legend(title = 'Risk Gradient (k)')

plt.savefig('fig1.png')


# %%
k = [1, 0.5, 0.25, 0.125]  # exponent

a = list(range(0, 100, 5))  # half saturation distance

plt.rcParams['font.size'] = '15'

mov_eq = np.zeros((len(k), len(a)))
mov_var = np.zeros((len(k), len(a)))

fig, axis = plt.subplots(1, 2, figsize = (16,8))

for i in range(len(k)):

    for j in range(len(a)):

        mov_eq[i, j] = np.mean(mean_dist[i, j, :, (T_max-100):(T_max-1)])
        mov_var[i, j] = np.mean(var_dist[i, j, :, (T_max-100):(T_max-1)])

    axis[0].scatter(a, mov_eq[i, :], label=k[i])
    axis[0].plot(a, mov_eq[i, :])

    axis[1].scatter(a, mov_var[i, :], label=k[i])
    axis[1].plot(a, mov_var[i, :])



axis[0].set_xlabel('Risk intensity (a)')
axis[0].set_ylabel('Mean distance from cover')
#plt.errorbar(a, veg_eq[i,:], label = k[i], yerr = veg_var[i,:], fmt='o')
axis[1].set_xlabel('Risk intensity (a)')
axis[1].set_ylabel('Variance')
axis[1].legend(title = 'Risk Gradient (k)')

plt.savefig('fig5.png')


# %%
fish_eq = np.zeros((len(k), len(a)))
fish_var = np.zeros((len(k), len(a)))

for i in range(len(k)):

    for j in range(len(a)):

        fish_eq[i, j] = np.mean(fish_abn[i, j, :, (T_max-100):(T_max-1)])
        fish_var[i, j] = np.var(fish_abn[i, j, :, (T_max-100):(T_max-1)])

    plt.scatter(a, fish_eq[i, :], label=k[i])
    plt.plot(a, fish_eq[i, :])
    plt.legend()
