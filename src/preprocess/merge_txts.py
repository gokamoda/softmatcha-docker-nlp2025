from argparse import ArgumentParser
import json



def main(args):
    file_paths = args.input_files
    file_paths.sort()

    line_to_file = {}
    merged_txt_file = args.output_file
    line_idx = 0

    with open(merged_txt_file, "w") as fo:
        for file_path in file_paths:
            with open(file_path) as fi:
                for line in fi:
                    if line == "\n":
                        continue
                    line = line.strip() + "\n"
                    assert len(line.split("\n")) == 2, line.split("\n")
                    line_to_file[line_idx] = file_path
                    fo.write(line)
                    line_idx += 1
    
    line_to_file_json = ".".join(merged_txt_file.split(".")[:-1]) + ".json"
    with open(line_to_file_json, "w") as fo:
        json.dump(line_to_file, fo)



if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("input_files", nargs="+")
    parser.add_argument("output_file")
    args = parser.parse_args()


    main(args)