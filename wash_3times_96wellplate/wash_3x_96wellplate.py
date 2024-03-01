metadata = {
    'protocolName': 'Discard supernatent from magnetic 96 well plate',
    'author': 'Blaise Mariner <blaisemariner17@gmail.com>',
    'source': 'Blaise',
    'apiLevel': '2.16'
}

def run(ctx):

    wells_to_wash = ["A1","A2","A3","A4","A5","A6","A7","A8","A9","A10","A11","A12","B1","B2","B3","B4","B5","B6","B7","B8","B9","B10","B11","B12","C1","C2","C3","C4","C5","C6","C7","C8","C9","C10","C11","C12","D1","D2","D3","D4","D5","D6","D7","D8","D9","D10","D11","D12","E1","E2","E3","E4","E5","E6","E7","E8","E9","E10","E11","E12","F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12","G1","G2","G3","G4","G5","G6","G7","G8","G9","G10","G11","G12","H1","H2","H3","H4","H5","H6","H7","H8","H9","H10","H11","H12"]
    wash_plate = ctx.load_labware("biorad_96_wellplate_200ul_pcr", 6)
    etoh_container = ctx.load_labware('agilent_1_reservoir_290ml', 5).wells()[0]
        
    #setting robot max speeds
    Default_max_speeds = {'X': 150, 'Y': 150, 'Z': 100, 'A': 100}

    #define the locations of the containers and instruments
    #create custom labware here: https://labware.opentrons.com/create/
    tiprack_200_1 = ctx.load_labware("opentrons_96_filtertiprack_200ul", 10)
    tiprack_200_2 = ctx.load_labware("opentrons_96_filtertiprack_200ul", 7)

    #the right pipette is 20ul and the left one is 200ul
    pipette_200 = ctx.load_instrument('p300_single_gen2', 'left', tip_racks=[tiprack_200_1, tiprack_200_2])

    #flow rates at ul/second
    pipette_200.flow_rate.aspirate = 20
    pipette_200.flow_rate.dispense = 20
    pipette_200.flow_rate.blow_out = 20

    #3x washing
    for i in range(3):
      for well_oi in wells_to_wash:
          
          pipette_oi = pipette_200
  
          pipette_oi.pick_up_tip()
  
          pipette_oi.aspirate(100,etoh_container)
          ctx.delay(seconds=0.1)
          pipette_oi.dispense(100,wash_plate.wells(well_oi))  
          ctx.delay(seconds=0.1)
          pipette_oi.mix(4, 100, wash_plate.wells(well_oi))   # mix 4 times, 100uL, in wash_plate:well_oi
  
          pipette_oi.drop_tip()
