metadata = {
    'protocolName': 'Normalization',
    'author': 'Blaise Mariner <blaisemariner17@gmail.com>',
    'source': 'Blaise',
    'apiLevel': '2.16'
}

def run(ctx):

    #The first thing you MUST do before uploading this script into the OT-2 is to generate the dictionaries that tell the robot how much liquid to pipette where
    #This is done by running the Generate_dictionaries_for_pooling-240208.jpy and copy/pasting the result here:
    ##############################################################
    ############### PASTE BELOW THESE HASHTAGS ###################
    ### (see normalization-with-csv-240208-blm.py for example) ###
    ##############################################################

    source_well_to_destination_well_dictionary = {'A1': 'A1', 'B2': 'B2', 'C3': 'C3', 'D4': 'D4', 'E5': 'E5'}
    water_addition_dictionary =  {'B1': '0', 'C2': '5', 'D3': '10', 'E4': '24', 'F5': '26'}
    DNA_addition_dictionary =  {'A1': '26', 'B2': '21', 'C3': '16', 'D4': '2', 'E5': '0'}


    #Python is white-space sensitive, it is essential that only one single tab precedes these variables.
    ##############################################################
    ##############################################################
    ##############################################################

    #setting robot max speeds
    Default_max_speeds = {'X': 100, 'Y': 100, 'Z': 100, 'A': 100}

    #define the locations of the containers and instruments
    #create custom labware here: https://labware.opentrons.com/create/
    tiprack_200_1 = ctx.load_labware("opentrons_96_filtertiprack_200ul", 10)
    tiprack_200_2 = ctx.load_labware("opentrons_96_filtertiprack_200ul", 7)
    tiprack_20_1 = ctx.load_labware("opentrons_96_filtertiprack_20ul", 11)
    tiprack_20_2 = ctx.load_labware("opentrons_96_filtertiprack_20ul", 8)
    water_container = ctx.load_labware('agilent_1_reservoir_290ml', 5).wells()[0]
    source_plate = ctx.load_labware("biorad_96_wellplate_200ul_pcr", 3)
    destination_plate = ctx.load_labware("biorad_96_wellplate_200ul_pcr", 6)

    #the right pipette is 20ul and the left one is 200ul
    pipette_20 = ctx.load_instrument('p20_single_gen2', 'right', tip_racks=[tiprack_20_1, tiprack_20_2])
    pipette_200 = ctx.load_instrument('p300_single_gen2', 'left', tip_racks=[tiprack_200_1, tiprack_200_2])

    #flow rates at ul/second
    pipette_20.flow_rate.aspirate = 2
    pipette_20.flow_rate.dispense = 2
    pipette_20.flow_rate.blow_out = 2
    pipette_200.flow_rate.aspirate = 20
    pipette_200.flow_rate.dispense = 20
    pipette_200.flow_rate.blow_out = 20
    
    #first, the water step-- we only need one tip for this so I will pick up the tip before the loop and then drop it after the loop
    # this loop gets water from the water_container and dispenses it into the destination_plate wells
    pipette_200.pick_up_tip()
    pipette_20.pick_up_tip()

    for destination_well_oi, water_volume_oi in water_addition_dictionary.items():
        water_volume_oi = float(water_volume_oi)
        if water_volume_oi < 2:
            ctx.comment("Water volume to be pipetted is less than 2ul, so it is being skipped...")
            continue

        #get the right pipette for the job
        if water_volume_oi > 20:
            pipette_oi = pipette_200
        else:
            pipette_oi = pipette_20

        pipette_oi.aspirate(water_volume_oi, water_container)
        ctx.delay(seconds=0.2)
        pipette_oi.dispense(water_volume_oi, destination_plate.wells_by_name()[destination_well_oi])
        ctx.delay(seconds=0.2)
        pipette_oi.blow_out()
        pipette_oi.touch_tip()
        ctx.delay(seconds=0.2)
    
    pipette_200.drop_tip()
    pipette_20.drop_tip()

    #now we can pipette the DNA from the source_plate wells to the destination_plate wells
    for source_well_oi, dna_volume_oi in DNA_addition_dictionary.items():
        destination_well_oi = source_well_to_destination_well_dictionary[source_well_oi]
        dna_volume_oi = float(dna_volume_oi)
        if dna_volume_oi < 2:
            ctx.comment("DNA volume to be pipetted is less than 2ul, so it is being skipped...")
            continue

        #get the right pipette for the job
        if dna_volume_oi > 20:
            pipette_oi = pipette_200
        else:
            pipette_oi = pipette_20

        pipette_oi.pick_up_tip()

        pipette_oi.aspirate(dna_volume_oi, source_plate.wells_by_name()[source_well_oi])
        ctx.delay(seconds=0.2)
        pipette_oi.dispense(dna_volume_oi, destination_plate.wells_by_name()[destination_well_oi])
        ctx.delay(seconds=0.2)
        pipette_oi.blow_out()
        pipette_oi.touch_tip()
        ctx.delay(seconds=0.2)

        pipette_oi.drop_tip()
