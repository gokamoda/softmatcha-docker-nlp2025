from argparse import ArgumentParser, Namespace

from softmatcha.cli.build_inverted_index import get_argparser, main




if __name__ == "__main__":
    args = get_argparser().parse_args()
    main(args)
