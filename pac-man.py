def func(d: str, h, i):
    print(d, h, i)


def main():
    my = {"h": 1,
          "i": 2,
          "d": 3}
    my2 = [1, 2, 3, 5, 6, 7]

    l, *args, j = my2
    func(**my)
    print(l, j, args)
    func(2, 4, i=5)


if __name__ == "__main__":
    main()
