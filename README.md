# Football Player Goal Sorter and Visualizer

This program recieves data detailing the goal counts of Football (soccer) players within a team during a season and visualizes/sorts it.
The data can either be retrieved from API-Football (with a valid API key) or from the provided JSON files.

------------------------------------------------------------------------------------------------------------------------------------

## Features

- Live data retrieval from API-Football using an API Key
- Offline option using provided .json files
- Animated stat sorting using Bubble Sort or Insertion Sort
- Options to display the data in either ascending or descending order

------------------------------------------------------------------------------------------------------------------------------------

## Technologies Used

- Python
- Pygame
- REST API (API-Football)
- JSON data files

------------------------------------------------------------------------------------------------------------------------------------

## How to Use

- Open the terminal and navigate to the respective folder using "cd <folder name>"
- Once in correct folder type "python football_stat_visualizer"
- From there follow instructions in terminal, be sure to read the disclaimer

------------------------------------------------------------------------------------------------------------------------------------

## Controls

Once in the Visual Window:
    R: Reloads data back to original state
    SPACE: After setting sorting algorithm, begins sorting (Bubble Sort is default)
    A: Sets sorting order to Ascending
    D: Sets sorting order to Descending
    I: Sets sorting algorithm to Insertion Sort
    B: Sets sorting algorithm to Bubble Sort

------------------------------------------------------------------------------------------------------------------------------------

## Author

Andrew Van Ommen


------------------------------------------------------------------------------------------------------------------------------------

## Acknowledgements


This project’s visualization framework (window setup, bar rendering, event loop, and animations)
was adapted from the "Python Sorting Algorithm Visualizer" tutorial by *Tech With Tim* on YouTube: https://www.youtube.com/watch?v=twRidO-_vqQ

This project extends that foundation with:
- API-Football data integration
- Offline dataset support using local JSON files
- Custom scaling and labeling
- User defined searching
- Tuple based sorting (rather than individual values)
- Other tweaks to the visualization framework
