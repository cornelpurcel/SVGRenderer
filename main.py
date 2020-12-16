from SVGRenderer import SVGRenderer

def main():
    r = SVGRenderer()
    r.load("circles.svg")
    r.render()
    # print(r.getContents())



if __name__ == "__main__":
    main()