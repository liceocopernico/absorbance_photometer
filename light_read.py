TSL2561_CLIPPING_402MS:int=65000
TSL2561_LUX_CHSCALE:int=10
TSL2561_LUX_RATIOSCALE:int =9

def calculateLux(broadband:int,ir:int):
    clipThreshold = TSL2561_CLIPPING_402MS
    chScale = (1 << TSL2561_LUX_CHSCALE)
     
    channel0:int = (broadband * chScale) >> TSL2561_LUX_CHSCALE
    channel1:int = (ir * chScale) >> TSL2561_LUX_CHSCALE
    
    
    
    ratio:float=0
    lux:float=0
    if (channel0 != 0):
        ratio =channel1/channel0
    
      

    if ratio>0 and ratio <=0.5:
        lux=0.0304*channel0-0.062*channel0*pow(ratio,1.4)
    elif ratio>0.5 and ratio<=0.61:
        lux=0.0224*channel0-0.031*channel1
    elif ratio>0.61 and ratio <=0.80:
        lux=0.0128*channel0-0.0153*channel1
    elif ratio>0.80 and ratio <=1.30:
        lux=0.00146*channel0-0.00112*channel1
    elif ratio>1.30 and ratio <=3.00:
        lux=0.0002

    
    return lux




print(calculateLux(20,2))