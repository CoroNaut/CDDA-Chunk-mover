# CDDA Chunk mover
import os
import json
import math

def main():
    print("\nWelcome to CDDA Chunk mover")
    menu_options = {
        1: "Change save location",
        2: "Change map 1",
        3: "Change map 2",
        4: "Change coordinates 1",
        5: "Change coordinates 2",
        6: "Apply overmap tile copy/paste",
        7: "Apply player copy/paste"
    }
    menu_funcs = {
        1: menu_save_location,
        2: menu_change_map,
        3: menu_change_map,
        4: menu_change_coordinates,
        5: menu_change_coordinates,
        6: menu_apply_tile_copy,
        7: menu_apply_player_copy
    }
    menu_data = {
        1: None,
        2: None,
        3: None,
        4: None,
        5: None,
        6: None,
        7: None
    }

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("\nMain Menu:")
        for i, option in enumerate(menu_options.values(), 1):
            if i == 1:
                print(f"{i}. {option}: {f"Found {len(menu_data[i])} valid worlds" if menu_data[i] else ""}")
            elif (i == 2 or i == 3) and menu_data[1]:
                print(f"{i}. {option}: {str(os.path.basename(menu_data[i])) if menu_data[i] else ""}")
            elif (i == 4 or i == 5) and menu_data[1]:
                print(f"{i}. {option}: {menu_data[i] if menu_data[i] else ""}")
            elif i == 6 and menu_data[2] and menu_data[3] and menu_data[4] and menu_data[5] and (menu_data[4] != menu_data[5]):
                print(f"{i}. {option} {(": "+menu_data[i]) if menu_data[i] else ""}")
            elif i == 7 and menu_data[2] and menu_data[3] and (menu_data[2] != menu_data[3]):
                print(f"{i}. {option} {(": "+menu_data[i]) if menu_data[i] else ""}")

        choice = input("Enter your choice: ")

        if choice.isdigit() and 1 <= int(choice) <= len(menu_data):
            choice = int(choice)
            if choice == 1:
                menu_data[choice] = menu_funcs[choice]()
            elif (choice == 2 or choice == 3) and menu_data[1]:
                menu_data[choice] = menu_funcs[choice](menu_data[1])
                menu_data[6] = None
                menu_data[7] = None
            elif (choice == 4 or choice == 5) and menu_data[1]:
                print(f"{i}. {option}: {menu_data[i] if menu_data[i] else ""}")
            elif choice == 6 and menu_data[2] and menu_data[3] and menu_data[4] and menu_data[5] and (menu_data[4] != menu_data[5]):
                if not menu_data[choice]:
                    menu_data[choice] = menu_funcs[choice](menu_data)
            elif choice == 7 and menu_data[2] and menu_data[3] and (menu_data[2] != menu_data[3]):
                if not menu_data[choice]:
                    menu_data[choice] = menu_funcs[choice](menu_data)


def menu_save_location():
    savedir = None
    save_dir_list = []
    save_sav_list = []

    while savedir == None:
        savedir = input("Enter full path to CDDA save directory: ")

        save_dir_list = getDirs(savedir)
        if not save_dir_list or len(save_dir_list) == 0:
            continue

        # get list of .sav files and store into save_sav_list
        for dir in save_dir_list:
            sav_file = getSave(dir)

            if not sav_file:
                save_dir_list.remove(dir)
            else:
                save_sav_list.append(os.path.basename(dir))

        # Check if we have atleast 1 save file
        if len(save_sav_list) < 1:
            print("No saves found in save folder")
            savedir = None
            save_dir_list = []
            save_sav_list = []
            continue
        else:
            return save_dir_list
    return None

def menu_change_map(save_dir_list):
    selected = False
    print("\nSelect world directory: ")

    # Print index and world name for user to select
    for index, dir in enumerate(save_dir_list):
        print("{}. World: {}".format(index+1, os.path.basename(dir)))

    # Allow user to select their world to copy from
    choice = input("Enter your choice: ")

    if choice.isdigit() and 1 <= int(choice) <= len(save_dir_list):
        return save_dir_list[int(choice)-1]

    return None

def menu_change_coordinates():
    print("Please enter a coordinates and include ',''s")
    print('Enter coordinates in the form: "LEVEL, XCOORD1, XCOORD2, YCOORD1, YCOORD2"')
    print('Example: "0,1,150,-1,25"')
    while True:
        selection = input("Enter coords: ")

        selection = selection.split(",")

        retry = False
        for i in range(5):
            if not check_number(selection[i]):
                print("Value {} not an integer".format(i))
                retry = True
                break
            selection[i] = int(selection[i])

            if i == 2 or i == 4:
                if selection[i] < 0 or selection[i] >= 180:
                    print("Value {} not in bound [0,179]".format(i))
                    retry = True
                    break

            if i == 0:
                if selection[0] < -10 or selection[0] > 10:
                    print("Value {} not in bound [-10,10]".format(i))
                    retry = True
                    break

        if retry:
            continue
        return selection

def menu_apply_player_copy(menu_data):
    from_sav_file = getSave(menu_data[2])
    to_sav_file = getSave(menu_data[3])

    try:
        from_data = readFileJson(from_sav_file, True)
        if not from_data:
            raise Exception("Error reading from 1st save file")

        to_data = readFileJson(to_sav_file, True)
        if not to_data:
            raise Exception("Error reading from 2nd save file")
        # copy everything about the player except these values:
        # make sure these values are copied to ensure consistency when player is copied over
        # All values except these are copied to the new world in the player .sav file
        data = [
            "turn",
            "calendar_start",
            "game_start",
            "initial_season",
            "levx",
            "levy",
            "levz",
            "om_x",
            "om_y",
            "grscent",
            "inactive_global_effect_on_condition_vector",
            "global_vals",
        ]
        for i in range(len(data)):
            from_data[data[i]] = to_data[data[i]]
        playerData = [
            "location",
            "moves",
            "grab_point",
            "grab_type",
            "translocators",
            "active_mission",
            "active_missions",
            "completed_missions",
            "failed_missions",
        ]
        for i in range(len(playerData)):
            from_data["player"][playerData[i]] = to_data["player"][playerData[i]]

        from_diary_file = getDiaryFile(menu_data[2], from_sav_file)
        if not from_diary_file:
            return "Diary file not found"
        from_diary_data = readFileJson(from_diary_file, False)
        if not from_diary_data:
            return "Diary data couldn't load"
        to_diary_file = getDiaryFile(menu_data[3], to_sav_file)
        if not to_diary_file:
            return "Diary file map 2 not found"
        
        writeFile(to_diary_file, from_diary_data)
        writeFile(to_sav_file, from_data)
        return "Applied successfully"
    except Exception as e:
        if hasattr(e, "message"):
            return e.message
        else:
            return str(e)

    return "Error"

def menu_apply_tile_copy(menu_data):
    from_map_file = getMapFileFromCoordinate(menu_data[2], menu_data[4])
    to_map_file = getMapFileFromCoordinate(menu_data[3], menu_data[5])

    try:
        from_data = readFileJson(from_map_file, False)
        if not from_data:
            raise Exception("Error reading from 1st save file")

        to_data = readFileJson(to_map_file, False)
        if not to_data:
            raise Exception("Error reading from 2nd save file")

        for i in range(4):
            from_data[i]["coordinates"] = to_data[i]["coordinates"]
            from_data[i]["turn_last_touched"] = to_data[i]["turn_last_touched"]
            from_data[i]["temperature"] = to_data[i]["temperature"]

        writeFile(to_map_file, from_data)
    except Exception as e:
        if hasattr(e, "message"):
            return e.message
        else:
            return str(e)

    return "Applied successfully"

def getDiaryFile(save_path, save_file):
    files = [f for f in os.listdir(save_path) if os.path.isfile(os.path.join(save_path, f))]
    files = [f for f in files if os.path.splitext(f)[1] == ".json"]
    for file in files:
        peek_data = peekFileAtPos(os.path.join(save_path,file),2)
        if peek_data and "\"owner\": \"" in peek_data:
            return os.path.join(save_path,file)
    return None

def peekFileAtPos(file, line_number):
    try:
        with open(file, "r", encoding="utf8") as file:
            file.seek(line_number)
            return file.readline()

    except FileNotFoundError:
        # print(f"File '{file}' not found.")
        return None
    except IOError:
        # print(f"Error reading file '{file}'.")
        return None
    return None

# get directories in the save folder
def getDirs(save_path):
    if(not os.path.exists(save_path)):
        return None
    save_dirs = []
    for folder in os.listdir(save_path):
        d = os.path.join(save_path, folder)
        if os.path.isdir(d):
            save_dirs.append(d)

    # Check if there are even any save files here
    if len(save_dirs) == 0:
        return []
    return save_dirs


# check if we have the save file for this directory0
def getSave(save_directory):
    for file in os.listdir(save_directory):
        f = os.path.join(save_directory, file)

        if os.path.isfile(f) and f.endswith(".sav"):
            return f
    return None

def getNumberSelection(save_dir_List, max):
    while True:
        selection = input(str)
        if not selection.isdigit():
            print("Must be positive number in range")
            selection = None
            continue

        selection = int(selection)
        if 0 < selection < max:
            return selection
        
        print("Number not in bounds")

def check_number(num):
    while True:
        try:
            num = int(num)
            return True
        except ValueError:
            return False


def readFileJson(mapFile, nextLine):
    try:
        with open(mapFile, "r", encoding="utf8") as file:
            if nextLine:
                next(file)
            data = json.load(file)
            return data

    except FileNotFoundError:
        # print("Map file not found...")
        return None

    except json.JSONDecodeError:
        # print("JSON didn't decode correctly")
        return None

    except Exception as e:
        if hasattr(e, "message"):
            return None
        else:
            return None

    return None


def writeFile(mapFile, data):
    try:
        with open(mapFile, "w") as file:
            json.dump(data, file)
            return True

    except Exception:
        print("Generic exception")
        return None

    return None


def getMapFileFromCoordinate(dir, coordinate):
    mapsFolder = os.path.join(dir, "maps")
    map32Folder = convertCoordTo32(coordinate)

    coordinateFolderStr = (
        str(map32Folder[0]) + "." + str(map32Folder[1]) + "." + str(map32Folder[2])
    )
    coordinateFolder = os.path.join(mapsFolder, coordinateFolderStr)

    mapFileCoord = convertCoordToThree(coordinate)
    mapFileStr = (
        str(mapFileCoord[0]) + "." + str(mapFileCoord[1]) + "." + str(mapFileCoord[2])
    ) + ".map"
    mapFile = os.path.join(coordinateFolder, (mapFileStr))

    return mapFile


def convertCoordToThree(coordinate):
    xcoordTotal = 0
    if coordinate[1] >= 0:
        xcoordTotal = (coordinate[1] * 180) + coordinate[2]
    else:
        xcoordTotal = ((coordinate[1] + 1) * 180) - (180 - coordinate[2])

    ycoordTotal = 0
    if coordinate[3] >= 0:
        ycoordTotal = (coordinate[3] * 180) + coordinate[4]
    else:
        ycoordTotal = ((coordinate[3] + 1) * 180) - (180 - coordinate[4])

    return [xcoordTotal, ycoordTotal, coordinate[0]]


def convertCoordTo32(coordinate):
    threeCoord = convertCoordToThree(coordinate)

    if threeCoord[0] >= 0:
        threeCoord[0] = math.floor(threeCoord[0] / 32)
    else:
        threeCoord[0] = (-math.floor(abs(threeCoord[0]) / 32)) - 1

    if threeCoord[1] >= 0:
        threeCoord[1] = math.floor(threeCoord[1] / 32)
    else:
        threeCoord[1] = (-math.floor(abs(threeCoord[1]) / 32)) - 1

    return [threeCoord[0], threeCoord[1], threeCoord[2]]


if __name__ == "__main__":
    main()


# each OM tile is 24x24 (0-23)
# negative is (-24, -1)

# each OM chunk is 180x180 (0-179)
# the coordinates in .map file are individual tiles/12 (4 submaps per OM tile)

# player location from .sav file is individual tiles from origin (0,0)
