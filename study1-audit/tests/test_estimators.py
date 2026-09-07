"""Analytical and adversarial estimator tests; all examples are synthetic."""
import sys
from pathlib import Path
import itertools
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from estimators import (slope_fit, slope_weights, box_slope_radius, rms_slope_radius,
                        moment_outer_bounds, paired_moments, heuristic_fit)


def test_affine_and_shift_invariance():
    x=np.array([100.,300.,800.,1200.]);y=33+.27*x
    f=slope_fit(x,y)
    assert f['slope']==pytest.approx(.27)
    assert f['max_abs_residual']<1e-12
    assert slope_fit(x+1e6,y+777)['slope']==pytest.approx(.27)
    assert slope_weights(x).sum()==pytest.approx(0)
    assert slope_weights(x)@x==pytest.approx(1)


def test_two_points_have_no_variance_estimate_or_affine_test():
    f=slope_fit([0,1],[2,1002])
    assert f['slope']==1000
    assert f['max_leverage']==1
    assert np.isnan(f['iid_se']) and np.isnan(f['hc3_se'])
    assert f['distinct_x']==2 and f['max_abs_residual']==0


@pytest.mark.parametrize('x,y', [([1,1],[2,3]),([1],[2]),([1,2],[3,np.nan]),([1,np.inf],[2,3])])
def test_unidentified_or_invalid_raises(x,y):
    with pytest.raises(ValueError):slope_fit(x,y)


def test_loo_matches_refit_and_hc3_formula():
    x=np.array([1.,2.,8.,20.]);y=np.array([0.,2.,3.,19.])
    f=slope_fit(x,y)
    actual=max(abs(slope_fit(np.delete(x,j),np.delete(y,j))['slope']-f['slope']) for j in range(4))
    assert f['max_loo_change']==pytest.approx(actual)
    w=slope_weights(x);h=.25+(x-x.mean())*w
    e=y-y.mean()-f['slope']*(x-x.mean())
    assert f['hc3_se']**2==pytest.approx(np.sum((w*e/(1-h))**2))


def test_box_bound_sharp_exhaustive_correlated_errors():
    x=np.array([0.,200.,700.,1000.]);cap=100.;w=slope_weights(x)
    radius=box_slope_radius(x,cap)
    attained=max(abs(w@(cap*np.array(signs))) for signs in itertools.product([-1,1],repeat=4))
    assert attained==pytest.approx(radius)
    assert w@(cap*np.sign(w))==pytest.approx(radius)


def test_rms_bound_sharp():
    x=np.array([0.,10.,900.,1000.]);cap=500.;w=slope_weights(x)
    u=cap*np.sqrt(len(w))*w/np.linalg.norm(w)
    assert np.sqrt(np.mean(u*u))==pytest.approx(cap)
    assert w@u==pytest.approx(rms_slope_radius(x,cap))


def test_moment_outer_bounds_cover_every_box_corner():
    observed=np.array([-.3,.02,.25,.4]);r=np.array([.1,.2,.01,.05])
    bounds=moment_outer_bounds(observed,r)
    for signs in itertools.product([-1,1],repeat=4):
        latent=observed+r*np.array(signs)
        for name,value in [('bias',latent.mean()),('rmse',np.sqrt(np.mean(latent**2))),('sd',latent.std())]:
            assert bounds[name][0]-1e-12<=value<=bounds[name][1]+1e-12


def test_bounds_do_not_clip_rates_or_center_bias_away():
    b=moment_outer_bounds([2.,3.],[0.,0.])
    assert b['bias']==[2.5,2.5]
    assert b['rmse']==[np.sqrt(6.5)]*2
    assert b['sd']==[.5,.5]
    with pytest.raises(ValueError):moment_outer_bounds([1],[-1])
    with pytest.raises(ValueError):box_slope_radius([0,1],-1)


def test_covariance_identity_and_negative_value_retained():
    a=np.array([-2.,0.,3.,5.]);b=-a
    m=paired_moments(a,b)
    assert m['covariance']<0
    assert m['average_variance']-m['difference_variance_over_four']==pytest.approx(m['covariance'])


def test_shared_slope_error_looks_stable_even_with_homogeneous_latent_beliefs():
    x=np.array([-15000.,-9000.,-3000.,3000.,9000.,15000.])
    error_slope=np.array([-.1,.1,-.1,.1])
    latent_slope=.2
    y=5000+(latent_slope+error_slope[:,None])*x
    a=np.array([slope_fit(x[::2],v[::2])['slope'] for v in y])
    b=np.array([slope_fit(x[1::2],v[1::2])['slope'] for v in y])
    assert paired_moments(a,b)['correlation']==pytest.approx(1)
    assert paired_moments(a,b)['covariance']==pytest.approx(np.var(error_slope,ddof=1))
    assert np.var(np.full(4,latent_slope))==0


def test_common_intercept_error_cancels_in_income_slope():
    x=np.array([0.,1.,2.,5.]);y=5+.2*x
    assert slope_fit(x,y+1000)['slope']==pytest.approx(.2)


def test_nonlinear_truth_can_share_nominal_bracket():
    x=np.array([0.,10.,20.]);nominal_bracket=np.array([3,3,3])
    tax=.25*x+np.array([0.,0.,2.])
    assert np.unique(nominal_bracket).size==1
    assert slope_fit(x,tax)['max_abs_residual']>.05


def test_heuristic_linear_recovery_and_rank_failure():
    x=np.array([10.,40.,80.,100.]);tax=np.array([0.,3.,15.,24.])
    iron=.1*x;spotlight=.25*x-5
    y=(1-.4-.1)*tax+.4*iron+.1*spotlight
    f=heuristic_fit(tax,iron,spotlight,y)
    assert f['gamma']==pytest.approx([.4,.1])
    assert f['grid']==pytest.approx([.4,.1])
    assert heuristic_fit(tax,np.zeros(4),np.zeros(4),y)['rank']==1
