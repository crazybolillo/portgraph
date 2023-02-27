#!/usr/bin/env python3

import argparse
import os
import subprocess

from graphviz import Digraph


class Portgraph:
    def __init__(
        self,
        graph,
        port,
        localbase,
        flavor=None,
        with_pkg=False,
        verbose=False,
        recursion=-1,
        www=None,
        suffix="",
        build=True,
        run=False,
        show_if_abandoned=True,
    ):
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
        self.pkg = "ports-mgmt/pkg"
        self.build = build
        self.run = run
        self.abandoned = show_if_abandoned
        self.graph.attr(
            "node", style="filled", fillcolor="#E1E1E1", fontcolor="#737373"
        )

    @staticmethod
    def _fullname2port(name):
        """Return the name of the port."""
        # returns category/name
        # don't use len(self.localbase) since it's not correct for some paths
        return os.sep.join(name.split(os.sep)[-2:])

    @staticmethod
    def _flavorname2port(flavorname):
        """Return a name without the @flavor"""
        sup_flavor = flavorname.rfind("@")
        if sup_flavor == -1:
            sup_flavor = len(flavorname)

        return flavorname[:sup_flavor]

    def build_graph(self):
        if self.flavor:
            self.port = self.port + "@" + self.flavor

        if self.build:
            self._recurseports(
                os.path.join(self.localbase, self.port),
                self.flavor,
                ["build", "#009999"],
                self.recursion,
            )
        if self.run:
            self._recurseports(
                os.path.join(self.localbase, self.port),
                self.flavor,
                ["run", "#990000"],
                self.recursion,
            )

    def _add_node(self, ports):
        portname = self._flavorname2port(ports)

        node_url = None
        if self.url:
            node_url = self.www + self._fullname2port(portname) + self.suffix

        node_color = "black"
        node_style = "filled"
        if self.abandoned:
            proc_maintainer = subprocess.Popen(
                ["make", "-C", portname, "maintainer"], stdout=subprocess.PIPE
            )
            maintainer = proc_maintainer.stdout.readline().decode("utf-8").rstrip()
            if maintainer == "ports@FreeBSD.org":
                node_color = "red"
                node_style = "bold"

        if (self._fullname2port(ports) != self.pkg) or (
            (self._fullname2port(ports) == self.pkg) and self.with_pkg
        ):
            self.graph.node(
                self._fullname2port(ports),
                URL=node_url,
                color=node_color,
                style=node_style,
            )

    def _recurseports(self, ports, flavor, depends_args, max_recurse=-1):
        if max_recurse == 0:
            return

        if self.verbose:
            print(ports)

        portname = self._flavorname2port(ports)

        self._add_node(ports)

        proc = subprocess.Popen(
            [
                "make",
                "-C",
                portname,
                depends_args[0] + "-depends-list",
                "-DDEPENDS_SHOW_FLAVOR",
            ]
            + (["FLAVOR=" + flavor] if flavor else []),
            stdout=subprocess.PIPE,
        )
        while True:
            line = proc.stdout.readline().decode("utf-8")
            if line != "":
                dep_port = line.rstrip()
                self.all_ports.append(ports)
                portname = self._fullname2port(ports)
                depportname = self._fullname2port(dep_port)

                if (depportname != self.pkg) or (
                    (depportname == self.pkg) and self.with_pkg
                ):
                    self.graph.edge(portname, depportname, color=depends_args[1])
                if dep_port not in self.all_ports:
                    self._add_node(dep_port)
                    self.all_ports.append(dep_port)
                    self._recurseports(dep_port, flavor, depends_args, max_recurse - 1)
            else:
                break


def graph4allports(
    localbase,
    flavor,
    with_pkg,
    verbose,
    recursion,
    url,
    suffix,
    build,
    run,
    abandoned,
    clean=True,
):
    for cat in [
        rec
        for rec in os.scandir(localbase)
        if rec.is_dir()
        # Maybe use $LOCALBASE$ SUBDIR instead?
        and rec.name
        not in ["Mk", "distfiles", "Tools", "Templates", "Keywords", "base"]
    ]:
        for port in [
            rec for rec in os.scandir(os.path.join(localbase, cat)) if rec.is_dir()
        ]:
            graph4port(
                os.path.join(cat.name, port.name),
                localbase,
                flavor,
                with_pkg,
                verbose,
                recursion,
                url,
                suffix,
                build,
                run,
                abandoned,
                clean,
            )


def graph4port(
    port,
    localbase,
    flavor,
    with_pkg,
    verbose,
    recursion,
    url,
    suffix,
    build,
    run,
    abandoned,
    clean=True,
):
    category = port[: port.find("/")]
    name = port[port.find("/") + 1 :]
    if flavor:
        name = name + "@" + flavor
    graph = Digraph(name, filename=name, format="svg")
    graph.graph_attr["rankdir"] = "LR"
    portgraph = Portgraph(
        graph,
        port,
        localbase,
        flavor,
        with_pkg,
        verbose,
        recursion,
        url,
        suffix,
        build,
        run,
        abandoned,
    )
    portgraph.build_graph()
    os.makedirs(category, exist_ok=True)

    graph.render(os.path.join(category, name), cleanup=clean)


def main():
    parser = argparse.ArgumentParser(
        description="portgraph produces a graph representing the dependencies needed for a given port"
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="be verbose")
    parser.add_argument(
        "-l",
        "--localbase",
        type=str,
        default="/usr/ports",
        help="Localbase where ports are located (/usr/ports by default)",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=str,
        default="ports-mgmt/portgraph",
        help="the port to produce the graph (ports-mgmt/portgraph by default).",
    )
    parser.add_argument("-f", "--flavor", type=str, help="Sets the flavor for ports")
    parser.add_argument(
        "-c", "--recursion", type=int, default=-1, help="Sets the maximum recursion."
    )
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        help="Adds a link on each node. Ex: url/ports-mgmt/portgraph",
    )
    parser.add_argument(
        "-s",
        "--url-suffix",
        dest="suffix",
        type=str,
        help="Adds a suffix to the url on each node. Ex: url/ports-mgmt/portgraph.svg",
    )
    parser.add_argument(
        "-w",
        "--with-pkg",
        dest="with_pkg",
        action="store_true",
        help="Since pkg is always required, this is disabled by default. You can enable it with this option.",
    )
    parser.add_argument(
        "-a",
        "--all",
        dest="allports",
        action="store_true",
        help="Build a graph for each port",
    )
    parser.add_argument(
        "-b",
        "--build",
        action="store_true",
        help="Build depends list. If -b or -r is not present, -b is actived by default",
    )
    parser.add_argument(
        "-r",
        "--run",
        action="store_true",
        help="Run depends list. If -b or -r is not present, -b is actived by default",
    )
    parser.add_argument(
        "-t",
        "--abandoned",
        action="store_true",
        help="Show abandoned ports with a particular style. You should Take maintainership ;)",
    )
    parser.add_argument(
        "-C",
        "--clean",
        action="store_true",
        help="Delete the source file (dot graph) after rendering",
    )

    args = parser.parse_args()

    if args.build is False and args.run is False:
        args.build = True

    if args.allports:
        graph4allports(
            args.localbase.rstrip(os.sep),
            args.flavor,
            args.with_pkg,
            args.verbose,
            args.recursion,
            args.url,
            args.suffix,
            args.build,
            args.run,
            args.abandoned,
            args.clean,
        )
    else:
        graph4port(
            args.port,
            args.localbase.rstrip(os.sep),
            args.flavor,
            args.with_pkg,
            args.verbose,
            args.recursion,
            args.url,
            args.suffix,
            args.build,
            args.run,
            args.abandoned,
            args.clean,
        )


if __name__ == "__main__":
    main()
