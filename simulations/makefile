EXE1=leaving_game.exe
CPP1=leaving_game_simulation.cpp 
EXE2=leaving_game_unconditional.exe
CPP2=leaving_game_simulation_unconditional.cpp 

CXX=g++
CXXFLAGS=-Wall -Wconversion -std=c++20 -O3

all : $(EXE1) $(EXE2)

$(EXE1) : $(CPP1) 
	$(CXX) $(CXXFLAGS) $(CPP1) -o $(EXE1) 

$(EXE2) : $(CPP2) 
	$(CXX) $(CXXFLAGS) $(CPP2) -o $(EXE2) 

clean :
	rm -rf $(EXE1)
	rm -rf $(EXE2)
