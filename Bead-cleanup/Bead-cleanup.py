metadata = {
    'protocolName': 'Bead cleanup',
    'author': 'Blaise Mariner <blaisemariner17@gmail.com>',
    'source': 'Blaise',
    'apiLevel': '2.16'
}

def run(ctx):
	
    num_samp = int(8)
    num_col = int(num_samp/8)
    index_start_col = int(1)
    index_start_col = int(index_start_col)-1
    asp_height = int(1)
    length_from_side = int(1.5)

    # setting robot max speeds
    Default_max_speeds = {'X': 100, 'Y': 100, 'Z': 100, 'A': 100}

    # define the pipettes
    tiprack_200_1 = ctx.load_labware("opentrons_96_filtertiprack_200ul", 10)
    tiprack_200_2 = ctx.load_labware("opentrons_96_filtertiprack_200ul", 7)
    tiprack_20_1 = ctx.load_labware("opentrons_96_filtertiprack_20ul", 11)
    tiprack_20_2 = ctx.load_labware("opentrons_96_filtertiprack_20ul", 8)
    #the right pipette is 20ul and the left one is 200ul
    pipette_20 = ctx.load_instrument('p20_single_gen2', 'right', tip_racks=[tiprack_20_1, tiprack_20_2])
    pipette_200 = ctx.load_instrument('p300_single_gen2', 'left', tip_racks=[tiprack_200_1, tiprack_200_2])
    # flow rates at ul/second
    pipette_20.flow_rate.aspirate = 2
    pipette_20.flow_rate.dispense = 2
    pipette_20.flow_rate.blow_out = 2
    pipette_200.flow_rate.aspirate = 20
    pipette_200.flow_rate.dispense = 20
    pipette_200.flow_rate.blow_out = 20

    # load labware
    mag_module = ctx.load_module('magnetic module gen2', '1')
    sample_plate = mag_module.load_labware('biorad_96_wellplate_200ul_pcr')
    reagent_plate = ctx.load_labware('biorad_96_wellplate_200ul_pcr', '2')
    index_plate = ctx.load_labware('illumina_96_wellplate_200ul', '3')
    reservoir = ctx.load_labware('nest_12_reservoir_15ml', '4')

    source_well_to_destination_well_dictionary = {'A1': 'A1', 'B2': 'B2', 'C3': 'C3', 'D4': 'D4', 'E5': 'E5'}
    water_addition_dictionary =  {'A1': '0', 'B2': '5', 'C3': '10', 'D4': '24', 'E5': '26'}
    DNA_addition_dictionary =  {'A1': '26', 'B2': '21', 'C3': '16', 'D4': '2', 'E5': '0'}


    # reagents
    twb = reservoir.wells()[1]
    tsb = reagent_plate.rows()[0][1]
    epm = reagent_plate.rows()[0][2:4]
    waste = reservoir.wells()[11]
    # transfer tsb from mastermix plate to sample plate
    airgap = 5
    for col in sample_plate.rows()[0][:num_col]:

        if col + 5 > 20:
            pipette_oi = pipette_200
        else:
            pipette_oi = pipette_20

        pipette_oi.pick_up_tip()
        
        pipette_oi.aspirate(5, tsb)
        ctx.delay(seconds=0.2)
        pipette_oi.air_gap(airgap)
        pipette_oi.dispense(5+airgap, col)
        pipette_oi.mix(10, 17, col, rate=0.5)
        pipette_oi.blow_out()
        pipette_oi.touch_tip()
        ctx.delay(seconds=0.2)
        
        pipette_oi.drop_tip()

    ctx.pause(
    '''
        Seal the plate with Microseal 'B', place on the preprogrammed
        thermal cycler, and run the PTC program. Afterwards, place plate
        back on magnetic module and select "Resume" on the Opentrons App.
        Empty trash.
    '''
    )

    #3x wash
    for wash in range(3):
        mag_module.engage()
        ctx.delay(minutes=5)

        # remove supernatant
        ctx.comment('\n Removing Supernatant \n')
        for i, col in enumerate(sample_plate.rows()[0][:num_col]):
            pipette_200.pick_up_tip()
            remove_supernatant(30 if wash == 0 else 50, i, col)
            pipette_200.blow_out(col.top())
            pipette_200.return_tip()
        mag_module.disengage()

        # add 50ul of twb over beads and mix at bead location
        ctx.comment('\n Adding TWB \n')
        for i, col in enumerate(sample_plate.rows()[0][:num_col]):
            pipette_200.pick_up_tip()
            pipette_200.aspirate(50, twb)
            pipette_200.dispense(50, col)
            mix_at_beads(40, i, col)
        pipette_200.drop_tip()
