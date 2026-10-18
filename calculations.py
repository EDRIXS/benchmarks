import numpy as np
import matplotlib.pyplot as plt
import edrixs

def model(nd):

    # Ni nd=8 Slater integrals in eV, with 0.8 screening of multipoles.
    slater = (
        [7.8, 9.7872, 6.0784],
        [7.8, 9.7872, 6.0784, 8.9, 6.1768, 4.6296, 2.6328],
    )
    Delta = 4.7
    ten_dq = 0.56
    impurity_levels = ten_dq * np.array([0.6, -0.4, -0.4, 0.6, -0.4])
    ten_dq_bath = 1.44
    bath_levels = ten_dq_bath * np.array([0.6, -0.4, -0.4, 0.6, -0.4])
    hyb = [2.06, 1.21, 1.21, 2.06, 1.21]
    v_soc = (0.1, 0.1)
    c_soc = 11.507

    # Effective exchange field along the [112] direction.
    exchange = 6 * 0.027
    ext_B = exchange / (2 * np.sqrt(6)) * np.array([1.0, 1.0, 2.0])

    # Align the calculated spectrum with the Ni L edge. The wrapper handles
    # the CT-derived core energy and returns the seven operator inputs plus the ED energy shift.
    edge_shift = 857.6
    *problem, shift = edrixs.model_siam_2d1p(
        slater=slater, nd=nd, Delta=Delta,
        impurity_levels=impurity_levels, bath_levels=bath_levels, hyb=hyb,
        v_soc=v_soc, c_soc=c_soc, om_shift=edge_shift,
        ext_B=ext_B, on_which='spin', sparse_U=True,
    )

    # Approximate L3 photon energy (eV): the CT convention cancels the
    # average Coulomb energies; a 2p3/2 hole contributes -c_soc/2.
    resE = edge_shift - c_soc/2
    return problem, shift, resE

def ed(nd, backend='petsc'):
    problem, shift, resE = model(nd)
    emat_i, umat_i, basis_i, emat_n, umat_n, basis_n, trans_mat = problem
    if backend=='fortran':
        hmat_i, _, _ = edrixs.get_ops(*problem, backend=backend)
    else:
        hmat_i = edrixs.build_op(emat_i, umat_i, basis_i, backend=backend)
    eval_i, evec_i = edrixs.ed(hmat_i, num_evals=3, shift=shift)
    return eval_i

def xas(nd, backend='petsc'):
    problem, shift, resE = model(nd)
    hmat_i, hmat_n, trans_ops = edrixs.get_ops(*problem, backend=backend)
    eval_i, evec_i = edrixs.ed(hmat_i, num_evals=3, shift=shift)
    gamma_c = 0.48 / 2
    ominc = np.arange(resE-3, resE+3, 0.1)
    Ixas = edrixs.xas(
        eval_i, evec_i, hmat_n, trans_ops, ominc,
        gamma_c=gamma_c)[:, 0]
    Ixas /= Ixas.max()
    return ominc, Ixas


def rixsmap(nd, backend='petsc'):
    problem, shift, resE = model(nd)
    emat_i, umat_i, basis_i, emat_n, umat_n, basis_n, trans_mat = problem
    hmat_i, hmat_n, trans_ops = edrixs.get_ops(*problem, backend=backend)
    eval_i, evec_i = edrixs.ed(hmat_i, num_evals=3, shift=shift)

    gamma_c = 0.48 / 2
    ominc = np.arange(resE-3, resE+3, 0.5)
    eloss = np.arange(-0.2, 3, 0.01)
    backend_kws={"linsys_maxiter": 5000} if backend == "petsc" else {"linsys_max": 5000}
    Irixs = edrixs.rixs(
    eval_i, evec_i, hmat_i, hmat_n, trans_ops,
    ominc, eloss,
    gamma_c=gamma_c,
    gamma_f=0.05,
    pol_type=[
        ('linear', 0, 'linear', 0),
        ('linear', 0, 'linear', np.pi / 2),
    ],
    backend_kws=backend_kws
)
    rixs_spectrum = Irixs[0].sum(axis=-1)
    rixs_spectrum /= rixs_spectrum.max()
    return ominc, eloss, rixs_spectrum


def rixsmap_recompute(nd, backend='petsc'):
    problem, shift, resE = model(nd)
    emat_i, umat_i, basis_i, emat_n, umat_n, basis_n, trans_mat = problem
    hmat_i, hmat_n, trans_ops = edrixs.get_ops(*problem, backend=backend)
    eval_i, evec_i = edrixs.ed(hmat_i, num_evals=3, shift=shift)

    gamma_c = 0.48 / 2
    ominc = np.arange(resE-3, resE+3, 0.5)
    eloss = np.arange(-0.2, 3, 0.01)
    backend_kws={"linsys_maxiter": 5000} if backend == "petsc" else {"linsys_max": 5000}
    if backend == 'petsc':
        backend_kws.update({'matrix_lifetime': 'recompute'})
    Irixs = edrixs.rixs(
    eval_i, evec_i, hmat_i, hmat_n, trans_ops,
    ominc, eloss,
    gamma_c=gamma_c,
    gamma_f=0.05,
    pol_type=[
        ('linear', 0, 'linear', 0),
        ('linear', 0, 'linear', np.pi / 2),
    ],
    backend_kws=backend_kws
)
    rixs_spectrum = Irixs[0].sum(axis=-1)
    rixs_spectrum /= rixs_spectrum.max()
    return ominc, eloss, rixs_spectrum


def singlerixs(nd, backend='petsc'):
    problem, shift, resE = model(nd)
    emat_i, umat_i, basis_i, emat_n, umat_n, basis_n, trans_mat = problem
    hmat_i, hmat_n, trans_ops = edrixs.get_ops(*problem, backend=backend)
    eval_i, evec_i = edrixs.ed(hmat_i, num_evals=3, shift=shift)

    backend_kws={"linsys_maxiter": 5000} if backend == "petsc" else {"linsys_max": 5000}

    gamma_c = 0.48 / 2
    ominc = [resE]
    eloss = np.arange(-0.2, 1, 0.01)
    Irixs = edrixs.rixs(
    eval_i, evec_i, hmat_i, hmat_n, trans_ops,
    ominc, eloss,
    gamma_c=gamma_c,
    gamma_f=0.05,
    pol_type=[
        ('linear', 0, 'linear', 0),
    ],
    backend_kws=backend_kws
)
    rixs_spectrum = Irixs[0].sum(axis=(-1))
    rixs_spectrum /= rixs_spectrum.max()
    return rixs_spectrum
