# LEWAS Package

This python package supplied modules used by the [LEWAS](http://www.lewas.centers.vt.edu/) lab

## Installation

    $ python setup.py install

## Test

    $ cd tests/
    $ python weather_station.py

# Conceptual Prerequisites

To understand the following you should have a good working knowledge
of the Python language, object oriented design philosophy,
functional design philosophy, and regular expressions.

# Conceptual model

The class model mirrors the conceptual model, so it's important to
understand the latter when working with the former. In particular, it
is important to keep two aligned: if your conceptual model of how
sensors operate and interface changes you should probably take another
look at your class model and make any changes there too.

## Components

We consider four conceptual objects: instruments, sensors, parsers,
data models.

## Instrument

An instrument is a device which interfaces with a computer via some
communication protocol. An instrument will generally contain one or
more sensors.

## Sensor

A sensor is a device that makes observations of some environmental
parameter. These observations are reified as
[measurements][measurement].

## Measurement

A measurement contains all observed information made by a sensor. This
includes the name of the property being measured, the measurement
units, the value itself, and in some cases other information such as
estimates of signal noise levels.

## Parser

The parser is a process that transforms data from an instrument into a
[measurement](#measurement) object.

# Implementation

TODO... with links to the API docs, coming at some point in the future.
