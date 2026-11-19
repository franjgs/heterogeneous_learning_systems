import pytest
from types import SimpleNamespace
from hls.rq1_allocation import Alert, Analyst, Assignment
from studies.soc_human_ai_organization.analyze_a0_weaknesses import order_loss, diagnose

def test_order_deadline_and_duration():
    assert order_loss(0, 3, 1, 10, 1, .8, .9) == pytest.approx(.9)
    assert order_loss(0, 1, 1, 1, 2, 1, 1) == 0

def test_elapsed_blocking_and_post_dispatch_idle():
    alerts=[Alert('a',0,'x',10),Alert('b',1,'x',10)]
    analyst=Analyst('i',frozenset({'x'}),{'x':1})
    jobs=[Assignment('a','i',0,3,1),Assignment('b','i',3,4,1)]
    meta={a.alert_id:SimpleNamespace(difficulty=0,severity='high') for a in alerts}
    original=tuple(jobs)
    _,swaps,d=diagnose(alerts,[analyst],{'i':{'x':1}},jobs,meta,5)
    assert d['critical_blocked']==2
    assert d['idle']==0
    assert swaps==[]
    assert tuple(jobs)==original
