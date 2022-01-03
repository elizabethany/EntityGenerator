# EntityGenerator
A Python script to generate entites from text templates, using coordinates and other parameters that you enter.

## General Usage
I wrote the script based on coordinates being gathered using the `where` command, and then pasting it into the console. You can also manually enter them, in the format `x y z yaw`, ex. `10.27 231.11 54.62 90`. Some entities may not need a yaw value, and only take the xyz coords.

I did include some safety measures for inputs, such as when you are asked to enter a number to select an option, and the entered number is out of range. But other cases, like entering a letter when prompted for a number, or using the arrow keys, I didn't include safeguards for, so be wary of that.

The generated entities will be named `mod_entity_type_###`, ex. `mod_spawn_target_017`. You'll have the option to set the initial numbering, and for every subsequent entity of that type generated, it will increment that value by 1.

## Entity Types to Generate
**Meathook Grapple Node**

Requires yaw value and DLC2 resources, Eternal only. The generated node will be double sided, and face the direction you are facing when you use `where`.

**Spawn Target**

Eternal version requires resources with generic_text.swf and other related files for markers. The generated spawn target will only have the bare minimum parameters needed for a teleport spawn. You can add additional parameters by editing the template. If you select the option to generate markers, they'll be written to the secondary output file. The markers will be a piece of floating text that displays the spawn target's numbering, exe. `mod_spawn_target_017` will have a marker that says `017` denoting it's physical location.

**Spawn Group**

The name of the spawn group will have spaces replaced with underscores if present, but otherwise can have any characters that are acceptable in an entity's name. When it asks for the numbering, it presumes that your spawn targets are named in the format `some_constant_name_###`. For example, if you have `mod_spawn_target_006`, `mod_spawn_target_007`, `mod_spawn_target_008` ... `mod_spawn_target_0013`, then you'd enter 6 and 13 as the first and last spawn targets, and you'll get a spawn group with `mod_spawn_target_006` all the way to `mod_spawn_target_0013`. But if your spawn targets don't use this naming format, then it won't work.

**Teleporter**

Eternal version requires a particle for a portal (decl for `particleSystem` in the template) to be present in the loaded resources. Staring coords should be grabbed when standing where you want the portal to be, but facing away from it. Destination coords should be grabbed from where to want to exit, including the direction you wanna face when exiting the portal. Note that the option for reciprocal portals is currently broken, so pick no for now.

**Shock Trap**

Requires Cultist Base resources, Eternal only. The instance ID can be any number up to 5 digits. The finalized ID will always start with 1, as IDs starting with 0 won't work sometimes. I did add an option for custom colours, but it only affects the hazard itself, and may not look good. The other colours are controlled by the logic decl, which this script doesn't touch. From the generated entities, `game_shock_trap_start_instanceID` and `game_shock_trap_stop_instanceID` need to be activated to start and stop the shock trap.

**Portal + Spawn Target**

Requires portal opening and closing particles in the loaded resources, ex. UAC Facility Atlantica or ARC Complex. This option generates the entities needed to simulate a demon spawning by entering from a portal. The coords are where the portal will open, and the yaw is the direction from which the portal faces and the demon enters from. To use these entities, you need to first activate `mod_target_timeline_portal_spawn_###`, then wait 2.25s and then activate the provided spawn target. The timeline will open, and after a delay close the portal, when activated.

**Pickup**

Currently has BFG ammo, bullets, plasma cells, shotgun shells, and single rockets as options.


## Configuration
Options for EntityGenerator to be edited in `config.ini`, which also contain descriptions of each variable

### Settings
`gameMode` : Determines what game to generate entities for. Also determines the menu options shown and the templates used. Currently only support for Eternal exists.

`clearSetting` : Whether to ask you if you want to clear the output or not, or to do it automatically without prompting.

`loopGeneration` : End the script after generating one entity, or keep looping so you can generate more.

`printToConsole` : Print or don't print the generated entity to the console.

### Output Files

`output1` : Main output. All generated entities go here unless otherwise specified.

`output2` : Secondary output. For generated entities that you'd want to be separate from the rest, for easier copying.

`output3` : Currently unused.

### Doom Eternal Templates
Template paths used for generating entities for Doom Eternal

### Doom Eternal Misc.
Miscellaneous game specific values used for generating entities.

`pm_normalViewHeight` : Coordinates taken using `where` are from camera height, the value of `pm_normalViewHeight`. This value is subtracted from some coords to ensure that the generated entity sits on the ground.

`DistanceScale` : Distance scalar for portal emitter + spawn target entity. This value is approximately the animation distance divided by 50.
