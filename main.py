from SVGRenderer import SVGRenderer
import sys
import os


def main():
    if len(sys.argv) != 2:
        print("You must specify a svg file!")
        return
    elif not sys.argv[1].endswith(".svg"):
        print("You must input a .svg file!")
        return
    elif not os.path.exists(sys.argv[1]):
        print("File does not exist!")
        return

    name = os.path.basename(sys.argv[1]).split('.')[-2]
    r = SVGRenderer()
    r.load(sys.argv[1])
    r.render(name + '.png')


if __name__ == "__main__":
    main()