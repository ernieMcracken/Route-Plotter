from os import linesep

class OutOfGridError(Exception):
    pass

class Coordinate:

    """This class represents a coordinate on a 2d grid.
    
    Attributes
    ----------
    x : int
        X coordinate value.
    y : int 
        Y coordinate value.
        
    """

    def __init__(self, x, y):
        """The constructor for the Coordinate class
        Parameters
        ----------
        x : int
            X coordinate value.
        y : int 
            Y coordinate value.
        """

        self.x = x
        self.y = y

    def __add__(self, object):
        #overloading + to allow addition of Coordinates
        return Coordinate(self.x + object.x, self.y + object.y)

    def __eq__(self, object):
        return self.x == object.x and self.y == object.y

    def __str__(self):
        return f"({self.x}, {self.y})"




class RoutePlotter():

    """This class plots routes for a drone navigation system in a grid.
    
    Attributes
    ----------
    coords : list
        List of the coordinates in the route.
    Methods
    -------
    printCoords()
        Print the list of coordinates in the route.
    drawGrid()
        Return a string representation of the route.
    printGrid()
        Print a string representation of the route.
    move(direction)
        Move from current position to an adjacent grid square.
    removeCoord(index=None)
        Remove a coordinate from the route, coordinate is removed 
        based on index. Default - remove last coordinate. 
    """
    _moves = {
        "N": Coordinate(0, 1),
        "S": Coordinate(0, -1),
        "E": Coordinate(1, 0),
        "W": Coordinate(-1, 0)
    }

    def __init__(self, rows, cols, initialPos = Coordinate(1, 1)):

        """The constructor for the RoutePlotter class.
        
        Parameters
        ----------
        rows : int
            Number or rows in the route grid.
        cols : int 
            Number of columns in the route grid.
        initialPos: Coordinate, optional
            The starting grid square coordinate for the route (default is 1,1).
        
        Raises 
        ------
        ValueError
            If either rows or columns are < 1.
        OutOfGridError
            If initialPos defines a coordinate that is beyond the bounds of
            the grid. 
        """

        if (rows <= 0 or cols <=0):
            raise ValueError("rows and cols must be greater than 0")
     
        self._rows = rows
        self._cols = cols
        self._coords = []
        self._matrix = []

        #generate string used to seperate rows in grid
        self._rowSep = "---:" * (self._rows + 1) + "---" + linesep

        #validate initial position
        if self._checkPos(initialPos):
            self._coords.append(initialPos)
        else:
            raise OutOfGridError(f"Initial position {initialPos} is invalid")

    def _checkPos(self, coord):
        """Check that a coordinate falls within the bounds of the grid"""
        if (coord.x >= 1 and coord.x <= self._cols) and (coord.y >= 1 and coord.y <=self._rows):
            return True
        return False
    
    def removeCoord(self, index=None):
        """Remove a coordinate from the route
        
        Parameters
        ----------
        index int, optional
            Index of coordinate to remove, defaults to last index.
        """
        if index == None:
            self._coords.pop()
        else:
            self._coords.pop(index)

    def printCoords(self):
        """Print the route's coordinates"""
        for coord in self._coords:
            print(coord)

    def drawRoute(self):
        """Return a string representation of the route plotted in a rows x cols grid"""

        #initialize an empty matrix or rows x cols
        self._matrix = [[" " for c in range(self._cols)]
                        for r in range(self._rows)]

        #fill the matrix based on each coordinate in the route
        for coord in self._coords:
            self._matrix[coord.y - 1][coord.x - 1] = "x"

        #top row of grid
        grid =  f"{':':>4}" * (self._cols + 1) + f"{' ':^3}" + linesep
        grid += self._rowSep

        #each row in matrix flipping order of rows
        for i in range(self._rows -1 , -1, -1):
            
            grid += f"{i + 1:>3}: " + f"{':':^3}".join(self._matrix[i]) + f"{':':>2}" + linesep
            grid += self._rowSep

        #bottom of grid
        grid += f"{':':>4}" + ":".join([f"{i + 1:^3}" for i in range(self._cols)]) + ":"

        return grid 

    def printRoute(self):
        """Print the route"""
        print(self.drawRoute()) 

    def move(self, direction):
        """Move to an adjacent grid square.
        
        Parameters
        ----------
        direction : {'N', 'S', 'E', 'W'}
            The direction of the move.
        
        Raises
        ------
        OutOfGridError
            If the move results in a position beyond the bounds of the route
            grid.
        """

        #new location is relative to previous location
        prevPos = self._coords[-1]
        
        #calculate new location and check it's validity
        try:
            newPos = prevPos + self._moves[direction]
        except KeyError:
            print(f"Provided direction {direction} is invalid")
            return

        if not self._checkPos(newPos):
            raise OutOfGridError("Outside grid")

        #store the new coordinate
        self._coords.append(newPos)

    @classmethod
    def fromFile(cls, filePath: str, rows=12, cols=12):
        """Read a route from text file formatted as follows
        Line 1: X-Coordinate of start of route
        Line 2: Y-Coordinate of start of route
        Line 3 onwards: Route instructions (directions) N, S, E or W. 
    
        Parameters
        ----------
        filePath : str 
            Location of file containing the route.
        rows : int
            Number of rows in the grid.
        cols: int
            Number of cols in the grid.
        
        Returns
        -------
        RoutePlotter 
            RoutePlotter object describing the route contained in the file.
        """

        try:
            inFile = open(filePath, "r")
        except FileNotFoundError:
            print("File not found")
            return

        with inFile:
            #parse the initial coordinate
            try:
                x = int(inFile.readline().strip())
                y = int(inFile.readline().strip())
            except TypeError:
                print("Initial coordinate values could not be parsed.")
                return

            #instantiate instance of RoutePlotter
            route = cls(rows, cols, Coordinate(x, y))

            #parse each move from the file
            try:
                for line in inFile:
                    route.move(line.strip())
            except OutOfGridError:
                print("Error: The route is outside of the grid.")
                return

            return route


if __name__ == "__main__":

    while True:

        nextRoute = input("Enter the next route instructions file, or enter STOP to finish: ").strip()
    
        if nextRoute == "STOP":
            break
       
        if nextRoute:
            routePlotter = RoutePlotter.fromFile(nextRoute)
            if routePlotter:
                routePlotter.printRoute()
                routePlotter.printCoords()
