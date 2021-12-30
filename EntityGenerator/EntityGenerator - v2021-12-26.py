from sys import hexversion
import time
import math
import chevron
from contextlib import redirect_stdout

# Read config file to get pm_normalViewHeight, input templates, and output files
with open("config.txt", 'r') as configFile:
     buffer = configFile.readlines()
     output1 = str(buffer[0].replace("OutputMain=", "")).rstrip("\n") # Main output for generated entities
     output2 = str(buffer[1].replace("Output2=", "")).rstrip("\n") # Additional output for generated entities
     output3 = str(buffer[2].replace("Output3=", "")).rstrip("\n") # Additional output for generated entities
     pmNormalViewHeight = float(str(buffer[3].replace("pm_normalViewHeight=", "")).rstrip("\n")) # pm_normalViewHeight
     MHNodeTemplate = str(buffer[4].replace("MHNodeTemplate=", "")).rstrip("\n") # MH Node template
     SpawnTargetTemplate = str(buffer[5].replace("SpawnTargetTemplate=", "")).rstrip("\n") # Spawn Target template
     MarkerTemplate = str(buffer[6].replace("MarkerTemplate=", "")).rstrip("\n") # GUI Text template
     SpawnGroupTemplate1 = str(buffer[7].replace("SpawnGroupTemplate1=", "")).rstrip("\n") # Spawn Group template 1
     SpawnGroupTemplate2 = str(buffer[8].replace("SpawnGroupTemplate2=", "")).rstrip("\n") # Spawn Group template 2
     TraversalChainTemplate = str(buffer[9].replace("TraversalChainTemplate=", "")).rstrip("\n") # Traversal Chain template
     TeleporterTemplate = str(buffer[10].replace("TeleporterTemplate=", "")).rstrip("\n") # Teleporter template
     ShockTrapTemplate = str(buffer[11].replace("ShockTrapTemplate=", "")).rstrip("\n") # Shock Trap template

print("EntityGenerator v0.1 by beth")
time.sleep(0.3)

# Ask user if they want to clear the output file, then clear it if the option was selected
clearOutput = input("\nClear the output files from previous sessions? (Y/N): ");
if clearOutput == 'y' or clearOutput == 'Y':
    with open(output1, 'w') as outFile:
        outFile.write("")
        outFile.close()
    with open(output2, 'w') as outFile:
        outFile.write("")
        outFile.close()

# Select entity type to generate
entityType = int(input("\nEntity type to generate: \n1: MH Node\n2: Spawn Target\n3: Spawn Group\n4: Traversal Chain (WIP)\n5: Teleporter\n6: Shock Trap\n"))
#while True:
#    if entityType > 6 or entityType < 1:
#        entityType = int(input("Invalid option, try again: ")
#    else:
#        break

# Used to loop main function
dontExit = True;

# pitch yaw roll to spawnOrientation matrix from Zandy
def sin_cos(deg):
    rad = math.radians(float(deg))
    return math.sin(rad), math.cos(rad)

def angle_to_mat3(x, y, z): # yaw, pitch, roll
    sy, cy = sin_cos(x)
    sp, cp = sin_cos(y)
    sr, cr = sin_cos(z)

    return [
        cp * cy,
        cp * sy,
        -sp,
        sr * sp * cy + cr * -sy,
        sr * sp * sy + cr * cy,
        sr * cp,
        cr * sp * cy + -sr * sy,
        cr * sp * sy + -sr * cy,
        cr * cp,
    ]

# Function to round the given value to the nearest specified interval
def roundToInterval (inputValue, interval):
    return round (inputValue / interval) * interval

# Convert a hex colour to RGB normalized decimals 9326ff
def hexToFloatColour(hexVal):
    rgb = tuple(int(hexVal[i:i+2], 16) for i in (0, 2, 4))
    print(rgb)
    return [
        float(rgb[0]/255),
        float(rgb[1]/255),
        float(rgb[2]/255)
    ]

# Generate MH Node
def generateMHNode(
    entityNameNumber,
    currentEntityTemplate,
    output1
    ):
    
    # Get coords
    coords = list(map(float, input("Enter coords: ").split()));
    
    # Leading zeros padding
    entityNameString = str(entityNameNumber).zfill(3)

    # Round yaw value to nearest 10°, then offset by 90° so that the entity will face the player's direction
    #yaw = roundToInterval(coords[3], 10) + 90
    yaw = coords[3] + 90

    entityOrientation = angle_to_mat3(yaw, 0, 0)
    print(entityOrientation)

    # args to pass into the templates
    args = {
        'entityDefNum': entityNameString,
        'coordX': coords[0],
        'coordY': coords[1],
        'coordZ': coords[2],
        'yaw' : yaw,
        'mat0X' : entityOrientation[0],
        'mat0Y' : entityOrientation[1],
        'mat0Z' : entityOrientation[2],
        'mat1X' : entityOrientation[3],
        'mat1Y' : entityOrientation[4],
        'mat1Z' : entityOrientation[5],
        'mat2X' : entityOrientation[6],
        'mat2Y' : entityOrientation[7],
        'mat2Z' : entityOrientation[8]
    }
    
    # Open templates and pass through args
    with open(currentEntityTemplate, 'r') as entityTemplate:
        generatedEntity1 = chevron.render(entityTemplate, args)
        print(generatedEntity1) # print generated entity 
    
    # Call function to write generated entities to file
    writeStuffToFile(generatedEntity1, output1)

# Generate spawn targets and GUIText markers
def generateSpawnTarget(
    entityNameNumber,
    generateMarkers,
    template1,
    template2,
    output1,
    output2
    ):
    
    # get coords
    coords = list(map(float, input("Enter entity coordinates: ").split()));
    
    # leading zeros padding
    entityNameString = str(entityNameNumber).zfill(3)
    
    # args to pass into the templates
    spawnTargetArgs = {
        'entityDefNum': entityNameString,
        'coordX': coords[0],
        'coordY': coords[1],
        'coordZ': coords[2] - pmNormalViewHeight # pm_NormalViewHeight full compensation, so the spawn target rests on the ground
    }
    markerArgs = {
        'entityDefNum': entityNameString,
        'coordX': coords[0],
        'coordY': coords[1],
        'coordZ': coords[2] - pmNormalViewHeight + 0.5 # pm_NormalViewHeight partial compensation, so the marker is slightly raised above ground
    }
    
    # Open templates and pass through args
    with open(template1, 'r') as spawnTargetTemplate:
        spawnTargetTemplateOutput = chevron.render(spawnTargetTemplate, spawnTargetArgs)
        print(spawnTargetTemplateOutput) # print generated spawn target
    with open(template2, 'r') as markerTemplate:
        generatedEntity2 = chevron.render(markerTemplate, markerArgs)
    
    # Call function to write generated entities to file
    writeStuffToFileAlt(generateMarkers, spawnTargetTemplateOutput, generatedEntity2, output1, output2)

# Generate spawn groups
def generateSpawnGroup(
    template1,
    template2,
    output1
    ):
    
    # Ask user what to append to the spawn group name, and make a duplicate with underscores in place of spaces
    encounterName = input("\nName of encounter: ");
    encounterNameFormatted = encounterName.replace(" ", "_")

    # Ask user for the numbering of the first and last spawn target they're adding
    startSpawnTargetNum = int(input("First spawn target: "));
    endSpawnTargetNum = int(input("Last spawn target: "));

    totalItems = int(endSpawnTargetNum - startSpawnTargetNum + 1);

    tempStartNum = startSpawnTargetNum;
    tempStartString = "";
    bufferString = "";

    # Stuff to pass into the main template
    mainArgs = {
        'encounterName' : encounterName,
        'encounterNameFormatted' : encounterNameFormatted,
        'totalItems': totalItems
    }

    # Open template and pass through args
    with open(template1, 'r') as spawnGroupTemplate:
        spawnGroupTemplateOutput = chevron.render(spawnGroupTemplate, mainArgs)
        print(spawnGroupTemplateOutput) # print generated entity
    
    # Call function to write generated entities to file
    writeStuffToFile(spawnGroupTemplateOutput, output1)

    for tempIndex in range(1, totalItems + 1):
        tempStartString = str(tempStartNum).zfill(3);
        # Stuff to pass into the secondary template
        secondaryArgs = {
            'index': tempIndex - 1,
            'itemNum': tempStartString
        }
        with open(template2, 'r') as secondaryTemplate:
            secondaryOutput = chevron.render(secondaryTemplate, secondaryArgs)
        print(secondaryOutput)
        writeStuffToFile(secondaryOutput, output1)
        tempStartNum += 1;
    writeStuffToFile('		}\n	}\n}\n}', output1)
    print('		}\n	}\n}\n}')

# Generate traversal chains
def generateTraversalChain(
    isOnCeiling,
    entityNameNumber,
    template1,
    output1
    ):
    
    # Get coords
    startCoords = list(map(float, input("Start coords: ").split()));
    midCoords = list(map(float, input("Mid coords: ").split()));
    endCoords = list(map(float, input("End coords: ").split()));
    
    # leading zeros padding
    entityNameString = str(entityNameNumber).zfill(3)
    
    if isOnCeiling == 'Y' or isOnCeiling == 'y':
        ceilingCompensation = 0.5;
    else:
        ceilingCompensation = 0 - pmNormalViewHeight
    
    yaw = roundToInterval(midCoords[3], 5)
    pitch = roundToInterval(midCoords[4], 5)

    entityOrientation = angle_to_mat3(yaw, pitch, 0)

    # args to pass into the templates
    entityArgs = {
        'entityNumber': entityNameString,
        'startCoordX': startCoords[0],
        'startCoordY': startCoords[1],
        'startCoordZ': startCoords[2] - pmNormalViewHeight, # pm_NormalViewHeight full compensation, so the entity rests on the ground
        'midCoordX': midCoords[0],
        'midCoordY': midCoords[1],
        'midCoordZ': midCoords[2] + ceilingCompensation, # Ceiling compensation
        'endCoordX': endCoords[0],
        'endCoordY': endCoords[1],
        'endCoordZ': endCoords[2] - pmNormalViewHeight, # pm_NormalViewHeight full compensation, so the entity rests on the ground
        'yaw' : yaw,
        'pitch' : pitch,
        'mat0X' : entityOrientation[0],
        'mat0Y' : entityOrientation[1],
        'mat0Z' : entityOrientation[2],
        'mat1X' : entityOrientation[3],
        'mat1Y' : entityOrientation[4],
        'mat1Z' : entityOrientation[5],
        'mat2X' : entityOrientation[6],
        'mat2Y' : entityOrientation[7],
        'mat2Z' : entityOrientation[8]
    }
    
    # Open templates and pass through args
    with open(template1, 'r') as entityTemplate:
        entityTemplateOutput = chevron.render(entityTemplate, entityArgs)
        print(entityTemplateOutput) # print generated entity
    
    # Call function to write generated entities to file
    writeStuffToFile(entityTemplateOutput, output1)

# Generate Teleporter + Emitter + Destination
def generateTeleporter(
    entityNameNumber,
    currentEntityTemplate,
    output1
    ):
    
    # Get coords
    coordsStart = list(map(float, input("Starting coords: ").split()));
    coordsEnd = list(map(float, input("Destination coords: ").split()));

    hexVal = input("Portal colour in hex: #") # 9326ff
    colourFloat = hexToFloatColour(hexVal)
    
    # Leading zeros padding
    entityNameString = str(entityNameNumber).zfill(3)

    # Round yaw value to nearest 5° (0 yaw+90 90)
    yawStart = roundToInterval(coordsStart[3], 5)
    yawEmit = roundToInterval(coordsStart[3], 5) + 90
    yawDest = roundToInterval(coordsEnd[3], 5)
    rollEmit = 90

    startOrientation = angle_to_mat3(yawStart, 0, 0)
    emitOrientation = angle_to_mat3(yawEmit, 0, 90)
    destOrientation = angle_to_mat3(yawDest, 0, 0)

    # args to pass into the templates
    args = {
        'entityNumber': entityNameString,
        'coordX': coordsStart[0],
        'coordY': coordsStart[1],
        'coordZ': coordsStart[2] - pmNormalViewHeight,
        'coordZEmit': coordsStart[2],
        'coordXDest': coordsEnd[0],
        'coordYDest': coordsEnd[1],
        'coordZDest': coordsEnd[2] - pmNormalViewHeight,
        'yawStart' : yawStart,
        'yawEmit' : yawEmit,
        'yawDest' : yawDest,
        'rollEmit' : rollEmit,
        'hexVal' : hexVal,
        'floatColourR' : colourFloat[0],
        'floatColourG' : colourFloat[1],
        'floatColourB' : colourFloat[2],
        'mat0XStart' : startOrientation[0],
        'mat0YStart' : startOrientation[1],
        'mat0ZStart' : startOrientation[2],
        'mat1XStart' : startOrientation[3],
        'mat1YStart' : startOrientation[4],
        'mat1ZStart' : startOrientation[5],
        'mat2XStart' : startOrientation[6],
        'mat2YStart' : startOrientation[7],
        'mat2ZStart' : startOrientation[8],
        'mat0XEmit' : emitOrientation[0],
        'mat0YEmit' : emitOrientation[1],
        'mat0ZEmit' : emitOrientation[2],
        'mat1XEmit' : emitOrientation[3],
        'mat1YEmit' : emitOrientation[4],
        'mat1ZEmit' : emitOrientation[5],
        'mat2XEmit' : emitOrientation[6],
        'mat2YEmit' : emitOrientation[7],
        'mat2ZEmit' : emitOrientation[8],
        'mat0XDest' : destOrientation[0],
        'mat0YDest' : destOrientation[1],
        'mat0ZDest' : destOrientation[2],
        'mat1XDest' : destOrientation[3],
        'mat1YDest' : destOrientation[4],
        'mat1ZDest' : destOrientation[5],
        'mat2XDest' : destOrientation[6],
        'mat2YDest' : destOrientation[7],
        'mat2ZDest' : destOrientation[8]
    }
    
    # Open templates and pass through args
    with open(currentEntityTemplate, 'r') as entityTemplate:
        generatedEntity1 = chevron.render(entityTemplate, args)
        print(generatedEntity1) # print generated entity 
    
    # Call function to write generated entities to file
    writeStuffToFile(generatedEntity1, output1)

# Generate shock trap
def generateShockTrap(
    template1,
    output1
    ):
    
    instanceID = input("\nEnter instance ID: ")
    coords = list(map(float, input("Enter entity coordinates: ").split()));
    
    # args to pass into the templates
    args = {
        'instanceID' : instanceID,
        'coordX': coords[0],
        'coordY': coords[1],
        'coordZ': coords[2] - pmNormalViewHeight,
        'coordZ1': coords[2] - pmNormalViewHeight + 0.25,
        'coordZ2': coords[2] - pmNormalViewHeight - 1.060002,
        'coordZ3': coords[2] - pmNormalViewHeight + 2.885204,
        'coordZ4': coords[2] - pmNormalViewHeight + 1.5,
        'coordZ5': coords[2] - pmNormalViewHeight + 3.320293
    }
    
    # Open templates and pass through args
    with open(template1, 'r') as entityTemplate:
        generatedEntity = chevron.render(entityTemplate, args)
        print(generatedEntity) # print generated entity
    
    # Call function to write generated entities to file
    writeStuffToFile(generatedEntity, output1)

# Function to write generated entities to file
def writeStuffToFile(
    generatedEntity1,
    output1
    ):

    # Open output txt and write spawn targets to file
    with open(output1, 'a') as outFileTargets:
        outFileTargets.write("\n" + generatedEntity1)

# Alt function, to avoid rewriting existing function to support more in/outputs. Remember to consolidate them later!
def writeStuffToFileAlt(
    generateMarkers,
    generatedEntity1,
    generatedEntity2,
    output1,
    output2
    ):

    # Open output txt and write spawn targets to file
    with open(output1, 'a') as outFileTargets:
        outFileTargets.write("\n" + generatedEntity1)
                
    # Open output text file and write generated spawn target markers if option was selected
    if generateMarkers == "y" or generateMarkers == "Y":
        with open(output2, 'a') as outFileMarkers:
                outFileMarkers.write("\n" + generatedEntity2);

# Loop functions to generate entities and write them to file
if entityType == 1:
    entityNameNumber = int(input("\nSet entity numbering start value: ")); # # Set number to append at end of entity name
    while dontExit:
        generateMHNode(entityNameNumber, MHNodeTemplate, output1);
        entityNameNumber += 1; # increment by 1 after every generated entity
elif entityType == 2:
    generateMarkers = input("\nGenerate markers for the spawn targets? (Y/N): "); # Ask user if they want to generate markers
    entityNameNumber = int(input("Set entity numbering start value: ")); # # Set number to append at end of entity name
    while dontExit:
        generateSpawnTarget(entityNameNumber, generateMarkers, SpawnTargetTemplate, MarkerTemplate, output1, output2);
        entityNameNumber += 1; # increment by 1 after every generated entity
elif entityType == 3:
    while dontExit:
        generateSpawnGroup(SpawnGroupTemplate1, SpawnGroupTemplate2, output1);
elif entityType == 4:
    isOnCeiling = input("\nIs the midpoint on the ceiling? (Y/N): ")
    entityNameNumber = int(input("Set entity numbering start value: ")); # # Set number to append at end of entity name
    while dontExit:
        generateTraversalChain(isOnCeiling, entityNameNumber, TraversalChainTemplate, output1);
        entityNameNumber += 1; # increment by 1 after every entity
elif entityType == 5:
    entityNameNumber = int(input("\nSet entity numbering start value: ")); # # Set number to append at end of entity name
    while dontExit:
        generateTeleporter(entityNameNumber, TeleporterTemplate, output1)
        entityNameNumber += 1; # increment by 1 after every entity
elif entityType == 6:
    while dontExit:
        generateShockTrap(ShockTrapTemplate, output1)
