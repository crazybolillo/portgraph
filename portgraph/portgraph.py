#!/usr/bin/env python3
# -*- coding:utf8 -*-

import os
import subprocess
import argparse
import sys
from graphviz import Digraph


class portgraph:
    def __init__(self, graph, port, localbase, flavor=None,
                 with_pkg=False, verbose=False, recursion=-1, www=None, suffix="",
                 build=True, run=False, showIfAbandoned=True):
        self.graph = graph
        self.localbase = localbase
        self.flavor = flavor
        self.port = port
        self.with_pkg = with_pkg
        self.verbose = verbose
        self.recursion = recursion
        self.url = www is not None
        self.www = "" if www is None else www
        self.suffix = "" if suffix is None else suffix
        self.all_ports = []
        self.PKG = "ports-mgmt/pkg"
        self.build = build
        self.run = run
        self.abandoned = showIfAbandoned
        self.graph.attr('node', style='filled',
                        fillcolor='#E1E1E1', fontcolor='#737373')

    def __fullname2port(self, name):
        """ Return the name of the port. """
        # returns category/name
        # don't use len(self.localbase) since it's not correct for some paths
        return os.sep.join(name.split(os.sep)[-2:])

    def __flavorname2port(self, flavorname):
        """ Return a name without the @flavor """
        supFlavor = flavorname.rfind('@')
        if supFlavor == -1:
            supFlavor = len(flavorname)

        return flavorname[:supFlavor]

    def buildGraph(self):
        if self.flavor:
            self.port = self.port + '@' + self.flavor

        if self.build:
            self.__recurseports(os.path.join(self.localbase, self.port),
                                self.flavor,
                                ['build', '#009999'],
                                self.recursion)
        if self.run:
            self.__recurseports(os.path.join(self.localbase, self.port),
                                self.flavor,
                                ['run', '#990000'],
                                self.recursion)

    def __addnode(self, ports):
        portname = self.__flavorname2port(ports)

        node_url = None
        if self.url:
            node_url = self.www + self.__fullname2port(portname) + self.suffix

        node_color = 'black'
        node_style = 'filled'
        if self.abandoned:
            proc_maintainer = subprocess.Popen(['make', '-C',
                                                portname,
                                                'maintainer'],
                                                stdout=subprocess.PIPE)
            maintainer = proc_maintainer.stdout.readline().decode('utf-8').rstrip()
            if maintainer == "ports@FreeBSD.org":
                node_color = 'red'
                node_style = 'bold'

        if (self.__fullname2port(ports) != self.PKG) or \
            ((self.__fullname2port(ports) == self.PKG) and
            self.with_pkg):
            self.graph.node(self.__fullname2port(ports),
                            URL=node_url,
                            color=node_color,
                            style=node_style)


    def __recurseports(self, ports, flavor, depends_args, maxRecurse=-1):
        if maxRecurse == 0:
            return

        if self.verbose:
            print(ports)

        portname = self.__flavorname2port(ports)

        self.__addnode(ports)

        proc = subprocess.Popen(['make', '-C',
                                 portname,
                                 depends_args[0] + '-depends-list',
                                 '-DDEPENDS_SHOW_FLAVOR'] +
                                (['FLAVOR='+flavor] if flavor else []),
                                stdout=subprocess.PIPE)
        while True:
            line = proc.stdout.readline().decode('utf-8')
            if line != '':
                dep_port = line.rstrip()
                self.all_ports.append(ports)
                portname = self.__fullname2port(ports)
                depportname = self.__fullname2port(dep_port)

                if (depportname != self.PKG) or \
                   ((depportname == self.PKG) and
                   self.with_pkg):

                    self.graph.edge(portname, depportname,
                                    color=depends_args[1])
                if dep_port not in self.all_ports:
                    self.__addnode(dep_port)
                    self.all_ports.append(dep_port)
                    self.__recurseports(dep_port, flavor, depends_args,
                                        maxRecurse - 1)
            else:
                break


def graph4allports(localbase, flavor, with_pkg, verbose, recursion, url, suffix,
                   build, run, abandoned, clean=True):
    for cat in [rec for rec in os.scandir(localbase)
                if rec.is_dir()
                # Maybe use $LOCALBASE$ SUBDIR instead?
                and rec.name not in ['Mk', 'distfiles',
                                     'Tools', 'Templates',
                                     'Keywords', 'base']]:
        for port in [rec for rec in os.scandir(os.path.join(localbase, cat))
                     if rec.is_dir()]:
            graph4port(os.path.join(cat.name, port.name), localbase, flavor,
                       with_pkg, verbose, recursion, url, suffix, build, run,
                       abandoned, clean)


def graph4port(port, localbase, flavor, with_pkg, verbose, recursion, url, suffix,
               build, run, abandoned, clean=True):
        category = port[:port.find('/')]
        name = port[port.find('/')+1:]
        if flavor:
            name = name + '@' + flavor
        g = Digraph(name, filename=name, format='svg')
        g.graph_attr['rankdir'] = 'LR'
        pg = portgraph(g, port, localbase, flavor, with_pkg,
                       verbose, recursion, url, suffix, build, run, abandoned)
        pg.buildGraph()
        os.makedirs(category, exist_ok=True)

        g.render(os.path.join(category,name), cleanup=clean)


def main():
    parser = argparse.ArgumentParser(description="portgraph produces a graph representing the dependencies needed for a given port")

    parser.add_argument('-v', '--verbose', action='store_true', help="be verbose")
    parser.add_argument('-l', '--localbase', type=str, default="/usr/ports", help="Localbase where ports are located (/usr/ports by default)")
    parser.add_argument('-p', '--port', type=str, default="ports-mgmt/portgraph", help="the port to produce the graph (ports-mgmt/portgraph by default).")
    parser.add_argument('-f', '--flavor', type=str, help="Sets the flavor for ports")
    parser.add_argument('-c', '--recursion', type=int, default=-1, help="Sets the maximum recursion.")
    parser.add_argument('-u', '--url', type=str, help="Adds a link on each node. Ex: url/ports-mgmt/portgraph")
    parser.add_argument('-s', '--url-suffix', dest="suffix", type=str, help="Adds a suffix to the url on each node. Ex: url/ports-mgmt/portgraph.svg")
    parser.add_argument('-w', '--with-pkg', dest='with_pkg', action='store_true', help="Since pkg is always required, this is disabled by default. You can enable it with this option.")
    parser.add_argument('-a', '--all', dest='allports', action='store_true', help="Build a graph for each port")
    parser.add_argument('-b', '--build', action='store_true', help="Build depends list. If -b or -r is not present, -b is actived by default")
    parser.add_argument('-r', '--run', action='store_true', help="Run depends list. If -b or -r is not present, -b is actived by default")
    parser.add_argument('-t', '--abandoned', action='store_true', help="Show abandoned ports with a particular style. You should Take maintainership ;)")
    parser.add_argument('-C', '--clean', action='store_true', help="Delete the source file (dot graph) after rendering")

    args = parser.parse_args()

    if args.build is False and args.run is False:
        args.build = True

    if args.allports:
        graph4allports(args.localbase.rstrip(os.sep), args.flavor, args.with_pkg, args.verbose, args.recursion, args.url, args.suffix,
                       args.build, args.run, args.abandoned, args.clean)
    else:
        graph4port(args.port, args.localbase.rstrip(os.sep), args.flavor, args.with_pkg, args.verbose, args.recursion, args.url, args.suffix,
                       args.build, args.run, args.abandoned, args.clean)

if __name__ == "__main__":
    main()
