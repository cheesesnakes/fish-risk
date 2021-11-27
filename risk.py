# importing set up script

exec(open('setup.py').read())

# Testing risk function

N = 50
center = N/2

ix = N/2
iy = list(range(N))

d = [0]*N

r = [0]*N
for i in range(N):

    d[i] = ((center - ix)**2 + (center - iy[i])**2)**0.5
    r[i] = risk_fun(d[i])


plt.plot(d, r)
plt.xlabel('Distance from cover')
plt.ylabel('Predation Risk')
plt.savefig('fig4.png')
