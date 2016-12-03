import datetime
import glob, os

def filter_and_save():

    raw_lines = []

    try:
        with open("../../../TradingData/raw_industry_data.txt", 'r') as f_obj:
            raw_lines = f_obj.read();

        now = datetime.datetime.now()
        file_path = "../../../TradingData/" + "ibd_industries_{:d}{:d}{:d}.tls".format(now.year, now.month, now.day)

        lines_to_file = []

        for line in raw_lines.split():
            if line != 'Sym' and not line.isspace() and line.isupper():
                lines_to_file.append(line)

        print("Start saving to file ...")

        with open(file_path, 'w') as f_obj:
            for line_to_file in lines_to_file:
                f_obj.write(line_to_file + "\n")
            f_obj.write("SPY" + "\n")

        print("End writing to file")

    except Exception as e:
        print("Exception ", str(e))

def main():
    filter_and_save();

main()
