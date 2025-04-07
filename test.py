import csv

comma_line = ""
output = []
name_r = []
with open("./bls_data.txt", "r") as inp:
    for line in inp.readlines():
        if "," in line:
            comma_line = line
        elif "APU" in line and comma_line != "":
            name_val = comma_line.split(",")[0]
            if name_val in name_r:
                name_val = ":".join(comma_line.split(",")[0:2])
            if name_val in name_r:
                continue
            name_r .append(name_val)
            output.append([name_val, line[line.index("APU"):-1]])
            comma_line = ""


with open("bls_data_items.csv", 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(output)