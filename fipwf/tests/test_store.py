from fipwf import models, store

def test_store():
    ses = store.session()

    t1 = models.Type(name="ResultType1", desc="First type of result")
    t2 = models.Type(name="ResultType2", desc="Second type of result")
    t3 = models.Type(name="ResultType3", desc="Third type of result")

    ps = models.Paramset(name="param1", params=dict(a=1,b=2,foo='bar',point=dict(x=3.,y=4.,z=5.)))

    res1 = models.Result(name="res1", type=t1)
    res2 = models.Result(name="res2", type=t2)
    res3 = models.Result(name="res3", type=t3)

    rs = models.Resultset(name="input results", results=[res1,res2])
    
    task = models.Task(name="task1", note="A task used to test this stuff.",
                       resultset=rs, paramset = ps, result=res3)

    ses.add(task)
    ses.commit()
    return ses

    
