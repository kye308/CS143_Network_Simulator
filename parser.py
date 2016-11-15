# The parser initializes a network given a series of
# hosts, routers, links and flows

# Assumes input is in this format

'''

n_l = number of links

For each link:
link_id
link_rate
link_delay
link_buffer_size

n_h = number of hosts

For each host:
network_address
connecting_link
host_id

n_r = number of routers

For each router:
network_address
number of connected links
link_1 ... link_n
router_id

n_f = number of flows

For each flow:
flow_id
flow_src
flow_dest
data_amt
flow_start_time

'''

# Constructs object in order

# Links, Routers/Hosts, Packets (importance is links first, really)
# and maps each object's id to the object in a map for each type of object
# by using a class-level global variable
# See here: 
# https://www.toptal.com/python/python-class-attributes-an-overly-thorough-guide

import link as link_class
import host as host_class
import router as router_class
import flow as flow_class

TEST_CASE = '1'
INFILE = './input/test_case_' + TEST_CASE


def next_line(f, cast='s'):
    '''
    Reads a line in the file and strips it of white spaces and the newline
    character. An optional letter argument will cast it to a float or int.
    '''
    if cast == 'f':
        return float(f.readline().strip())
    elif cast == 'i':
        return int(f.readline().strip())

    return f.readline().strip()

def parse_hosts(f, l_map):
    '''
    Parses the input relevant to hosts from the test case input. Since the links
    have already been initialized at this point, the map of link_id to link 
    object is passed in as well. We use the map to set the link that each host
    is connected to, as well as set the entities on each "end" of a link.
    '''
    hosts = []
    h_map = {}

    num_hosts = next_line(f, 'i')
    # print num_hosts

    # print "HOSTS\n"

    for i in xrange(num_hosts):
        addr = next_line(f)
        # print addr

        link_id = next_line(f)
        # print link_id

        # Get the link object with that ID from the map
        host_link = l_map[link_id]
        # print host_link

        host_id = next_line(f)
        # print host_id

        h = host_class.Host(host_id, host_link)
        h_map[host_id] = h
        hosts.append(h)

        # Add the host as an 'end' to the link
        host_link.add_end(h)

        # print

    host_class.Host.h_map = h_map

    return (hosts, h_map)

def parse_routers(f, l_map):
    '''
    Parses the input relevant to hosts from the test case input. Since the links
    have already been initialized at this point, the map of link_id to link 
    object is passed in as well. We use the map to set the link that each host
    is connected to, as well as set the entities on each "end" of a link.
    '''

    routers = []
    r_map = {}
    r_links = []

    num_routers = int(next_line(f))
    # print num_routers

    # if num_routers > 0:
    #     print "ROUTERS\n"

    for i in xrange(num_routers):
        addr = next_line(f)
        # print addr

        num_links = int(next_line(f))
        # print "Num links: %d" % num_links

        for j in xrange(num_links):
            link_id = next_line(f)
            # print link_id
            r_links.append(link_id)


        router_id = next_line(f)
        # print router_id

        r = router_class.Router(router_id, r_links)
        r_map[router_id] = r
        routers.append(r)

        for l_id in r_links:
            mapped_link = l_map[l_id]
            mapped_link.add_end(r)

        # Reset r_links after each iteration
        r_links = []

        # print

    router_class.Router.r_map = r_map

    return (routers, r_map)

def parse_links(f):
    links = []
    l_map = {}

    num_links = int(next_line(f))
    # print num_links

    # print "LINKS\n"

    for i in xrange(num_links):
        link_id = next_line(f)
        # print link_id

        link_rate = next_line(f, 'f')
        # print link_rate

        link_delay = next_line(f, 'f')
        # print link_delay

        # Passing buffer size into constructor as number of bytes
        link_buffer_size = next_line(f, 'f') * 1e3
        # print link_buffer_size

        l = link_class.Link(link_id, link_rate, link_delay, link_buffer_size)
        l_map[link_id] = l
        links.append(l)

        # print

    link_class.Link.l_map = l_map

    return (links, l_map)

def parse_flows(f, h_map):
    flows = []
    f_map = {}

    num_flows = int(next_line(f))
    # print num_flows

    # print "FLOWS\n"

    for i in xrange(num_flows):
        flow_id  = next_line(f)
        # print flow_id, type(flow_id)

        # This is an id
        flow_src = next_line(f)
        # print flow_src

        src_host = h_map[flow_src]
        # print src_host

        flow_dest = next_line(f)
        # print flow_dest

        dest_host = h_map[flow_dest]
        # print dest_host

        data_amount = next_line(f, 'i')
        # print data_amount

        flow_start_time = next_line(f, 'f')
        # print flow_start_time

        f = flow_class.Flow(flow_id, src_host, dest_host, 
                            data_amount, flow_start_time)
        f_map[flow_id] = f
        flows.append(f)

        # print

    flow_class.Flow.f_map = f_map

    return (flows, f_map)

def parse(file_name):
    f = open(file_name, 'r')

    links, l_map = parse_links(f)
    hosts, h_map = parse_hosts(f, l_map)
    routers, r_map = parse_routers(f, l_map)
    flows, f_map = parse_flows(f, h_map)

    # hosts[0].maps = h_map

    f.close()

    # print links, l_map, len(links)
    # print
    # print hosts, h_map, len(hosts)
    # print
    # print routers, r_map, len(routers)
    # print
    # print flows, f_map, len(flows)

    return (hosts, links, routers, flows)

    # for i in xrange(len(hosts)):
    #     print hosts[i].h_map

    # print

    # for i in xrange(len(links)):
    #     print links[i].l_map

    # print

    # for i in xrange(len(routers)):
    #     print routers[i].r_map

    # print

    # for i in xrange(len(flows)):
    #     print flows[i].f_map

if __name__ == '__main__':
    parse(INFILE)

