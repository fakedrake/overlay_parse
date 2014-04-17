# overlay_parse

[![Build Status](https://secure.travis-ci.org/fakedrake/overlay_parse.png)](http://travis-ci.org/fakedrake/overlay_parse)
[![Stories in Ready](https://badge.waffle.io/fakedrake/overlay_parse.png?label=ready)](https://waffle.io/fakedrake/overlay_parse) [![pypi version](https://badge.fury.io/py/overlay_parse.png)](http://badge.fury.io/py/overlay_parse)
[![# of downloads](https://pypip.in/d/overlay_parse/badge.png)](https://crate.io/packages/overlay_parse?version=latest)
[![code coverage](https://coveralls.io/repos/fakedrake/overlay_parse/badge.png?branch=master)](https://coveralls.io/r/fakedrake/overlay_parse?branch=master)

## Overview

Make sense of free text with overlays.

## Usage

Install `overlay_parse`:

    pip install overlay_parse
	python setup.py install

As a small demo on how you well you can parse dates:


	>>> from overlay_parse import date
	>>> dates.just_dates("I shall come on July the 17th 1991")
	[(17, 7, 1991)]
	>>> dates.just_dates("I shall 30th of september 2006")
	[(30, 9, 2006)]
	>>> dates.just_dates("I shall 30th of september 2006, timestamp: 19071991, 18.7.1991")
	[(19, 7, 1991), (18, 7, 1991), (30, 9, 2006)]

You can also parse date ranges with

	>>> dates.just_ranges("I will be here from 30th of september 2006-2007")
	[((30, 9, 2006), (0, 0, 2007))]
	>>> dates.just_ranges("I will be here from 30th of september 2006 to 18.7.2007")
	[((30, 9, 2006), (18, 7, 2007))]
	>>> dates.just_ranges("200 BC - 300 AD")
	[((0, 0, -200), (0, 0, 300))]
	>>>

<!-- ## Documentation -->

<!-- [API Documentation](http://overlay_parse.rtfd.org) -->

## Testing

Install development requirements:

    pip install -r requirements.txt

Tests can then be run with:

    nosetests

Lint the project with:

    flake8 overlay_parse tests

## API documentation

Generate the documentation with:

    cd docs && PYTHONPATH=.. make singlehtml

To monitor changes to Python files and execute flake8 and nosetests
automatically, execute the following from the root project directory:

    stir
