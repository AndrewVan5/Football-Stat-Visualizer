import pygame
import requests
import math
import json

API_KEY = None

"""
Stores visualization settings and rendering state for the visual display. This includes dimensions, colours, padding, scaling info, etc.
"""
class DrawInformation:
    BLACK = 0, 0, 0
    WHITE = 255, 255, 255
    GREEN = 0, 255, 0
    RED = 255, 0, 0
    BACKGROUND_COLOUR = WHITE

    # Different bar colours improves readability 
    GRADIENTS = [(128, 128, 128), (160, 160, 160), (192, 192, 192)]

    # So bars dont touch window edges
    SIDE_PAD = 100
    TOP_PAD = 150
    BOTTOM_PAD = 150

    """
    Initializes visualization window and font.
    
    Args:
        width (int): Width of pygame window
        height (int): Height of pygame window
        lst (list[tuple[str, int]]): Initial dataset
    """
    def __init__(self, width, height, lst):
        self.width = width
        self.height = height

        # Creates Pygame window
        self.window = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Sorting Algorithm Visualization")
        self.set_list(lst)

        # Fonts to be used further down
        self.FONT = pygame.font.SysFont('comicsans', 20)
        self.LARGE_FONT = pygame.font.SysFont('comicsans', 30)
        
    """
    Updates the dataset and recalculates scaling.
    
    Args:
        lst (list[tuple[str, int]]): Updated dataset
    """  
    def set_list(self, lst):
        self.lst = lst
        
        # Normalizes bar heights
        self.min_val = min(val[1] for val in lst)
        self.max_val = max(val[1] for val in lst)

        # Scales bar width depending on dataset size
        self.block_width = round((self.width - self.SIDE_PAD) / len(lst))
        
        # Scales bar height to fit between top and bottom
        self.block_height = math.floor(
        (self.height - self.TOP_PAD - self.BOTTOM_PAD) / max(1, (self.max_val - self.min_val or 1)))

        # Centres bars horizontally
        self.start_x = self.SIDE_PAD // 2
        
        
"""
Searches API-Football for teams matching user entered name.

Args:
    team_name (str): Team name to search for
    
Returns:
    List of matching teams from the API
"""
def search_team(team_name):
    
    url = f"https://v3.football.api-sports.io/teams?search={team_name}"
    headers = {
        "x-apisports-key": API_KEY
    }

    response = requests.get(url, headers=headers)

    # Checks if API is valid
    if response.status_code != 200:
        print(f"API Error: {response.status_code}")
        return []

    data = response.json()
    teams = data.get("response", [])

    if not teams:
        return []

    return teams


"""
Finds player goal totals for a given team and season. Searches through API results and adds goals from all competitions.

Args:
    team_id (int): Team's ID from API-Football
    season_year (int): Season year to get data from
    
Returns:
    list[tuple[str, int]]: Top 20 players by goal count
"""
def fetch_players_by_goals(team_id, season_year):
    page = 1
    goal_list = []
    
    # Loops through pages, until empty page is reached
    while True:
        url = f"https://v3.football.api-sports.io/players?team={team_id}&season={season_year}&page={page}"
        headers = {
            "x-apisports-key": API_KEY
        }
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"API Error: {response.status_code}")
            break

        data = response.json()
        players = data.get("response", [])
        
        if not players and page == 1:
            print("No players returned from API.")
            break
        
        elif not players:
            break            

        for player in players:
            name = player["player"]["name"]
            
            # Sums goals/appearences from all competitions
            total_goals = sum(stats["goals"]["total"] or 0 for stats in player["statistics"])
            
            # "appearences" used by API (not a typo)
            total_appearances = sum(stats["games"]["appearences"] or 0 for stats in player["statistics"])

            # Only includes players who appeared and scored
            if total_goals > 0 and total_appearances > 0:
                goal_list.append((name, total_goals))

            
        page += 1
        
    if not goal_list:
        print("No players with goals found.")
    
    # Limits size to keep visualization readable
    return goal_list[:20]


"""
Displays the UI elements and current state of the dataset.

Args:
    draw_info (DrawInformation): Current state of visualization 
    algo_name (str): Name of current sorting algorithm
    ascending (bool): Determines sort order
"""
def draw(draw_info, algo_name, ascending):
    
    # Clears entire window to before redrawing
    draw_info.window.fill(draw_info.BACKGROUND_COLOUR)
    
    # Title matches current algorithm/direction
    title = draw_info.LARGE_FONT.render(f"{algo_name} - {'Ascending' if ascending else 'Descending'}", 1, draw_info.GREEN)
    draw_info.window.blit(title, (draw_info.width/2 - title.get_width()/2 , 5))

    # Instructions redrawn each frame
    controls = draw_info.FONT.render("R - Reload Data | SPACE - Start Sorting | A - Ascending | D - Descending", 1, draw_info.BLACK)
    draw_info.window.blit(controls, (draw_info.width/2 - controls.get_width()/2 , 40))

    # Sorts algorithm selection
    sorting = draw_info.FONT.render("I - Insertion Sort | B - Bubble Sort", 1, draw_info.BLACK)
    draw_info.window.blit(sorting, (draw_info.width/2 - sorting.get_width()/2 , 70))

    draw_list(draw_info)
    
    # All draw calls updated at once
    pygame.display.update()


"""
Displays dataset as vertical bars.

Args:
    draw_info (DrawInformation): Current state of visualization
    colour_positions (dict): Highlights bars during sorting
    clear_bg (bool): Whether to clear background before drawing or not
"""
def draw_list(draw_info, colour_positions=None, clear_bg=False):
    lst = draw_info.lst
    if colour_positions is None:
        colour_positions = {}

    # Clears only bar area when animating swaps as it is only part that needs to change
    if clear_bg:
        clear_rect = (draw_info.SIDE_PAD//2, draw_info.TOP_PAD - 40,
                      draw_info.width - draw_info.SIDE_PAD, draw_info.height - draw_info.TOP_PAD)
        pygame.draw.rect(draw_info.window, draw_info.BACKGROUND_COLOUR, clear_rect)

    for i, (name, val) in enumerate(lst):
        
        # Index important for position
        x = draw_info.start_x + i * draw_info.block_width
        
        # Scaled relative to min and max values
        y = draw_info.height - draw_info.BOTTOM_PAD - (val - draw_info.min_val) * draw_info.block_height

        # Uses saved alternating colours
        colour = draw_info.GRADIENTS[i % 3]
        if i in colour_positions:
            colour = colour_positions[i]

        # Draws the bar
        pygame.draw.rect(draw_info.window, colour, (x, y, draw_info.block_width, draw_info.height - y))

        # Numeric value placed above bar
        label = draw_info.FONT.render(str(val), 1, draw_info.BLACK)
        draw_info.window.blit(label, (x + draw_info.block_width//4, y - 20))
        
        # Shortens display name to reduce overlap in large datasets
        short_name = name.split()[-1]
        if len(short_name) > 8 and len(draw_info.lst) > 12:
            short_name = name.split()[-1]
            short_name = short_name[:5] + "."
            name_label = draw_info.FONT.render(short_name, 1, draw_info.BLACK)
        elif len(short_name) > 5 and len(draw_info.lst) > 18:
            short_name = name.split()[-1]
            short_name = short_name[:4] + "."
            name_label = draw_info.FONT.render(short_name, 1, draw_info.BLACK)
            
        else:
            name_label = draw_info.FONT.render(short_name, 1, draw_info.BLACK)

        # Centres name label beneath bar
        name_x = x + (draw_info.block_width - name_label.get_width()) // 2
        name_y = draw_info.height - draw_info.BOTTOM_PAD // 2
        draw_info.window.blit(name_label, (name_x, name_y))

    # Updates diaplay immediately
    if clear_bg:
        pygame.display.update()
        
        
"""
Visually executes bubble sort on the data (by goals).

Args:
    draw_info (DrawInformation): Current state of visualization
    ascending (bool): Determines sort order
"""
def bubble_sort(draw_info, ascending=True):
    lst = draw_info.lst

    for i in range(len(lst) - 1):
        for j in range(len(lst) - 1 - i):
            num1 = lst[j][1]
            num2 = lst[j + 1][1]

            if (num1 > num2 and ascending) or (num1 < num2 and not ascending):
                lst[j], lst[j + 1] = lst[j + 1], lst[j]
                draw_list(draw_info, {j: draw_info.GREEN, j + 1: draw_info.RED}, True)
                yield True

    return lst


"""
Visually executes insertion sort on the data (by goals).

Args:
    draw_info (DrawInformation): Current state of visualization
    ascending (bool): Determines sort order
"""
def insertion_sort(draw_info, ascending=True):
    lst = draw_info.lst

    for i in range(1, len(lst)):
        current = lst[i]
        j = i
        while j > 0 and ((lst[j - 1][1] > current[1] and ascending) or (lst[j - 1][1] < current[1] and not ascending)):
            lst[j] = lst[j - 1]
            j -= 1
        lst[j] = current
        draw_list(draw_info, {j: draw_info.GREEN, i: draw_info.RED}, True)
        yield True

    return lst


"""
Loads player goal data from a local JSON file.

Args: 
    filename(str): Path to the JSON file selected by the user. 

Returns: 
    A list of tuples containing (name, goals)
"""
def load_offline_data(filename):
    with open(filename, "r") as f:
        data = json.load(f)

    return [(player["name"], player["goals"]) for player in data["players"]]


"""
Runs the program.

Handles user inputs and runs the Pygame visual display event loop.
"""
def main():
    global API_KEY
    
    while True:
        isonline = input("Do you have a valid API-Football Key? Type '1' for Yes and '2' for No: ").strip()
        if isonline in ["1", "2"]:
            break
        print("Invalid Input, Try Again.")

    # Online
    if isonline == "1":
        API_KEY = input("Enter API-Football Key here: ").strip()

        print("DISCLAIMER:\n"
              "-Use Full Team Names (E.g. 'Manchester United')\n"
              "-Use Recent Seasons, Older Seasons Limited by API (E.g. '2024')\n"
              "-Major Teams/Leagues Contain Data More Often")

        team_name = input("Enter team name to search: ").strip()
        season_year = input("Enter what year's stats you'd like to view: ").strip()
        
        results = search_team(team_name)
        if not results:
            print("No matching team found.")
            return

        team_id = results[0]["team"]["id"]
        raw_data = fetch_players_by_goals(team_id, season_year)

    # Offline
    else:  
        while True:
            choice = input(
                "Choose the Offline Data You'd Like to View.\n"
                "Type '1' for 2022 Vancouver Whitecaps.\n"
                "Type '2' for 2024 Chelsea.\n"
                "Type '3' for 2022 Manchester United.\n"
                "Enter Your Choice Here: ").strip()

            if choice == "1":
                filename = "data/whitecaps_sample_data.json"
                break
            elif choice == "2":
                filename = "data/chelsea_sample_data.json"
                break
            elif choice == "3":
                filename = "data/manunited_sample_data.json"
                break
            else:
                print("Invalid Input, Try Again.")

        raw_data = load_offline_data(filename)

    if not raw_data:
        print("No data to visualize.")
        return

    pygame.init()
    draw_info = DrawInformation(1400, 1000, raw_data)
    run = True
    clock = pygame.time.Clock()
    sorting = False
    ascending = True
    sorting_algorithm = bubble_sort
    sorting_algo_name = "Bubble Sort"
    sorting_algorithm_generator = None

    # Pygame loop
    while run:
        clock.tick(30)
        if sorting:
            try:
                next(sorting_algorithm_generator)
            except StopIteration:
                sorting = False
        else:
            draw(draw_info, sorting_algo_name, ascending)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_r:
                if isonline == "1":
                    raw_data = fetch_players_by_goals(team_id, season_year)
                else:
                    raw_data = load_offline_data(filename)
                draw_info.set_list(raw_data)
                sorting = False
            elif event.key == pygame.K_SPACE and not sorting:
                sorting = True
                sorting_algorithm_generator = sorting_algorithm(draw_info, ascending)
            elif event.key == pygame.K_a and not sorting:
                ascending = True
            elif event.key == pygame.K_d and not sorting:
                ascending = False
            elif event.key == pygame.K_i and not sorting:
                sorting_algorithm = insertion_sort
                sorting_algo_name = "Insertion Sort"
            elif event.key == pygame.K_b and not sorting:
                sorting_algorithm = bubble_sort
                sorting_algo_name = "Bubble Sort"

    pygame.quit()

if __name__ == "__main__":

    main()
