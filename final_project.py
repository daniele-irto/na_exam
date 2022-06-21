# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.8
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import lagrange
from scipy.misc import derivative


# + active=""
# X = np.polynomial.chebyshev.chebpts2(6)
# e_3 = np.zeros((6,))
# e_3[3] = 1
#
# B_3 = lagrange(X, e_3)
# B_3_prime = np.polyder(B_3)
#
# x = np.linspace(-1,1,501)
# plt.plot(x, B_3(x))
# plt.plot(X, 0*X, 'ro')
# plt.figure()
# plt.plot(x, B_3_prime(x))
# plt.plot(X, 0*X, 'ro')

# + [markdown] pycharm={"name": "#%% md\n"}
# # Final project -- Numerical Analysis -- 2020/2021
#
# ## General goal
#
# Consider the hyper-cube $\Omega := [-1,1]^d$ in dimension `d`.
#
# Given a function $f: \Omega \mapsto R$, find $u: \Omega \mapsto R$ such that 
#
# $$
# - \Delta u  + u = f, \text{ in } \Omega
# $$
#
# $
# \frac{\partial u}{\partial n} = 0 \text{ on } \partial \Omega
# $
#
# using Chebyshev spectral elements, and in a matrix-free framework.
#
# ## Due date: 
#
# - MHPC students: 20 February 2021
# - DSSC/LM/PHD students: 1 day before the oral examination
#
# ## General definitions
#
# We recall here some general definitions that will be useful throughout the project.
#
# - The space $Q^p(\Omega)$ is the space of polynomials of order $p$ in each coordinate direction. The dimension of $Q^p$ is $(p+1)^d$ where $d$ is the dimension of the space. 
#
# - A tensor product basis for $Q^p(\Omega)$ can be constructed from a basis for $P^p([-1,1])$, by arranging the indices in d-dimensional arrays, i.e., if $\{v_i\}_{i=0}^p$ is a basis for $P^p([-1,1])$, then, for example, 
# $$
# v_{ijk} := v_i(x_0)v_j(x_1)v_k(x_2)
# $$
# is a basis for $Q^p([-1,1]^3)$.
#
# - Chebyshev points of type 2 are Chebishev points in one dimension that include end points. These are not minimizers of the linfty norm of the Lebesgue function (those are Chebishev points of type 1), but are minimizers of Lebesgue function when you constrain two of the points to coincide with the extremes of the interval $[-1,1]$. You can obtain those points by calling `numpy.polynomial.chebyshev.chebpts2`.
#
# - Chebyshev spectral elements are the tensor product basis for $Q^p(\Omega)$, generated by the Lagrange basis functions constructed using as support points the Chebyshev points of type 2. In one dimension, for degree=5, npoints=6, they look like
#
# ![basis_6.png](imgs/basis_6.png)
#
# - Integration in each coordinate direction can be performed using Gauss quadrature formulas, which can be queried by the function `numpy.polynomial.legendre.leggauss`. That function returns a tuple of two objects,  containing both the quadrature points `q` and the quadrature weights `w`, i.e., `q, w = numpy.polynomial.legendre.leggauss(nq)`.
#
# - The construction of a Lagrange basis can be done easily by calling `scipy.interpolate.lagrange(X, ei)` where `X` are the interpolation points, and `ei` is a vector containing all zeros, except a one in the position corresponding to the index i. For example, the following code 
#
# ~~~
# X = numpy.polynomial.chebyshev.chebpts2(6)
# e_3 = zeros((6,))
# e_3[3] = 1
#
# B_3 = lagrange(X, e_3)
# B_3_prime = polyder(B_3)
#
# x = linspace(-1,1,501)
# plot(x, B_3(x))
# plot(X, 0*X, 'ro')
# figure()
# plot(x, B_3_prime(x))
# plot(X, 0*X, 'ro')
# ~~~
#
# will produce the following pictures
#
# ![base_3.png](imgs/base_3.png)
#
# ![base_3_prime.png](imgs/base_3_prime.png)
#
# Which correspond to the fourth (`index=3`) Chebishev spectral basis function and its derivative, for the space $P^5([-1,1])$.
#
# The functions `B_3` and `B_3_prime` computed above are callable functions, i.e., you can evaluate the basis and its derivative as normal functions, and they accept as input numpy arrays.
#
# ## Weak formulation
#
# The weak form of the problem reads:
#
# Given $f:\Omega \mapsto R$, find $u\in H^1(\Omega)$ such that
#
# $
# \int_\Omega \nabla u \cdot \nabla v + \int_\Omega u v = \int_\Omega f v \qquad \forall v \in H^1(\Omega)
# $
#
# ## Discrete weak formulation (one dimensional case)
#
# Given a finite dimensional space $V_h \subset H^1([-1,1])$ such that  $V_h = \text{span}\{v_i\}_{i=0}^p$, then
# the discrete problem reads:
#
# Find $u$ such that
#
# $
# A u = f 
# $
#
# where $A$ is a matrix in  $R^{(p+1)\times(p+1)}$  and $f$ is a vector in $R^{(p+1)}$ 
#
# $
# A_{ij} = \int_\Omega \nabla v_j \cdot \nabla v_i+\int_\Omega  v_j  v_i, \qquad f_i = \int_\Omega f v_i
# $
#
# that is (using a quadrature with $q_\alpha$ and $w_\alpha$ as points and weights):
#
# $
# A_{ij} = \sum_{\alpha=0}^{nq-1}\left[ v'_j(q_\alpha) v'_i(q_\alpha)+  v_j(q_\alpha)  v_i(q_\alpha)\right]w_\alpha
# $
#
# $
# f_{i} = \sum_{\alpha=0}^{nq-1} v_j(q_\alpha) f(q_\alpha) w_\alpha
# $
#
# Let's assume we have computed the matrices $B_{i\alpha} := v_i(q_\alpha)$, and $D_{i\alpha} := v'_i(q_\alpha)$ containing the evaluation of all basis functions and of their derivatives in the quadrature points $q_\alpha$.  
#
# The matrix $A$ can then be written as
#
# $
# A_{ij} = \sum_\alpha \left(D_{i\alpha} D_{j\alpha} w_\alpha + B_{i\alpha} B_{j\alpha} w_\alpha\right) = K_{ij} + M_{ij}
# $
#
# where $K$ is usually known as the one dimensional stiffness matrix, and $M$ as the one dimensional mass matrix:
#
#
# $
# K_{ij} = \sum_\alpha \left(D_{i\alpha} D_{j\alpha} w_\alpha \right)
# $
#
#
# $
# M_{ij} = \sum_\alpha \left(B_{i\alpha} B_{j\alpha} w_\alpha \right)
# $
#
# Using numpy and Lapack, these can be computed efficiently by calling `einsum`:
#
# ~~~
# K = einsum('iq, q, jq', D, w, D)
# M = einsum('iq, q, jq', B, w, B)
# ~~~
#
# where the function `einsum` interprets the first argument (a string) as a list of indices over which sum should occur. The list must be of the same length of the other arguments (3 in this case), and the number of indices for each entry musth match the input (i.e., `iq` for `D`, and `q` for `w`). The three arrays are multiplied entry by entry, and if an index is repeated in the description, those entries are summed over (see the documentation).
#
# ## Higher dimensional case
#
# If we have already computed the one dimensional matrices $B_{i\alpha} = v_i(q_\alpha)$ and $D_{i\alpha} := v'_i(q_\alpha)$ we can compute easily the 2 and 3 dimensional versions of the stiffness, mass, and system matrices.
#
# In particular, defining $q_{\alpha\beta} := (q_\alpha, q_\beta)$, and $w_{\alpha\beta} = w_\alpha w_\beta$, we have
#
# $\nabla v_{ij}(q_{\alpha\beta}) \cdot \nabla v_{kl}(q_{\alpha\beta}) := v'_i(q_{\alpha})v_j(q_{\beta})v'_k(q_{\alpha})v_l(q_{\beta}) + v_i(q_{\alpha})v'_j(q_{\beta})v_k(q_{\alpha})v'_l(q_{\beta})$. 
#
# Integrating with quadrature twice (once for each dimension), we get:
#
# $
# K_{ij,kl} := \sum_q \sum_p v'_i(X_q)v_j(X_p)v'_k(X_q)v_l(X_p) + v_i(X_q)v'_j(X_p)v_k(X_q)v'_l(X_p) w_p w_q
# $
#
# These are easily expressed directly through python `einsum`, i.e., 
#
# ```
# KM = einsum('iq, jp, q, p, kq, lp -> ijkl', D, B, w, w, D, B)
# MK = einsum('iq, jp, q, p, kq, lp -> ijkl', D, B, w, w, B, D)
# KK = KM+MK
# ```
#
# Or, if we have already the one dimensional matrices $K_{ij}$ and $M_{ij}$, then the above become:
#
# $
# A_{ij,kl} := K_{ik}M_{jl} + M_{ik}K_{jl} + M_{ik}M_{jl}
# $
#
# which, using the `einsum` command, becomes:
#
# ```
# KM = einsum('ik, jl -> ijkl', K, M)
# MK = einsum('ik, jl -> ijkl', M, K)
# MM = einsum('ik, jl -> ijkl', M, M)
# KK = KM+MK
# AA = KK+MM
#
# ```
#
# The resulting array can be reshaped to a two dimensional matrix by calling `AA.reshape((n**2, n**2))`, and solved for using `linalg.solve`.
#
# Similarly in 3 dimensions:
#
#
# $
# A_{ijk,lmn} := (K_{il}M_{jm}M_{kn}+M_{il}K_{jm}M_{kn}+M_{il}M_{jm}K_{kn})+M_{il}M_{jm}M_{kn}
# $
#
# Sums of the kind $D_{ijk,lmn} = A_{il}B_{jm}C_{kn}$ can be expressed using `einsum` as
#
# ```
# D = einsum('il, jm, kn -> ijklmn', A, B, C)
# ```
#
# And the resulting six-dimensional array can be reshaped to a matrix by calling `D.reshape((n**3, n**3))`.

# + [markdown] pycharm={"name": "#%% md\n"}
# ## Intermediate assignments
#
# ### 1. One dimensional matrices
# Write a function that, given the number of Chebishev points `n`, returns `K`, `M`, and `A` for a one dimensional problem, integrated exactly using Gauss quadrature formulas with the correct number of quadrature points 
# -

def get_e(n):
    e = np.zeros((n, n))
    for i in range(n):
        e[i, i] = 1
    return e


def get_basis(n, e, X, i):
    v = lagrange(X, e[i])
    return v


# + pycharm={"name": "#%%\n"}
def compute_one_dimensional_matrices(n):

    e = get_e(n)  # matrix with i-th row all 0s except i-th index
    X = np.polynomial.chebyshev.chebpts2(n)  # interpolation points
    q, w = np.polynomial.legendre.leggauss(n)  # quadrature points and weights

    B = np.zeros((n, n))
    D = np.zeros((n, n))

    for i in range(0, n):
        v = get_basis(n, e, X, i)
        for alpha in range(0, n):
            B[i, alpha] = v(q[alpha])
            D[i, alpha] = derivative(v, q[alpha])

    K = np.einsum('iq, q, jq', D, w, D)
    M = np.einsum('iq, q, jq', B, w, B)
    A = K + M

    return K, M, A


# -

K, M, A = compute_one_dimensional_matrices(2)

K

M

A


# + [markdown] pycharm={"name": "#%% md\n"}
# ### 2. Error in one dimension
#
# Using 
#
# $
# u_{exact}(x) = \cos(\pi x)
# $
#
# as the exact solution, compute the forcing term $f$ that should go on the right hand side of the system to ensure that the exact solution is $u$, i.e., $f = -\Delta u + u$  
#
# Use $f$ to compute the right hand side of your problem, and solve the problem (using `linalg.solve`) for increasing numbers of Chebishev points. Compute the $L^2$ error between the exact solution and the computed approximation, using a higher order quadrature w.r.t. what you used to assemble the matrices. 
#
# Plot the error as a function of $n$, for $n$ in $[10,...,20]$.

# + pycharm={"name": "#%%\n"}
def exact_one_d(x):
    u = np.cos(np.pi * x)
    return u


def rhs_one_d(x):
    rhs = np.cos(np.pi * x) * (1 + np.pi**2)
    return rhs


def compute_error_one_d(n, exact, rhs):
    # Replace this with you implementation
    error = 1/n
    return error


error = []
all_n = range(10, 20)
for n in all_n:
    error.append(compute_error_one_d(n, exact_one_d, rhs_one_d))

plt.loglog(all_n, error, 'o-')


# + [markdown] pycharm={"name": "#%% md\n"}
# ### 3. Two dimensional matrices
#
# Write a function that, given the number of Chebishev points `n` per each coordinate direction, returns `K`, `M`, and `A` for a two dimensional problem, integrated exactly using Gauss quadrature formulas with the correct number of quadrature points (as matrices, i.e., reshaped to be two dimensional)

# + pycharm={"name": "#%%\n"} tags=[]
# your code here

# + [markdown] pycharm={"name": "#%% md\n"}
# ### 3. Error in two dimension
#
# Using 
#
# $
# u_{exact}(x) = \cos(\pi x_0)\cos(\pi x_1)
# $
#
# as the exact solution, compute the forcing term $f$ that should go on the right hand side of the system to ensure that the exact solution is $u$, i.e., $f = -\Delta u + u$  
#
# Use $f$ to compute the right hand side of your problem, and solve the problem (using `linalg.solve`) for increasing numbers of Chebishev points. Compute the $L^2$ error between the exact solution and the computed approximatio, using a higher order quadrature w.r.t. what you used to assemble the matrices. 
#
# A solution should look like:
#
# ![exact_2d.png](imgs/exact_2d.png)
#
# The plot was obtained as `imshow(u.reshape((n,n))`.
#
# Plot the error as a function of $n$, for $n$ in $[10,...,20]$.

# + pycharm={"name": "#%%\n"} tags=[]
# your code here

# + [markdown] pycharm={"name": "#%% md\n"}
# ### 4. Conjugate gradient
#
# The conjugate gradient method does not require the knowledge of the matrix, but only of the result of the matrix vector product with the system matrix A. 
#
# Implement a version of the conjugate gradient method that solves the linear system of the two dimensional problem (up to a given tolerance) by only using a function that implements the matrix vector product, i.e., given a `matvec` function, for example defined by  
#
# ~~~
# def matvec(src):
#     return A.dot(src)
# ~~~
#
# build a conjugate gradient method that only uses the function `matvec` to evaluate `A.dot(src)`. 

# + jupyter={"outputs_hidden": true} pycharm={"name": "#%%\n"}
def cg(matvec, b, x0, tol=1e-05, maxiter=10000):
    # inside this function, you can call matvec(b) to evaluate the matrix vector 
    x = x0.copy()
    return x

# + [markdown] pycharm={"name": "#%% md\n"}
# ### 5. "Matrix free" evaluation
#
# Instead of assembling the two (or three dimensional) matrix, and then compute the matrix vector product using `A.dot(v)`, we can exploit the tensor product structure of the problem, and gain some computational time.
#
# In particular, we exploit the fact that the two dimensional matrix is a `reshape` of the array
#
# $
# A_{ij,kl} := K_{ik}M_{jl} + M_{ik}K_{jl} + M_{ik}M_{jl}
# $
#
# which is constructed using the one dimensional matrices assembled at step 1.
#
# Given an array `v`, it can be reshaped to a matrix of coefficients $v_{ij}$ in $R^{n\times n}$, and we can compute `A.dot(v)` as the sum $w_{ij} = \sum_{kl} A_{ij,kl} v_{kl}$
#
# So `A.dot(v)` reduces to  series of one dimensional matrix-matrix and matrix vector products:
#
#
# $
# w_{ij}  = \sum_{kl} A_{ij,kl} v_{kl} = \sum_{kl} (K_{ik}M_{jl}v_{kl} + M_{ik}K_{jl}v_{kl} + M_{ik}M_{jl}v_{kl})
# $
#
# which can be rearranged as 
#
# ~~~
# def matvec(vinput):
#     v = vinput.reshape((n,n))
#
#     Mv = M.dot(v) # result is n x n 
#     Kv = K.dot(v) # result is n x n 
#
#     # KT_Mv = K.dot(Mv)  # K is symmetric
#     # MT_Kv = M.dot(Kv)  # M is symmetric
#     # MT_Mv = M.dot(Mv)  # M is symmetric
#
#     u = K.dot(Mv)
#     u += M.dot(Kv) 
#     u += M.dot(Mv)
#     return u.reshape((n**2,))
# ~~~
#
# Make a comparison of the timings between using the full two dimensional matrix `A` to compute the matrix vector product, VS using the compressed version above, as we increase `n` from 50 to 100.

# + jupyter={"outputs_hidden": true} pycharm={"name": "#%%\n"}
# your code here

# + [markdown] pycharm={"name": "#%% md\n"}
# ### 6. "Matrix free" evaluation for three dimensional problems (mandatory for MHPC, optional for others)
#
# Looking at https://www.geeksforgeeks.org/running-python-script-on-gpu/, implement the same matrix free solver for three dimensional problems, exploiting just in time compilation, numba, and (optionally) GPU acceleration (if you have access to a GPU). 
#
# Compare the timings you get for a fixed number of matrix vector products as n increases from 50 to 100 for the cases 
#
# 1. matrix based (assemble the three dimensional A, measure time of 100 A.dot(v)
# 2. matrix free, pure numpy (using techinque above, measure time 100 applications of matvec(v))
# 3. matrix free, numba+jit on CPU (measure time 100 applications of matvec(v))
# 4. (optional) matrix free, numba+jit on GPU (measure time 100 applications of matvec(v))
#
# Comment on your findings.

# + jupyter={"outputs_hidden": true} pycharm={"name": "#%%\n"}
# your code here
