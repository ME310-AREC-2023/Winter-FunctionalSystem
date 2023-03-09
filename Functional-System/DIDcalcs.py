def body_center(points):
    xb = 0
    yb = 0
    s2 = 0
    for point in points:
        q = point[0]
        x_p = point[1]
        y_p = point[2]
        xb = xb + x_p / (q ** 2)
        yb = yb + y_p / (q ** 2)
        s2 = s2 + 1 / (q ** 2)
    xb = xb/s2
    yb = yb/s2
    return xb, yb, s2


def dispersion(points, xb, yb, s2):
    d = 0
    for point in points:
        q = point[0]
        x_p = point[1]
        y_p = point[2]
        r2 = (xb - x_p)**2 + (yb - y_p)**2
        d = d + r2 / (q ** 2)
    d_out = math.sqrt(d/s2)
    return d_out

if __name__ == '__main__':
    points = file_read()
    xb, yb, s2 = body_center(points)
    d_out = dispersion(points, xb, yb, s2)
    print(xb, yb, s2, d_out)