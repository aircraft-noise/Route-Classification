import csv



def obslistmaker():
    obs_list = []
    with open('virtual_observers.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        counter = 0

        for row in reader:
            obs_line = ()
            if counter != 0:
                print(row)
                name = str(row[0])
                latitude = float(row[1])
                longitude = float(row[2])
                elevation = float(row[3])
                obs_line = (name, latitude, longitude, elevation)
                obs_list.append(obs_line)
            counter += 1
    return obs_list

