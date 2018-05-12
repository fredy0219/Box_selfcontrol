from neat.six_util import iteritems, itervalues
import json
import io

def species_to_json( species ):

    print("-----json-----\n");
    j_species = []
    for sk , spec in iteritems(species.species): # index

        print("Species :{0}-----".format(sk))
        j_members = []
        for g in itervalues(spec.members): # key , node , connection

            j_genome = {} 

            # print("-----node-----")
            j_nodes = []
            for nk, ng in iteritems(g.nodes): # key , bias
                j_node = {}
                j_node["key"] = nk
                j_node["bias"] = ng.bias
                j_nodes.append(j_node)
                # print("{0},{1}".format(nk,ng.bias))
            
            # print("-----connection-----")
            j_connections = []
            for ck , cg in iteritems(g.connections):
                j_connection = {}
                j_connection["key"] = ck
                j_connection["weight"] = cg.weight
                j_connections.append(j_connection)
                # print("{0},{1}".format(ck,cg.weight))

            j_genome["key"] = g.key
            j_genome["nodes"] = j_nodes
            j_genome["connections"] = j_connections

            j_members.append(j_genome)

        j_species.append(j_members)

    encode = json.dumps(j_species)

    with io.open('neat_visualization/data/data.json','w',encoding='utf8') as outfile:
        str_ = json.dumps(j_species, sort_keys = True, ensure_ascii=False)
        outfile.write(unicode(str_))
