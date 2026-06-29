EXE1=leaving_game.exe
CPP1=leaving_game_simulation.cpp 
EXE2=leaving_game_unconditional.exe
CPP2=leaving_game_simulation_unconditional.cpp 
EXE2=leaving_game_a_priori.exe
CPP2=leaving_game_simulation_a_priori.cpp 

CXX=g++
CXXFLAGS=-Wall -Wconversion -std=c++20 -O3

all : $(EXE1) $(EXE2)

$(EXE1) : $(CPP1) 
	$(CXX) $(CXXFLAGS) $(CPP1) -o $(EXE1) 

$(EXE2) : $(CPP2) 
	$(CXX) $(CXXFLAGS) $(CPP2) -o $(EXE2) 

$(EXE3) : $(CPP3)
	$(CXX) $(CXXFLAGS) $(CPP3) -o $(EXE3) 

clean :
	rm -rf $(EXE1)
	rm -rf $(EXE2)
	rm -rf $(EXE3)
