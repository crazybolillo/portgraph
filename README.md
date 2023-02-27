Started from an idea on twitter and used to reduce the dependencies of a port, here a python script to produce dependencies' graph of a(ll) FreeBSD ports.

# Install
## Using pip

`pip install portgraph`

## Using FreeBSD pkg

`pkg install py36-portgraph`

## Using FreeBSD ports

`make -C /usr/ports/ports-mgmt/py-portgraph`

# Usage
portgraph produces a graph representing the dependencies needed for a given port or all ports.

Options are:
```
-h or --help: Show this help
-l my_dir or --localbase my_dir: Sets my_dir as the directory where ports are located (/usr/ports by default)
-p my_port or --port my_port: Sets my_port as the port to produce the graph (ports-mgmt/py-portgraph by default).
-b or --build: build-depends-list (if -b or -r is not present, -b is actived by default).
-r or --run: run-depends-list (if -b or -r is not present, -b is actived by default).
-f my_flavor or --flavor my_flavor: Sets the flavor for the port.
-c or --recursion: Sets the maximum recursion.
-u or --url: Adds a link to freshports.
-w or --with-pkg: Since pkg is always required, this is disabled  by default. You can enable it with this option.
-a or --all: Build a graph for each port
-v or --verbose: Print the port being traversed
```

The result is a svg and a graphviz file.

# Examples

## Without arguments:

`portgraph`

[<img src="https://glcdn.githack.com/lbartoletti/portgraph/raw/master/img/py-portgraph.png" alt="without arguments"/>](https://glcdn.githack.com/lbartoletti/portgraph/raw/master/img/py-portgraph.svg)

## Using a specific local ports, like poudriere:

`portgraph -l /usr/local/poudriere/ports/default`


## Most important arguments, the port:

`portgraph -p ports-mgmt/portscout`

[<img src="https://glcdn.githack.com/lbartoletti/portgraph/raw/master/img/portscout.png" alt="portscout"/>](https://glcdn.githack.com/lbartoletti/portgraph/raw/master/img/portscout.svg)

## Sets the flavor for the port:

`portgraph -p databases/py-psycopg2 -f py36`

[<img src="https://glcdn.githack.com/lbartoletti/portgraph/raw/master/img/py-psycopg2@py36.png" alt="py36-psycopg2"/>](https://glcdn.githack.com/lbartoletti/portgraph/raw/master/img/py-psycopg2@py36.svg)

`portgraph -p databases/py-psycopg2 -f py27`

[<img src="https://glcdn.githack.com/lbartoletti/portgraph/raw/master/img/py-psycopg2@py27.png" alt="py27-psycopg2"/>](https://glcdn.githack.com/lbartoletti/portgraph/raw/master/img/py-psycopg2@py27.svg)

## You can define the depth of the dependencies to display

`portgraph -p databases/pgmodeler -c 1`

[<img src="https://glcdn.githack.com/lbartoletti/portgraph/raw/master/img/pgmodeler_rec_1.png" alt="pgmodeler with max recursion defined" width="20%" height="20%"/>](https://glcdn.githack.com/lbartoletti/portgraph/raw/master/img/pgmodeler_rec_1.svg)

## You want a link to freshports? Add the -u/--url option.

`portgraph -p databases/sfcgal -u -c 2`

[<img src="https://glcdn.githack.com/lbartoletti/portgraph/raw/master/img/sfcgal.png" alt="sfcgal with freshports url" width="20%" height="20%"/>](https://glcdn.githack.com/lbartoletti/portgraph/raw/master/img/sfcgal.svg)

## ports-mgmt/pkg is the god of all. Do you want to put it?

`portgraph -p ports-mgmt/portscout -w`

[<img src="https://glcdn.githack.com/lbartoletti/portgraph/raw/master/img/portscout_pkg.png" alt="portscout with pkg"/>](https://glcdn.githack.com/lbartoletti/portgraph/raw/master/img/portscout_pkg.svg)

## Run and build depends list

build-depends-list are blue and run-depends-list are red.

`portgraph -p lang/python36 -rb -c 2 -u`

[<img src="https://glcdn.githack.com/lbartoletti/portgraph/raw/master/img/python36.png" alt="python36 with run-depends-list, build-depends-list, url and max recursion defined "/>](https://glcdn.githack.com/lbartoletti/portgraph/raw/master/img/python36.svg)


## Build all ports (accept all arguments except -p/--ports)

For freshports with only one dependency.

`portgraph -a -c 1 -u`


It can take a long time (880s on my desktop computer and produces 245M of files).

> Note: examples were made on 2018-02-15. The results may differ depending on port updates.
