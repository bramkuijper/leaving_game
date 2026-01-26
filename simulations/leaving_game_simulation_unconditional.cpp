#include <iostream>

#include <ctime>
#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <string>
#include <cmath>
#include <cassert>
#include <random>

// random number generators
//
// we need something to 'seed' our random
// number generators (i.e., which sequence 
// of random numbers will we pick)
std::random_device rd; 
unsigned seed = rd();

// the actual random number generator
std::mt19937 rng_r(seed);

// allocate a uniform [0,1] random number distribution
std::uniform_real_distribution <double> uniform{0.0,1.0};

std::normal_distribution normal{0.0,1.0};

unsigned max_pop{5000};
unsigned n_per_deme{50};
unsigned n_groups{100};
unsigned output_interval{10};

unsigned max_generations{50000};

std::string file_name{"sim"};

double v_stay{0.0};
double v_group{0.0};
double v_alone{0.0};
double l_init{0.0};

double mu_l{0.02};
double sdmu{0.05};

// stats
double mean_stay[2]{0.0,0.0};
std::vector <double> fitnesses{};

struct Individual {
    double l{0.0};
    bool departed[2]{false,false};
    double w{0.0};
};

struct Group {
    std::vector <Individual> members{};
    std::vector <Individual> juveniles{};
};

std::vector <Group> population{};

// initialize the population parameters
void init_population(int argc, char **argv)
{
    v_stay = std::stod(argv[1]);
    v_group = std::stod(argv[2]);
    v_alone = std::stod(argv[3]);
    l_init  = std::stod(argv[4]);
    n_per_deme = static_cast<unsigned>(std::stoi(argv[5]));

    n_groups = max_pop / n_per_deme;
    file_name = argv[6];

    Individual standard_individual;
    standard_individual.l = l_init;

    Group standard_group;
    
    for (unsigned group_idx{0}; group_idx < n_per_deme; ++group_idx)
    {
        standard_group.members.push_back(standard_individual);
    }

    for (unsigned group_idx{0}; group_idx < n_groups; ++group_idx)
    {
        population.push_back(standard_group);
    }

} // end init_population()

void write_data(std::ofstream &data_file, unsigned const generation)
{
    double meanl{0.0};
    double ssl{0.0};

    double l;
    
    for (unsigned group_idx{0}; group_idx < n_groups; ++group_idx)
    {
        for (unsigned member_idx{0}; member_idx < n_per_deme; ++member_idx)
        {
            l = population[group_idx].members[member_idx].l;

            meanl += l;
            ssl += l*l;
        }
    } // unsigned group_idx

    unsigned n{n_groups * n_per_deme};

    meanl /= n;

    double varl{ssl / n - meanl * meanl};

    data_file << generation 
        << ";" << meanl 
        << ";" << varl 
        << ";" << mean_stay[0]
        << ";" << mean_stay[1]
        << ";" << std::endl;
} // end write_data

void write_parameters(std::ofstream &data_file)
{
    data_file << std::endl << std::endl
        << "seed;" << seed << std::endl
        << "v_stay;" << v_stay << std::endl
        << "v_alone;" << v_stay << std::endl
        << "l_init;" << l_init << std::endl
        << "n_per_deme;" << n_per_deme << std::endl
        << "mu;" << mu_l << std::endl
        << "sdmu;" << sdmu << std::endl;
}

void depart_vs_stay()
{
    // reset all fitnesses
    fitnesses.clear();

    unsigned n_stay[2]{0,0};
    unsigned n_departed[2]{0,0};

    for (unsigned group_idx{0}; group_idx < n_groups; ++group_idx)
    {
        // reset counters of the number of
        // individuals staying / departing each time step
        n_stay[0] = 0;
        n_stay[1] = 0;
        n_departed[0] = 0;
        n_departed[1] = 0;

        assert(population[group_idx].members.size() == n_per_deme);

        for (unsigned member_idx{0}; member_idx < n_per_deme; ++member_idx)
        {
            population[group_idx].members[member_idx].departed[0] = false;
            population[group_idx].members[member_idx].departed[1] = false;

            // individual leaves during t1
            if (uniform(rng_r) < 
                    population[group_idx].members[member_idx].l)
            {
                population[group_idx].members[member_idx].departed[0] = true;
                ++n_departed[0];
            }
            else // individual stays during t1
            {
                population[group_idx].members[member_idx].departed[0] = false;
                ++n_stay[0];

                // individual stays during t = 0
                // will it also stay during t = 1?
                if (uniform(rng_r) < 
                        population[group_idx].members[member_idx].l)
                {
                    population[group_idx].members[member_idx].departed[1] = true;
                    ++n_departed[1];
                }
                else // individual stays during t = 1
                {
                    population[group_idx].members[member_idx].departed[1] = false;
                    ++n_stay[1];
                }
            }
        }

        // does it all add up
        assert(n_stay[0] + n_departed[0] == n_per_deme);
        assert(n_stay[1] + n_departed[1] == n_stay[0]);

        // stats
        mean_stay[0] += n_stay[0];
        mean_stay[1] += n_stay[1];

        // now assign fitness to each member
        for (unsigned member_idx{0}; 
                member_idx < n_per_deme; ++member_idx)
        {
            // individual left during time step 1
            if (population[group_idx].members[member_idx].departed[0])
            {
                population[group_idx].members[member_idx].w = n_departed[0] > 1 ?
                    v_group : v_alone;
            }
            else if (population[group_idx].members[member_idx].departed[1])
            {
                population[group_idx].members[member_idx].w = n_departed[1] > 1 ?
                    v_group : v_alone;
            }
            else
            {
                population[group_idx].members[member_idx].w = v_stay;
            }

            fitnesses.push_back(population[group_idx].members[member_idx].w);

        } // end for member_idx
    } // end for group_idx
    
    mean_stay[0] /= n_groups;
    mean_stay[1] /= n_groups;
} // end depart_vs_stay

void mutate(double &val)
{
    if (uniform(rng_r) < mu_l)
    {
        val += sdmu * normal(rng_r);
    }

    if (val > 1.0)
    {
        val = 1.0;
    } else if (val < 0.0)
    {
        val = 0.0;
    }
}

void create_kid(Individual const &mom, Individual &kid)
{
    kid.w = 0;
    kid.departed[0] = false;
    kid.departed[1] = false;

    kid.l = mom.l;
    mutate(kid.l);
}

// reproduce where we assume hard selection
// e.g., fitnesses of all individuals across all groups
// are all put in a single sampling distribution
// and parents are then sampled from there
void reproduce()
{
    // initialize a fitness sampler
    std::discrete_distribution <unsigned> fitness_sampler(
            fitnesses.begin(),
            fitnesses.end()
            );

    unsigned sampled_parent_overall_id;
    unsigned sampled_parent_group_id;
    unsigned sampled_parent_id_within_group;

    for (unsigned group_idx{0}; group_idx < n_groups; ++group_idx)
    {
        // clear any juveniles from the previous generation
        population[group_idx].juveniles.clear();

        for (unsigned member_idx{0}; member_idx < n_per_deme; ++member_idx)
        {
            sampled_parent_overall_id = fitness_sampler(rng_r);

            sampled_parent_group_id = static_cast<unsigned>(
                    floor(static_cast<double>(sampled_parent_overall_id) / n_per_deme)
                    );

            sampled_parent_id_within_group = sampled_parent_overall_id % n_per_deme;

            assert(fitnesses[sampled_parent_overall_id] ==
                    population[sampled_parent_group_id].members[sampled_parent_id_within_group].w);

            Individual Kid;

            create_kid(
                    population[sampled_parent_group_id].
                        members[sampled_parent_id_within_group],
                        Kid);

            population[group_idx].juveniles.push_back(Kid);

        }
            
        assert(population[group_idx].juveniles.size() == n_per_deme);
    }


    
    for (unsigned group_idx{0}; group_idx < n_groups; ++group_idx)
    {
        population[group_idx].members.clear();
        population[group_idx].members = population[group_idx].juveniles;
    }

} // end reproduce()


int main(int argc, char **argv)
{
    init_population(argc, argv);

    std::ofstream output_file(file_name.c_str());
  
    // write header to data file
    output_file << "generation;meanl;varl;mean_stay1;mean_stay2;" << std::endl;
    
    for (unsigned generation{0}; generation < max_generations; ++generation)
    {
        depart_vs_stay();

        reproduce();

        if (generation % output_interval == 0)
        {
            write_data(output_file, generation);
        }

    } // end for generation

    write_parameters(output_file);
} // main()
