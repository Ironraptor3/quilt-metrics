from sys import argv
import ntpath

'''
command line for non-normalized:
MPEG7.exe DCD 0 1 1 input output
'''
def main(txt, files, normalized, split):
    header = 'image,dominant_colors,spatial_coherence,color_intravariance'
    offset = 3
    spacing = 7
    n = 3

    div = 32 if normalized else 100

    print(header)
    dcd = [line.strip().split(split) for line in txt]
    for i in range(len(dcd)):
        image = files[i].strip()
        name = ntpath.basename(image)
        # Offset to avoid spacing shenanigans
        data = dcd[i][len(name.split(split))-1:]
        if len(data) > 3:
            # directly extract number of colors
            domColors = int(data[1])
            # out of 32
            sc = int(data[2]) / 32
            # calculate variance
            intravar = 0
            for i in range(domColors):
                i = i*spacing + offset
                # Percentage is out of div (32 or 100)
                p = int(data[i]) / (n*div)
                v = 0
                # Add all variance
                for j in range(n):
                    ind = i+j+4
                    v+=int(data[i+j+4])
                intravar += v*p
            print(f'{image},{str(domColors)},{str(sc)},{str(intravar)}')
    # Done

if __name__ == '__main__' and len(argv) > 2:
    with open(argv[1]) as f1:
        with open(argv[2]) as f2:
            normalized = True
            if len(argv) > 3:
                normalized = argv[3] == 'True'
            main(f1.readlines(), f2.readlines(), normalized, ' ')
