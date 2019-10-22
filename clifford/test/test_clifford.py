from functools import reduce
import operator

import pytest
import numpy as np
import numpy.testing

from clifford import Cl, randomMV, Frame, \
    conformalize, grade_obj, MultiVector, MVArray


class TestClifford:

    @pytest.fixture(params=[3, 4, 5], ids='Cl({})'.format)
    def algebra(self, request):
        return Cl(request.param)

    def test_inverse(self, algebra):
        layout, blades = algebra
        a = 1. + blades['e1']
        with pytest.raises(ValueError):
            1 / a
        for i in range(10):
            a = randomMV(layout, grades=[0, 1])
            denominator = float(a(1)**2-a(0)**2)
            if abs(denominator) > 1.e-5:
                a_inv = (-a(0)/denominator) + ((1./denominator) * a(1))
                assert abs((a * a_inv)-1.) < 1.e-11
                assert abs((a_inv * a)-1.) < 1.e-11
                assert abs(a_inv - 1./a) < 1.e-11

    def test_grade_masks(self, algebra):
        layout, blades = algebra
        A = layout.randomMV()
        for i in range(layout.dims + 1):
            np.testing.assert_almost_equal(A(i).value,A.value*layout.grade_mask(i))

    def test_rotor_mask(self, algebra):
        layout, blades = algebra
        rotor_m = layout.rotor_mask
        rotor_m_t = np.zeros(layout.gaDims)
        for _ in range(10):
            rotor_m_t += 100*np.abs(layout.randomRotor().value)
        np.testing.assert_almost_equal(rotor_m_t > 0, rotor_m)

    def test_exp(self):
        layout, blades = Cl(3)
        e12 = blades['e12']
        theta = np.linspace(0, 100 * np.pi, 101)
        a_list = [np.e**(t * e12) for t in theta]
        for a in a_list:
            np.testing.assert_almost_equal(abs(a), 1.0, 5)

    def test_exp_g4(self):
        '''
        a numerical test for the exponential of a bivector. truth was
        generated by results of clifford v0.82
        '''
        layout, blades = Cl(4)

        valB = np.array([-0.                 ,  0.                 ,  0.                 ,
               -0.                 , -0.                 , -1.9546896043012914 ,
                0.7069828848351363 , -0.22839793693302957,  1.0226966962560002 ,
                1.8673816483342143 , -1.7694566455296474 , -0.                 ,
               -0.                 ,  0.                 , -0.                 ,
               -0.                 ])
        valexpB = np.array([-0.8154675764311629  ,  0.                  ,
                0.                  ,  0.                  ,
                0.                  ,  0.3393508714682218  ,
                0.22959588097548828 , -0.1331099867581965  ,
               -0.01536404898029994 ,  0.012688721722814184,
                0.35678394795928464 ,  0.                  ,
                0.                  ,  0.                  ,
                0.                  , -0.14740840378445502 ])


        B = MultiVector(layout=layout,value=valB)
        expB =MultiVector(layout=layout,value=valexpB)
        np.testing.assert_almost_equal(np.exp(B)[0].value,expB.value)

    def test_inv_g4(self):
        '''
        a numerical test for the inverse of a MV. truth was
        generated by results of clifford v0.82
        '''
        layout, blades = Cl(4)
        valA = np.array([-0.3184271488037198 , -0.8751064635010213 , -1.5011710376191947 ,
                1.7946332649746224 , -0.8899576254164621 , -0.3297631748225678 ,
                0.04310366054166925,  1.3970365638677635 , -1.545423393858595  ,
                1.7790215501876614 ,  0.4785341530609175 , -1.32279679741638   ,
                0.5874769077573831 , -1.0227287710873676 ,  1.779673249468527  ,
               -1.5415648119743852 ])

        valAinv= np.array([ 0.06673424072253006 , -0.005709960252678998,
               -0.10758540037163118 ,  0.1805895938775471  ,
                0.13919236400967427 ,  0.04123255613093294 ,
               -0.015395162562329407, -0.1388977308136247  ,
               -0.1462160646855434  , -0.1183453106997158  ,
               -0.06961956152268277 ,  0.1396713851886765  ,
               -0.02572904638749348 ,  0.02079613649197489 ,
               -0.06933660606043765 , -0.05436077710009021 ])

        A = MultiVector(layout=layout,value=valA)
        Ainv = MultiVector(layout=layout,value=valAinv)


        np.testing.assert_almost_equal(A.inv().value, Ainv.value)

    def test_indexing(self):
        layout, blades = Cl(3)
        e12 = blades['e12']
        e1 = blades['e1']
        e2 = blades['e2']
        e3 = blades['e3']
        assert e12[e12] == 1
        assert e12[e3] == 0
        assert e12[(2,1)] == -1


    def test_add_float64(self):
        '''
        test array_wrap method to take control addition from numpy array
        '''
        layout, blades = Cl(3)
        e1 = blades['e1']

        np.float64(1) + e1
        assert 1 + e1 == np.float64(1) + e1

        assert 1 + e1 == e1 + np.float64(1)

    def test_array_control(self):
        '''
        test methods to take control addition from numpy arrays
        '''
        layout, blades = Cl(3)
        e1 = blades['e1']
        e3 = blades['e3']
        e12 = blades['e12']

        for i in range(100):

            number_array = np.random.rand(4)

            output = e12+(e1*number_array)
            output2 = MVArray([e12+(e1*n) for n in number_array])
            np.testing.assert_almost_equal(output, output2)

            output = e12 + (e1 * number_array)
            output2 = MVArray([e12 + (e1 * n) for n in number_array])
            np.testing.assert_almost_equal(output, output2)

            output = (number_array*e1) + e12
            output2 = MVArray([(n*e1) + e12 for n in number_array])
            np.testing.assert_almost_equal(output, output2)

            output = number_array/ e12
            output2 = MVArray([n/ e12 for n in number_array])
            np.testing.assert_almost_equal(output, output2)

            output = (e1 / number_array)
            output2 = MVArray([(e1/n) for n in number_array])
            np.testing.assert_almost_equal(output, output2)

            output = ((e1 / number_array)*e3)/e12
            output2 = MVArray([((e1 / n)*e3)/e12 for n in number_array])
            np.testing.assert_almost_equal(output, output2)

    def test_array_overload(self, algebra):
        '''
        test overload operations
        '''
        layout, blades = algebra
        test_array = MVArray([layout.randomMV() for i in range(100)])

        normed_array = test_array.normal()
        other_array = np.array([t.normal().value for t in test_array])
        np.testing.assert_almost_equal(normed_array.value, other_array)

        dual_array = test_array.dual()
        other_array_2 = np.array([t.dual().value for t in test_array])
        np.testing.assert_almost_equal(dual_array.value, other_array_2)

    def test_comparison_operators(self):
        layout, blades = Cl(3)
        e1 = blades['e1']
        e2 = blades['e2']

        pytest.raises(TypeError, operator.lt, e1, e2)
        pytest.raises(TypeError, operator.le, e1, e2)
        pytest.raises(TypeError, operator.gt, e1, e2)
        pytest.raises(TypeError, operator.ge, e1, e2)

        assert operator.eq(e1, e1) == True
        assert operator.eq(e1, e2) == False
        assert operator.ne(e1, e1) == False
        assert operator.ne(e1, e2) == True

        assert operator.eq(e1, None) == False
        assert operator.ne(e1, None) == True

    def test_layout_comparison_operators(self):
        l3a, _ = Cl(3)
        l3b, _ = Cl(3)
        l4, _ = Cl(4)

        assert operator.eq(l3a, l3b) == True
        assert operator.eq(l3a, l4) == False
        assert operator.eq(l3a, None) == False

        assert operator.ne(l3a, l3b) == False
        assert operator.ne(l3a, l4) == True
        assert operator.ne(l3a, None) == True

    def test_mv_str(self):
        """ Test the __str__ magic method """
        layout, blades = Cl(3)
        e1 = blades['e1']
        e2 = blades['e2']
        e12 = blades['e12']

        assert str(e1) == "(1^e1)"
        assert str(1 + e1) == "1 + (1^e1)"
        assert str(-e1) == "-(1^e1)"
        assert str(1 - e1) == "1 - (1^e1)"

    def test_add_preserves_dtype(self):
        """ test that adding blades does not promote types """
        layout, blades = Cl(3)
        e1 = blades['e1']
        e2 = blades['e2']
        assert (e1 + 1).value.dtype == e1.value.dtype
        assert (e1 + e2).value.dtype == e1.value.dtype

    def test_indexing_blade_tuple(self):
        # gh-151
        layout, blades = Cl(3)
        mv = layout.MultiVector(value=np.arange(2**3) + 1)

        # one swap makes the sign flip
        assert mv[1, 2] == -mv[2, 1]
        assert mv[2, 3] == -mv[3, 2]
        assert mv[3, 1] == -mv[1, 3]

        assert mv[1, 2, 3] == -mv[2, 1, 3]
        assert mv[1, 2, 3] == -mv[1, 3, 2]

        # two swaps does not
        assert mv[1, 2, 3] == mv[2, 3, 1] == mv[3, 1, 2]
        assert mv[3, 2, 1] == mv[2, 1, 3] == mv[1, 3, 2]

        # three swaps does
        assert mv[1, 2, 3] == -mv[3, 2, 1]


class TestBasicConformal41:
    def test_metric(self):
        layout = Cl(4, 1)[0]
        e1 = layout.blades['e1']
        e2 = layout.blades['e2']
        e3 = layout.blades['e3']
        e4 = layout.blades['e4']
        e5 = layout.blades['e5']

        assert (e1 * e1)[0] == 1
        assert (e2 * e2)[0] == 1
        assert (e3 * e3)[0] == 1
        assert (e4 * e4)[0] == 1
        assert (e5 * e5)[0] == -1


    def test_factorise(self):
        layout_a = Cl(3)[0]
        layout,blades,stuff = conformalize(layout_a)
        e1 = layout.blades['e1']
        e2 = layout.blades['e2']
        e3 = layout.blades['e3']
        e4 = layout.blades['e4']
        e5 = layout.blades['e5']

        up = stuff['up']

        blade = up(e1 + 3*e2 + 4*e3)^up(5*e1 + 3.3*e2 + 10*e3)^up(-13.1*e1)

        basis, scale = blade.factorise()
        new_blade = (reduce(lambda a, b: a^b, basis)*scale)
        print(new_blade)
        print(blade)
        np.testing.assert_almost_equal(new_blade.value, blade.value, 5)


    def test_gp_op_ip(self):
        layout = Cl(4, 1)[0]
        e1 = layout.blades['e1']
        e2 = layout.blades['e2']
        e3 = layout.blades['e3']
        e4 = layout.blades['e4']
        e5 = layout.blades['e5']

        e123 = layout.blades['e123']
        np.testing.assert_almost_equal(e123.value, (e1 ^ e2 ^ e3).value)
        np.testing.assert_almost_equal(e123.value, (e1 * e2 * e3).value)

        e12345 = layout.blades['e12345']
        np.testing.assert_almost_equal(e12345.value, (e1 ^ e2 ^ e3 ^ e4 ^ e5).value)
        np.testing.assert_almost_equal(e12345.value, (e1 * e2 * e3 * e4 * e5).value)

        e12 = layout.blades['e12']
        np.testing.assert_almost_equal(-e12.value, (e2 ^ e1).value)

        t = np.zeros(32)
        t[0] = -1
        np.testing.assert_almost_equal(t, (e12*e12).value)

    def test_categorization(self):
        layout = Cl(3)[0]
        e1 = layout.blades['e1']
        e2 = layout.blades['e2']
        e3 = layout.blades['e3']

        blades = [
            layout.scalar,
            e1,
            e1 ^ e2,
            (e1 + e2) ^ e2,
        ]
        for b in blades:
            # all invertible blades are also versors
            assert b.isBlade()
            assert b.isVersor()

        versors = [
            1 + (e1^e2),
            e1 + (e1^e2^e3),
        ]
        for v in versors:
            assert not v.isBlade()
            assert v.isVersor()

        neither = [
            layout.scalar*0,
            1 + e1,
            1 + (e1^e2^e3)
        ]
        for n in neither:
            assert not n.isBlade()
            assert not n.isVersor()

    def test_blades_of_grade(self):
        layout = Cl(3)[0]
        e1 = layout.blades['e1']
        e2 = layout.blades['e2']
        e3 = layout.blades['e3']
        assert layout.blades_of_grade(1) == [e1, e2, e3]
        assert layout.blades_of_grade(2) == [e1^e2, e1^e3, e2^e3]
        assert layout.blades_of_grade(3) == [e1^e2^e3]

class TestBasicSpaceTime:
    def test_initialise(self):

        # Dirac Algebra  `D`
        D, D_blades = Cl(1, 3, names='d', firstIdx=0)

        # Pauli Algebra  `P`
        P, P_blades = Cl(3, names='p')

        # put elements of each in namespace
        locals().update(D_blades)
        locals().update(P_blades)


class TestBasicAlgebra:

    def test_gp_op_ip(self):
        layout = Cl(3)[0]
        e1 = layout.blades['e1']
        e2 = layout.blades['e2']
        e3 = layout.blades['e3']

        print('outer product')
        e123 = layout.blades['e123']
        np.testing.assert_almost_equal(e123.value, (e1 ^ e2 ^ e3).value)
        np.testing.assert_almost_equal(e123.value, (e1 * e2 * e3).value)

        print('outer product ordering')
        e12 = layout.blades['e12']
        np.testing.assert_almost_equal(-e12.value, (e2 ^ e1).value)

        print('outer product zeros')
        np.testing.assert_almost_equal(0, (e1 ^ e1).value)
        np.testing.assert_almost_equal(0, (e2 ^ e2).value)
        np.testing.assert_almost_equal(0, (e3 ^ e3).value)

        print('scalar outer product')
        np.testing.assert_almost_equal(((1 + 0 * e1) ^ (1 + 0 * e1)).value, (1 + 0 * e1).value)

        print('scalar inner product')
        np.testing.assert_almost_equal(((1 + 0 * e1) | (1 + 0 * e1)).value, 0)

    @pytest.fixture(
        params=[Cl(i) for i in [3, 4]] + [conformalize(Cl(3)[0])],
        ids=['Cl(3)', 'Cl(4)', 'conformal Cl(3)']
    )
    def algebra(self, request):
        return request.param

    def test_grade_obj(self, algebra):
        layout = algebra[0]
        for i in range(len(layout.sig)+1):
            mv = layout.randomMV()(i)
            assert i == grade_obj(mv)

    def test_left_multiplication_matrix(self, algebra):
        layout = algebra[0]
        for i in range(1000):
            mv = layout.randomMV()
            mv2 = layout.randomMV()
            np.testing.assert_almost_equal(np.matmul(layout.get_left_gmt_matrix(mv),mv2.value), (mv*mv2).value)


    def test_right_multiplication_matrix(self, algebra):
        layout = algebra[0]
        for i in range(1000):
            a = layout.randomMV()
            b = layout.randomMV()
            b_right = layout.get_right_gmt_matrix(b)
            res = a*b
            res2 = layout.MultiVector(value=b_right@a.value)
            np.testing.assert_almost_equal(res.value, res2.value)


class TestFrame:

    def check_inv(self, A):
        Ainv = None
        for k in range(3):
            try:
                Ainv = A.inv
            except ValueError:
                pass
        if Ainv is None:
            return
        for m, a in enumerate(A):
            for n, b in enumerate(A.inv):
                if m == n:
                    assert(a | b == 1)
                else:
                    assert(a | b == 0)

    @pytest.mark.parametrize(('p', 'q'), [
        (2, 0), (3, 0), (4, 0)
    ])
    def test_frame_inv(self, p, q):
        layout, blades = Cl(p, q)
        A = Frame(layout.randomV(p + q))
        self.check_inv(A)

    @pytest.mark.parametrize(('p', 'q'), [
        (2, 0), (3, 0), (4, 0)
    ])
    def test_innermorphic(self, p, q):
        layout, blades = Cl(p, q)

        A = Frame(layout.randomV(p+q))
        R = layout.randomRotor()
        B = Frame([R*a*~R for a in A])
        assert A.is_innermorphic_to(B)
