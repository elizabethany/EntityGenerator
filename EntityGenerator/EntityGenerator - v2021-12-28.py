from sys import hexversion
import time
import math
import chevron
from contextlib import redirect_stdout

# Read config file to get parameters, templates, and output files
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
     ShockTrapTemplate = str(buffer[11].replace("ShockTrapTemplate=", "")).rstrip("\n") # Shock Trap template (modified from Anny)
     distanceScale = float(str(buffer[12].replace("DistanceScale=", "")).rstrip("\n")) # Distance scalar for portal + spawn target combo (~anim distance / 50)
     PortalSpawnTargetTemplate = str(buffer[13].replace("PortalSpawnTargetTemplate=", "")).rstrip("\n") # Portal + spawn target combo template
     BFGTemplate = str(buffer[14].replace("BFGTemplate=", "")).rstrip("\n") # idProp2 BFG Ammo template
     BulletsTemplate = str(buffer[15].replace("BulletsTemplate=", "")).rstrip("\n") # idProp2 Bullet Ammo template
     CellsTemplate = str(buffer[16].replace("CellsTemplate=", "")).rstrip("\n") # idProp2 Plasma Cell Ammo template
     ShellsTemplate = str(buffer[17].replace("ShellsTemplate=", "")).rstrip("\n") # idProp2 Shells Ammo template
     Rockets_SingleTemplate = str(buffer[18].replace("Rockets_SingleTemplate=", "")).rstrip("\n") # idProp2 Single Rocket Ammo template

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

# Calculate side lengths based on given angle (yaw) and known hypotenuse (1 * distanceScale)
def hypotReverse(
    yaw
    ):
    
    yawRad = math.radians(yaw)
    deltaX = (math.cos(yawRad)) * distanceScale
    deltaY = (math.sin(yawRad)) * distanceScale
    return [
        roundToInterval(deltaX, 0.0001),
        roundToInterval(deltaY, 0.0001)
    ]

# Generate MH Node
def generateMHNode(
    ):
        
    entityNameNumber = int(input("\nSet entity numbering start value: ")); # # Set number to append at end of entity name

    while True:
        # Get coords
        coords = list(map(float, input("Enter coords: ").split()));
        
        # Leading zeros padding
        entityNameString = str(entityNameNumber).zfill(3)

        # Offset yaw by 90° so that the entity will face the player's direction
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
            'mat0X' : roundToInterval(entityOrientation[0], 0.0001), # Round to nearest one ten thousandth
            'mat0Y' : roundToInterval(entityOrientation[1], 0.0001),
            'mat0Z' : roundToInterval(entityOrientation[2], 0.0001),
            'mat1X' : roundToInterval(entityOrientation[3], 0.0001),
            'mat1Y' : roundToInterval(entityOrientation[4], 0.0001),
            'mat1Z' : roundToInterval(entityOrientation[5], 0.0001),
            'mat2X' : roundToInterval(entityOrientation[6], 0.0001),
            'mat2Y' : roundToInterval(entityOrientation[7], 0.0001),
            'mat2Z' : roundToInterval(entityOrientation[8], 0.0001)
        }
        
        # Open templates and pass through args
        with open(MHNodeTemplate, 'r') as entityTemplate:
            generatedEntity1 = chevron.render(entityTemplate, args)
            print(generatedEntity1) # print generated entity 
        
        # Call function to write generated entities to file
        writeStuffToFile(generatedEntity1, output1)

        entityNameNumber += 1; # increment by 1 after every generated entity

# Generate spawn targets and GUIText markers
def generateSpawnTarget(
    ):
    
    generateMarkers = input("\nGenerate markers for the spawn targets? (Y/N): "); # Ask user if they want to generate markers
    entityNameNumber = int(input("Set entity numbering start value: ")); # # Set number to append at end of entity name
    
    while True:
        # Get coords
        coords = list(map(float, input("Enter spawn target coordinates: ").split()));
        
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
        
        # Open spawn target template and pass through args, then wrtie to file
        with open(SpawnTargetTemplate, 'r') as entityTemplate1:
            generatedEntity1 = chevron.render(entityTemplate1, spawnTargetArgs)
            print(generatedEntity1) # print generated spawn target
        writeStuffToFile(generatedEntity1, output1)

        # Do the same for markers if the option was selected
        if generateMarkers == "y" or generateMarkers == "Y":
            with open(MarkerTemplate, 'r') as entityTemplate2:
                generatedEntity2 = chevron.render(entityTemplate2, markerArgs)
            writeStuffToFile(generatedEntity2, output2)
        entityNameNumber += 1; # increment by 1 after every generated entity

# Generate spawn groups
def generateSpawnGroup(
    ):

    while True:
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
        with open(SpawnGroupTemplate1, 'r') as spawnGroup_Template:
            spawnGroupTemplateOutput = chevron.render(spawnGroup_Template, mainArgs)
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
            with open(SpawnGroupTemplate2, 'r') as secondary_Template:
                secondaryOutput = chevron.render(secondary_Template, secondaryArgs)
            print(secondaryOutput)
            writeStuffToFile(secondaryOutput, output1)
            tempStartNum += 1;
        writeStuffToFile('		}\n	}\n}\n}', output1)
        print('		}\n	}\n}\n}')

# Generate traversal chains
def generateTraversalChain(
    ):
    
    #isOnCeiling = input("\nIs the midpoint on the ceiling? (Y/N): ")
    isOnCeiling = 'Y'
    entityNameNumber = int(input("Set entity numbering start value: ")); # # Set number to append at end of entity name

    while True:
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

        entityNameNumber += 1

# Generate Teleporter + Emitter + Destination
def generateTeleporter(
    ):
    
    # Set number to append at end of entity name
    entityNameNumber = int(input("\nSet entity numbering start value: "));
    
    while True:
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
        emitOrientation = angle_to_mat3(yawEmit, 0, rollEmit)
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
            'mat0XStart' : roundToInterval(startOrientation[0], 0.0001),
            'mat0YStart' : roundToInterval(startOrientation[1], 0.0001),
            'mat0ZStart' : roundToInterval(startOrientation[2], 0.0001),
            'mat1XStart' : roundToInterval(startOrientation[3], 0.0001),
            'mat1YStart' : roundToInterval(startOrientation[4], 0.0001),
            'mat1ZStart' : roundToInterval(startOrientation[5], 0.0001),
            'mat2XStart' : roundToInterval(startOrientation[6], 0.0001),
            'mat2YStart' : roundToInterval(startOrientation[7], 0.0001),
            'mat2ZStart' : roundToInterval(startOrientation[8], 0.0001),
            'mat0XEmit' : roundToInterval(emitOrientation[0], 0.0001),
            'mat0YEmit' : roundToInterval(emitOrientation[1], 0.0001),
            'mat0ZEmit' : roundToInterval(emitOrientation[2], 0.0001),
            'mat1XEmit' : roundToInterval(emitOrientation[3], 0.0001),
            'mat1YEmit' : roundToInterval(emitOrientation[4], 0.0001),
            'mat1ZEmit' : roundToInterval(emitOrientation[5], 0.0001),
            'mat2XEmit' : roundToInterval(emitOrientation[6], 0.0001),
            'mat2YEmit' : roundToInterval(emitOrientation[7], 0.0001),
            'mat2ZEmit' : roundToInterval(emitOrientation[8], 0.0001),
            'mat0XDest' : roundToInterval(destOrientation[0], 0.0001),
            'mat0YDest' : roundToInterval(destOrientation[1], 0.0001),
            'mat0ZDest' : roundToInterval(destOrientation[2], 0.0001),
            'mat1XDest' : roundToInterval(destOrientation[3], 0.0001),
            'mat1YDest' : roundToInterval(destOrientation[4], 0.0001),
            'mat1ZDest' : roundToInterval(destOrientation[5], 0.0001),
            'mat2XDest' : roundToInterval(destOrientation[6], 0.0001),
            'mat2YDest' : roundToInterval(destOrientation[7], 0.0001),
            'mat2ZDest' : roundToInterval(destOrientation[8], 0.0001)
        }
        
        # Open templates and pass through args
        with open(TeleporterTemplate, 'r') as entityTemplate:
            generatedEntity1 = chevron.render(entityTemplate, args)
            print(generatedEntity1) # print generated entity 
        
        # Call function to write generated entities to file
        writeStuffToFile(generatedEntity1, output1)

        entityNameNumber += 1; # increment by 1 after every entity

# Generate shock trap
def generateShockTrap(
    ):
    
    while True:
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
        with open(ShockTrapTemplate, 'r') as entityTemplate:
            generatedEntity = chevron.render(entityTemplate, args)
            print(generatedEntity) # print generated entity
        
        # Call function to write generated entities to file
        writeStuffToFile(generatedEntity, output1)
    
# Generate Portal Emitter + Spawn Target + Timeline
def generatePortalSpawnTarget(
    ):
    
    # Set number to append at end of entity name
    entityNameNumber = int(input("\nSet entity numbering start value: "));

    while True:
        # Get coords
        coords = list(map(float, input("Portal coords: ").split()));

        hexVal = input("Portal colour in hex: #") # 9326ff
        colourFloat = hexToFloatColour(hexVal)
        
        # Leading zeros padding
        entityNameString = str(entityNameNumber).zfill(3)
        
        # Round yaw value to nearest 5°
        yawSpawn = roundToInterval(coords[3], 5)
        yawEmit = yawSpawn + 90
        rollEmit = 90
        
        emitOrientation = angle_to_mat3(yawEmit, 0, 90)
        spawnOrientation = angle_to_mat3(yawSpawn, 0, 0)

        # The spawn target's x & y coords will be adjusted by these amounts to maintain the same distance (hypotenuse) behind the portal, regardless of orientaion
        deltas = hypotReverse(yawSpawn)

        # args to pass into the templates
        args = {
            'entityNumber': entityNameString,
            'coordX': coords[0],
            'coordY': coords[1],
            'coordZ': coords[2],
            'coordXSpawn' : coords[0] - deltas[0],
            'coordYSpawn' : coords[1] - deltas[1],
            'coordZSpawn' : coords[2] - pmNormalViewHeight,
            'yawEmit' : yawEmit,
            'rollEmit' : rollEmit,
            'hexVal' : hexVal,
            'floatColourR' : colourFloat[0],
            'floatColourG' : colourFloat[1],
            'floatColourB' : colourFloat[2],
            'mat0XEmit' : roundToInterval(emitOrientation[0], 0.0001),
            'mat0YEmit' : roundToInterval(emitOrientation[1], 0.0001),
            'mat0ZEmit' : roundToInterval(emitOrientation[2], 0.0001),
            'mat1XEmit' : roundToInterval(emitOrientation[3], 0.0001),
            'mat1YEmit' : roundToInterval(emitOrientation[4], 0.0001),
            'mat1ZEmit' : roundToInterval(emitOrientation[5], 0.0001),
            'mat2XEmit' : roundToInterval(emitOrientation[6], 0.0001),
            'mat2YEmit' : roundToInterval(emitOrientation[7], 0.0001),
            'mat2ZEmit' : roundToInterval(emitOrientation[8], 0.0001),
            'yawSpawn' : yawSpawn,
            'mat0XSpawn' : roundToInterval(spawnOrientation[0], 0.0001),
            'mat0YSpawn' : roundToInterval(spawnOrientation[1], 0.0001),
            'mat0ZSpawn' : roundToInterval(spawnOrientation[2], 0.0001),
            'mat1XSpawn' : roundToInterval(spawnOrientation[3], 0.0001),
            'mat1YSpawn' : roundToInterval(spawnOrientation[4], 0.0001),
            'mat1ZSpawn' : roundToInterval(spawnOrientation[5], 0.0001),
            'mat2XSpawn' : roundToInterval(spawnOrientation[6], 0.0001),
            'mat2YSpawn' : roundToInterval(spawnOrientation[7], 0.0001),
            'mat2ZSpawn' : roundToInterval(spawnOrientation[8], 0.0001)
        }
        
        # Open templates and pass through args
        with open(PortalSpawnTargetTemplate, 'r') as entityTemplate:
            generatedEntity1 = chevron.render(entityTemplate, args)
            print(generatedEntity1) # print generated entity 
        
        # Call function to write generated entities to file
        writeStuffToFile(generatedEntity1, output1)
        
        entityNameNumber += 1; # increment by 1 after every entity

# Dictionary of pickup templates
idProp2Type = {
    1: BFGTemplate,
    2: BulletsTemplate,
    3: CellsTemplate,
    4: ShellsTemplate,
    5: Rockets_SingleTemplate
}

# Generate idProp2 pickup
def generatePickup(
    ):
    
    # Set number to append at end of entity name
    entityNameNumber = int(input("\nSet entity numbering start value: ")); 
    
    # Select the pickup type to generate
    pickupIndex = int(input("Pickup Type:\n1. BFG\n2. Bullets\n3. Plasma Cells\n4. Shells\n5. Rockets (single)\n"))

    while True:
        # Get coords
        coords = list(map(float, input("Pickup coords: ").split()));
        
        # Leading zeros padding
        entityNameString = str(entityNameNumber).zfill(3)
        
        spawnOrientation = angle_to_mat3(coords[3], 0, 0)

        # args to pass into the template
        args = {
            'entityDefNum': entityNameString,
            'coordX': coords[0],
            'coordY': coords[1],
            'coordZ': coords[2] - pmNormalViewHeight,
            'yaw' : coords[3],
            'mat0X' : roundToInterval(spawnOrientation[0], 0.0001),
            'mat0Y' : roundToInterval(spawnOrientation[1], 0.0001),
            'mat0Z' : roundToInterval(spawnOrientation[2], 0.0001),
            'mat1X' : roundToInterval(spawnOrientation[3], 0.0001),
            'mat1Y' : roundToInterval(spawnOrientation[4], 0.0001),
            'mat1Z' : roundToInterval(spawnOrientation[5], 0.0001),
            'mat2X' : roundToInterval(spawnOrientation[6], 0.0001),
            'mat2Y' : roundToInterval(spawnOrientation[7], 0.0001),
            'mat2Z' : roundToInterval(spawnOrientation[8], 0.0001)
        }
        
        # Open template and pass through args
        with open(idProp2Type[pickupIndex], 'r') as entityTemplate:
            generatedEntity1 = chevron.render(entityTemplate, args)
            print(generatedEntity1) # print generated entity 
        
        # Call function to write generated entities to file
        writeStuffToFile(generatedEntity1, output1)
        
        entityNameNumber += 1; # increment by 1 after every entity

# Write generated entities to file
def writeStuffToFile(
    inputItem,
    outputFile
    ):

    # Open output txt and write spawn targets to file
    with open(outputFile, 'a') as output_File:
        output_File.write("\n" + inputItem)

# Select entity type to generate
def selectEntityType(
    ):

    entityDictionary = {
        1 : generateMHNode,
        2 : generateSpawnTarget,
        3 : generateSpawnGroup,
        4 : generatePortalSpawnTarget,
        5 : generateTeleporter,
        6 : generateShockTrap,
        7 : generatePickup
    }
    entityDictionaryStrings = {
        1 : "MH Node",
        2 : "Spawn Target",
        3 : "Spawn Group",
        4 : "Portal + Spawn Target",
        5 : "Teleporter",
        6 : "Shock Trap",
        7 : "Pickup"
    }
    
    print("\nEntity type to generate: ")
    for i in range (1, 7):
        print(str(i) + ". " + entityDictionaryStrings[i])

    entityType = int(input())
    while True:
        if entityType > 7 or entityType < 1:
            entityType = int(input("Invalid option, try again: "))
        else:
            break
    
    entityDictionary[entityType]()

selectEntityType()
