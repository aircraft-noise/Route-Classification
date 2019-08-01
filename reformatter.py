import json

def reformat(input_date):
    print("Reformatting Sightings file")
    jsonFile = "./Data Sets by Date/" + input_date + "/FA_Sightings." + input_date + ".airport_ids.json.txt"
    jsonFile_new = "./Data Sets by Date/" + input_date + "/FA_Sightings_new." + input_date + ".airport_ids.json.txt"
    Flights = []
    with open(jsonFile) as f:
        data = json.load(f)

        master_buffer = data['aircraft']

        for each_icao in master_buffer:
            count = 0
            icao_metadata = {}
            for each_data in master_buffer[each_icao]:
                if count == 0:
                    icao_metadata = each_data
                else:
                    for each_segment, flight_data in zip(each_data[:-1], each_data[1:]):
                        alldata = {}
                        alldata['flight'] = each_segment['flight']
                        icao_metadata.update(each_segment)
                        alldata['metadata'] = icao_metadata
                        alldata['positions'] = flight_data
                        Flights.append(alldata)
                count += 1

    with open(jsonFile_new, 'w') as f2:  # writing JSON object
        json.dump(Flights, f2)

    print("Sightings File reformatted")


target_date_input = input('Enter the target date (yymmdd): ')
reformat(target_date_input)