import cv2
import metrics

# Test cases for pattern functions

# Generate fake data
def gen_data():
    # a-b and c-d are relationships
    # a-c and b-d have are grouped

    # x,y,size,angle
    a = cv2.KeyPoint(0, 0, 1, 0)
    b = cv2.KeyPoint(1,1,0.5,90)
    c = cv2.KeyPoint(2,2,2,90)
    d = cv2.KeyPoint(4,4,1,180)

    # Hardcode arrays
    data = [a,b,c,d]
    points = [[0,2],[1,3]]

    return data, points

# Test normalize_point (works)
def test_normalize_point(data, points):
    # Same
    norm_0 = metrics.normalize_point(data, 0, 1)[0]
    norm_1 = metrics.normalize_point(data, 2, 3)[0]
    print(metrics.kp_str(norm_0))
    print(metrics.kp_str(norm_1))
    # Different
    norm_2 = metrics.normalize_point(data, 1, 2)[0]
    print(metrics.kp_str(norm_2))

# Test normalize_all (works)
def test_normalize_all(data, points):
    a = points[0]
    b = points[1]
    norm = metrics.normalize_all(data, a, b)
    for n in norm:
        print(f'n: {metrics.kp_str(n[0])}, p1:{n[1]}, p2:{n[2]}')

# Test compare_norm (works)
def test_compare_multi(data, points):
    norm = metrics.normalize_all(data, points[0], points[1])
    groups = metrics.compare_norm(norm, lambda x: x[0].size, None)
    for g in groups:
        for p in g:
            print(f'({metrics.kp_str(p[0])}, p1: {p[1]}, p2: {p[2]})')
        print()
    groups = metrics.compare_norm(norm, lambda x: x[0].pt[0], groups)
    # Pardon the copy paste
    for g in groups:
        for p in g:
            print(f'({metrics.kp_str(p[0])}, p1: {p[1]}, p2: {p[2]})')
        print()

if __name__ == '__main__':
    data, points = gen_data()
    test_compare_multi(data, points)
